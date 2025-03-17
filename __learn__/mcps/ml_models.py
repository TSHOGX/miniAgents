import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_client")


@dataclass
class ModelConfig:
    """Configuration for a machine learning model."""

    model_id: str
    endpoint_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    metadata: Dict[str, Any] = None


class MCPClient:
    """
    Model Control Protocol client for managing and accessing different ML models.
    Provides a unified interface to interact with various ML models regardless of their backend.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP client with optional configuration path.

        Args:
            config_path: Path to JSON configuration file for models
        """
        self.models: Dict[str, ModelConfig] = {}
        self.session = requests.Session()

        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """Load model configurations from JSON file."""
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            for model_id, model_config in config_data.items():
                self.register_model(
                    model_id=model_id,
                    endpoint_url=model_config["endpoint_url"],
                    api_key=model_config.get("api_key"),
                    timeout=model_config.get("timeout", 30),
                    max_retries=model_config.get("max_retries", 3),
                    metadata=model_config.get("metadata", {}),
                )
            logger.info(f"Loaded {len(config_data)} model configurations")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise

    def register_model(
        self,
        model_id: str,
        endpoint_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new model with the client.

        Args:
            model_id: Unique identifier for the model
            endpoint_url: URL endpoint for the model API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
            metadata: Additional model metadata
        """
        if model_id in self.models:
            logger.warning(f"Overwriting existing model configuration for {model_id}")

        self.models[model_id] = ModelConfig(
            model_id=model_id,
            endpoint_url=endpoint_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {},
        )
        logger.info(f"Registered model: {model_id}")

    def unregister_model(self, model_id: str) -> bool:
        """
        Remove a model from the client.

        Args:
            model_id: Unique identifier for the model to remove

        Returns:
            True if model was removed, False if not found
        """
        if model_id in self.models:
            del self.models[model_id]
            logger.info(f"Unregistered model: {model_id}")
            return True
        logger.warning(f"Attempted to unregister non-existent model: {model_id}")
        return False

    def list_models(self) -> List[str]:
        """
        Get list of all registered model IDs.

        Returns:
            List of model IDs
        """
        return list(self.models.keys())

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.

        Args:
            model_id: Unique identifier for the model

        Returns:
            Dictionary with model information or None if model not found
        """
        if model_id not in self.models:
            logger.warning(f"Model not found: {model_id}")
            return None

        model = self.models[model_id]
        return {
            "model_id": model.model_id,
            "endpoint_url": model.endpoint_url,
            "timeout": model.timeout,
            "max_retries": model.max_retries,
            "metadata": model.metadata,
        }

    def predict(
        self,
        model_id: str,
        inputs: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a prediction using the specified model.

        Args:
            model_id: Unique identifier for the model to use
            inputs: Input data for the model
            params: Optional parameters for the prediction request

        Returns:
            Prediction results from the model

        Raises:
            ValueError: If model_id is not registered
            ConnectionError: If connection to model endpoint fails
            TimeoutError: If request times out
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")

        model = self.models[model_id]
        headers = {"Content-Type": "application/json"}

        if model.api_key:
            headers["Authorization"] = f"Bearer {model.api_key}"

        payload = {"inputs": inputs, "parameters": params or {}}

        retry_count = 0
        last_error = None

        while retry_count <= model.max_retries:
            try:
                logger.debug(f"Sending request to {model_id}")
                response = self.session.post(
                    model.endpoint_url,
                    headers=headers,
                    json=payload,
                    timeout=model.timeout,
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(
                    f"Request to {model_id} timed out (attempt {retry_count+1}/{model.max_retries+1})"
                )
            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(
                    f"Connection error for {model_id} (attempt {retry_count+1}/{model.max_retries+1})"
                )
            except requests.exceptions.HTTPError as e:
                last_error = e
                logger.error(f"HTTP error for {model_id}: {str(e)}")
                # Don't retry for client errors (4xx)
                if e.response.status_code >= 400 and e.response.status_code < 500:
                    break
                logger.warning(
                    f"Retrying request (attempt {retry_count+1}/{model.max_retries+1})"
                )
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error for {model_id}: {str(e)}")

            retry_count += 1

        # If we got here, all retries failed
        logger.error(
            f"All requests to {model_id} failed after {model.max_retries+1} attempts"
        )
        if isinstance(last_error, requests.exceptions.Timeout):
            raise TimeoutError(
                f"Request to {model_id} timed out after {model.max_retries+1} attempts"
            ) from last_error
        elif isinstance(last_error, requests.exceptions.ConnectionError):
            raise ConnectionError(
                f"Failed to connect to {model_id} after {model.max_retries+1} attempts"
            ) from last_error
        else:
            raise RuntimeError(
                f"Failed to get prediction from {model_id}: {str(last_error)}"
            ) from last_error

    def batch_predict(
        self,
        model_id: str,
        batch_inputs: List[Dict[str, Any]],
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Make batch predictions using the specified model.

        Args:
            model_id: Unique identifier for the model to use
            batch_inputs: List of input data for the model
            params: Optional parameters for the prediction request

        Returns:
            List of prediction results from the model
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")

        results = []
        for input_data in batch_inputs:
            try:
                result = self.predict(model_id, input_data, params)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch item: {str(e)}")
                results.append({"error": str(e)})

        return results

    def save_config(self, config_path: str) -> None:
        """
        Save current model configurations to a JSON file.

        Args:
            config_path: Path to save the configuration file
        """
        config_data = {}
        for model_id, model in self.models.items():
            config_data[model_id] = {
                "endpoint_url": model.endpoint_url,
                "timeout": model.timeout,
                "max_retries": model.max_retries,
                "metadata": model.metadata,
            }
            if model.api_key:
                config_data[model_id]["api_key"] = model.api_key

        try:
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Create MCP client
    client = MCPClient()

    # Register some example models
    client.register_model(
        model_id="text-classification",
        endpoint_url="https://api.example.com/models/text-classification",
        api_key="YOUR_API_KEY",
        metadata={"type": "classification", "version": "1.0.0"},
    )

    client.register_model(
        model_id="image-segmentation",
        endpoint_url="https://api.example.com/models/image-segmentation",
        api_key="YOUR_API_KEY",
        timeout=60,  # Longer timeout for image processing
        metadata={"type": "segmentation", "version": "2.1.0"},
    )

    # List available models
    models = client.list_models()
    print(f"Available models: {models}")

    # Make a prediction
    try:
        result = client.predict(
            model_id="text-classification",
            inputs={"text": "This is a sample text for classification"},
            params={"threshold": 0.5},
        )
        print(f"Prediction result: {result}")
    except Exception as e:
        print(f"Prediction failed: {str(e)}")

    # Save configuration for future use
    client.save_config("mcp_config.json")
