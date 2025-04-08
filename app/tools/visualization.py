import base64
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from typing import Dict, Any, Optional, Union, List

from app.logger import logger


def make_chart(
    data: Union[pd.DataFrame, Dict[str, List]],
    chart_type: str = "bar",
    title: Optional[str] = None,
    x_col: Optional[str] = None,
    y_cols: Optional[List[str]] = None,
    max_points: int = 100,
) -> str:
    """
    Generate a visualization based on the provided data and chart type.
    Optimized for handling larger datasets.

    Args:
        data: DataFrame or dict data to visualize
        chart_type: Type of chart to generate (bar, line, pie, scatter, heatmap, or box)
        max_points: Maximum number of points to plot for performance
        title: Title for the chart
        x_col: Column name to use for x-axis
        y_cols: List of column names to use for y-axis

    Returns:
        A base64 encoded string of the chart image
    """
    # Convert dict to DataFrame if necessary
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Ensure we have data to visualize
    if data.empty:
        return "**Error in generating chart: no data available for visualization**"

    # Sample data if it's too large
    original_size = len(data)
    sampled_flag = False
    if len(data) > max_points and chart_type.lower() in ["bar", "line", "scatter"]:
        if chart_type.lower() == "line":
            # For line charts, use a smarter downsampling to preserve trends
            data = downsample_dataframe(data, max_points)
        else:
            # For other charts, use random sampling
            data = data.sample(max_points, random_state=42)
        sampled_flag = True
        sampled_info = f"Data sampled from {original_size} to {max_points} points for better performance"
        logger.info(sampled_info)

    # Determine x_col if not provided
    if x_col is None:
        # Try to find a datetime column first
        datetime_cols = [
            col
            for col in data.columns
            if pd.api.types.is_datetime64_any_dtype(data[col])
        ]
        if datetime_cols:
            x_col = datetime_cols[0]
        else:
            x_col = data.columns[0]

    # Determine y_cols if not provided
    if y_cols is None:
        # Use all numeric columns except the x_col as y_cols
        y_cols = [
            col
            for col in data.columns
            if col != x_col and pd.api.types.is_numeric_dtype(data[col])
        ]
        # If no numeric columns found, use the second column if available
        if not y_cols and len(data.columns) > 1:
            y_cols = [data.columns[1]]

    # Validate that x_col and y_cols exist in the data
    if x_col not in data.columns:
        return f"**Error in generating chart: column '{x_col}' not found in data**"

    for col in y_cols:
        if col not in data.columns:
            return f"**Error in generating chart: column '{col}' not found in data**"

    # Set memory-optimized figure
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    try:
        # Handle different chart types with optimized approaches
        if chart_type.lower() == "bar":
            if len(y_cols) == 1:
                # For single y column, create a standard bar chart
                ax = sns.barplot(x=data[x_col], y=data[y_cols[0]])
                plt.ylabel(y_cols[0])
            else:
                # For multiple y columns, create a grouped bar chart using melt
                melt_data = data.melt(
                    id_vars=[x_col],
                    value_vars=y_cols,
                    var_name="Series",
                    value_name="Value",
                )
                ax = sns.barplot(x=x_col, y="Value", hue="Series", data=melt_data)
                plt.ylabel("Value")

            plt.xlabel(x_col)
            plt.xticks(rotation=45, ha="right")

        elif chart_type.lower() == "line":
            # For line charts, optimize for time series if x is datetime
            if pd.api.types.is_datetime64_any_dtype(data[x_col]):
                for col in y_cols:
                    plt.plot(data[x_col], data[col], label=col)
                plt.legend()
            else:
                # Use seaborn's lineplot for other cases
                if len(y_cols) == 1:
                    ax = sns.lineplot(x=data[x_col], y=data[y_cols[0]], marker="o")
                else:
                    melt_data = data.melt(
                        id_vars=[x_col],
                        value_vars=y_cols,
                        var_name="Series",
                        value_name="Value",
                    )
                    ax = sns.lineplot(
                        x=x_col,
                        y="Value",
                        hue="Series",
                        data=melt_data,
                        marker="o",
                    )

            plt.xlabel(x_col)
            plt.ylabel(y_cols[0] if len(y_cols) == 1 else "Value")
            plt.xticks(rotation=45, ha="right")

        elif chart_type.lower() == "pie":
            # For pie charts, use only the top categories if data is large
            if len(data) > 10:
                # Group smaller categories into "Other"
                if len(y_cols) >= 1:
                    # Sort by value and keep top 9 categories
                    sorted_data = data.sort_values(by=y_cols[0], ascending=False)
                    top_data = sorted_data.head(9)
                    other_sum = sorted_data.iloc[9:][y_cols[0]].sum()

                    # Add "Other" category if needed
                    if len(sorted_data) > 9:
                        other_row = pd.DataFrame(
                            {x_col: ["Other"], y_cols[0]: [other_sum]}
                        )
                        plot_data = pd.concat([top_data, other_row])
                    else:
                        plot_data = top_data

                    plt.pie(
                        plot_data[y_cols[0]],
                        labels=plot_data[x_col].tolist(),
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                else:
                    plt.pie(
                        data.iloc[:, 0],
                        labels=data.index.tolist(),
                        autopct="%1.1f%%",
                        startangle=90,
                    )
            else:
                # Use all data if it's small enough
                if len(y_cols) >= 1:
                    plt.pie(
                        data[y_cols[0]],
                        labels=data[x_col].tolist(),
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                else:
                    plt.pie(
                        data.iloc[:, 0],
                        labels=data.index.tolist(),
                        autopct="%1.1f%%",
                        startangle=90,
                    )

            plt.axis("equal")

        elif chart_type.lower() == "scatter":
            # Need at least 2 numeric columns for a scatter plot
            if len(y_cols) >= 1:
                # If multiple y columns, create pairwise scatter plots
                if len(y_cols) > 1:
                    # Use the first y column with x_col
                    ax = sns.scatterplot(x=data[x_col], y=data[y_cols[0]])
                    plt.ylabel(y_cols[0])
                else:
                    ax = sns.scatterplot(x=data[x_col], y=data[y_cols[0]])
                    plt.ylabel(y_cols[0])

                plt.xlabel(x_col)
            else:
                return "**Error in generating chart: need at least two numeric columns for a scatter plot**"

        elif chart_type.lower() == "heatmap":
            # Create a correlation matrix for the numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            if len(numeric_data.columns) < 2:
                return "**Error in generating chart: need at least two numeric columns for a heatmap**"

            corr = numeric_data.corr()
            mask = np.triu(np.ones_like(corr, dtype=bool))
            ax = sns.heatmap(corr, mask=mask, annot=True, vmax=1, vmin=-1)

        elif chart_type.lower() == "box":
            if len(y_cols) >= 1:
                # If multiple y columns, create a boxplot for each
                melt_data = data.melt(
                    id_vars=[x_col],
                    value_vars=y_cols,
                    var_name="Series",
                    value_name="Value",
                )
                ax = sns.boxplot(x="Series", y="Value", data=melt_data)
                plt.ylabel("Value")
                plt.xlabel("Series")
            else:
                ax = sns.boxplot(y=data.iloc[:, 0])
                plt.ylabel(data.columns[0])

        else:
            return f"**Error in generating chart: unsupported chart type: {chart_type}. Supported types are: bar, line, pie, scatter, heatmap, box**"

        # Set title if provided
        if title:
            plt.title(title)

        # Adjust layout for better display
        plt.tight_layout()

        # Save the figure to a bytes buffer with optimized compression
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)

        # Encode the image to base64
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        # Return image as markdown with base64 encoding
        if sampled_flag:
            return f"![Chart](data:image/png;base64,{img_str})\n\n{sampled_info}"
        else:
            return f"![Chart](data:image/png;base64,{img_str})"

    except Exception as e:
        plt.close()
        return f"**Error in generating chart:**\n{str(e)}"


def downsample_dataframe(df: pd.DataFrame, n_samples: int) -> pd.DataFrame:
    """
    Intelligently downsample a DataFrame while preserving trends and important points.

    Args:
        df: DataFrame to downsample
        n_samples: Target number of samples

    Returns:
        Downsampled DataFrame
    """
    if len(df) <= n_samples:
        return df

    # If there's a datetime column, use that for intelligent time-based sampling
    datetime_cols = [
        col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])
    ]

    if datetime_cols:
        # Use the first datetime column found
        time_col = datetime_cols[0]

        # Determine appropriate frequency based on data size
        total_time_span = (df[time_col].max() - df[time_col].min()).total_seconds()
        freq = pd.Timedelta(seconds=total_time_span / n_samples)

        # Resample based on the calculated frequency
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Set the datetime column as index for resampling
        df_temp = df.set_index(time_col)

        # Determine appropriate aggregation method for each column
        resampled = df_temp.resample(freq).agg(
            {col: "mean" if col in numeric_cols else "first" for col in df_temp.columns}
        )

        # Reset index to get the datetime column back as a regular column
        return resampled.reset_index()
    else:
        # For non-time series data, use a combination of uniform sampling and important points

        # First, identify numeric columns for consideration
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            # Calculate row-wise statistical properties
            df["__importance"] = 0

            # Add importance based on extremes in each numeric column
            for col in numeric_cols:
                normalized = (
                    (df[col] - df[col].mean()) / df[col].std()
                    if df[col].std() > 0
                    else 0
                )
                df["__importance"] += abs(normalized)

            # Get important points (highest importance score)
            important_point_count = n_samples // 3
            regular_point_count = n_samples - important_point_count

            # Select important points
            important_points = df.nlargest(important_point_count, "__importance")

            # Get indices not in important_points
            remaining_indices = df.index.difference(important_points.index)

            # Uniformly sample from the remaining points
            step_size = max(1, len(remaining_indices) // regular_point_count)
            uniform_indices = remaining_indices[::step_size][:regular_point_count]

            # Combine the samples and sort by original index
            result = pd.concat([important_points, df.loc[uniform_indices]]).sort_index()

            # Drop the temporary importance column
            result = result.drop("__importance", axis=1)

            return result
        else:
            # If no numeric columns, just do uniform sampling
            return df.iloc[np.linspace(0, len(df) - 1, n_samples, dtype=int)]


def get_visualization_tool() -> Dict[str, Any]:
    """
    Get the visualization tool definition for use with LLM.

    Returns:
        A dictionary containing the tool definition
    """
    return {
        "type": "function",
        "function": {
            "name": "make_chart",
            "description": "Generate visualizations from data",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "description": "Type of chart to generate (bar, line, pie, scatter, heatmap, or box)",
                        "enum": ["bar", "line", "pie", "scatter", "heatmap", "box"],
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the chart",
                    },
                    "x_col": {
                        "type": "string",
                        "description": "Column name to use for x-axis",
                    },
                    "y_cols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of column names to use for y-axis (can be multiple columns)",
                    },
                },
                "required": ["chart_type", "title", "x_col", "y_cols"],
            },
        },
    }
