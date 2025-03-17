"""
Example usage of the NL2SQL agent workflow to convert natural language to SQL.
"""

from agent.nl2sql_agent import NL2SQLAgent
from nl2sql_prompts import NL2SQL_PROMPTS
from llm.llm_openai import OpenAILLM

# Sample database schema - replace with your actual schema
SAMPLE_SCHEMA = {
    "analytics_db": {
        "user_events": {
            "columns": [
                {
                    "name": "user_id",
                    "type": "UInt64",
                    "description": "Unique identifier for the user",
                },
                {
                    "name": "event_time",
                    "type": "DateTime",
                    "description": "Timestamp when the event occurred",
                },
                {
                    "name": "event_type",
                    "type": "String",
                    "description": "Type of user event (click, view, purchase)",
                },
                {
                    "name": "page_id",
                    "type": "UInt32",
                    "description": "Identifier for the page where event occurred",
                },
                {
                    "name": "product_id",
                    "type": "UInt32",
                    "description": "Product identifier if applicable",
                },
                {
                    "name": "user_agent",
                    "type": "String",
                    "description": "User agent string",
                },
                {
                    "name": "ip_address",
                    "type": "String",
                    "description": "IP address of the user",
                },
            ],
            "description": "Table containing all user events and interactions with the website/app",
        },
        "products": {
            "columns": [
                {
                    "name": "product_id",
                    "type": "UInt32",
                    "description": "Unique identifier for the product",
                },
                {
                    "name": "name",
                    "type": "String",
                    "description": "Name of the product",
                },
                {
                    "name": "price",
                    "type": "Decimal(10,2)",
                    "description": "Current price of the product",
                },
                {
                    "name": "category",
                    "type": "String",
                    "description": "Product category",
                },
                {
                    "name": "created_at",
                    "type": "DateTime",
                    "description": "When the product was added",
                },
            ],
            "description": "Product catalog information",
        },
    },
    "sales_db": {
        "transactions": {
            "columns": [
                {
                    "name": "transaction_id",
                    "type": "UInt64",
                    "description": "Unique identifier for the transaction",
                },
                {
                    "name": "user_id",
                    "type": "UInt64",
                    "description": "User who made the purchase",
                },
                {
                    "name": "transaction_time",
                    "type": "DateTime",
                    "description": "When the transaction occurred",
                },
                {
                    "name": "total_amount",
                    "type": "Decimal(12,2)",
                    "description": "Total amount of the transaction",
                },
                {
                    "name": "payment_method",
                    "type": "String",
                    "description": "Method of payment",
                },
            ],
            "description": "Sales transaction records",
        },
        "transaction_items": {
            "columns": [
                {
                    "name": "item_id",
                    "type": "UInt64",
                    "description": "Unique identifier for the line item",
                },
                {
                    "name": "transaction_id",
                    "type": "UInt64",
                    "description": "Transaction this item belongs to",
                },
                {
                    "name": "product_id",
                    "type": "UInt32",
                    "description": "Product that was purchased",
                },
                {
                    "name": "quantity",
                    "type": "UInt16",
                    "description": "Number of items purchased",
                },
                {
                    "name": "price_per_unit",
                    "type": "Decimal(10,2)",
                    "description": "Price per unit at time of purchase",
                },
            ],
            "description": "Individual line items in transactions",
        },
    },
}


def main():
    """Example of running the NL2SQL agent"""

    # Initialize the LLM model
    # Replace with your specific configuration
    llm = OpenAILLM(
        model_name="gpt-4",  # Or your preferred model
        api_key="your_api_key",  # Replace with your actual API key
        api_base="https://api.openai.com/v1",  # Default OpenAI API endpoint
    )

    # Initialize the NL2SQL agent
    nl2sql_agent = NL2SQLAgent(
        agent_name="NL2SQL Agent",
        llm_model=llm,
        table_schemas=SAMPLE_SCHEMA,
        prompts=NL2SQL_PROMPTS,
    )

    # Example natural language queries
    queries = [
        "How many products do we have in each category?",
        "What was the total sales amount last month?",
        "Who are our top 10 users by transaction amount in the last 30 days?",
    ]

    # Process each query
    for i, query in enumerate(queries):
        print(f"\n--- Query {i+1}: {query} ---")

        # First run - initial SQL generation
        response = nl2sql_agent.work(query)

        # Check if successful
        if response["status"] == "success":
            print("Status: Success!")
            print(f"Message: {response['content']['message']}")
            print("Result path:", response["content"]["result_path"])
        else:
            print("Status: Failed")
            print(f"Error: {response['content']['message']}")

            # Example of providing feedback and retrying
            if i == 0:  # Just for the first query as an example
                print("\n--- Retrying with feedback ---")
                feedback = "Please use COUNT(DISTINCT product_id) instead of COUNT(*)"
                retry_response = nl2sql_agent.work(query, feedback)

                if retry_response["status"] == "success":
                    print("Retry Status: Success!")
                    print(f"Message: {retry_response['content']['message']}")
                else:
                    print("Retry Status: Failed")
                    print(f"Error: {retry_response['content']['message']}")


if __name__ == "__main__":
    main()
