from typing import Dict, Any, Optional
import json
import pandas as pd
import psycopg2
from app.config import config


class DatabaseTool:
    """A tool for handling database operations with PostgreSQL/Supabase."""

    def __init__(self):
        # Initialize the PostgreSQL connection
        self.pg_connection = psycopg2.connect(
            host=config.pg.host,
            database=config.pg.database,
            port=config.pg.port,
            user=config.pg.user,
            password=config.pg.password,
        )
        # Autocommit mode to avoid transaction blocks
        self.pg_connection.autocommit = False

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query against PostgreSQL database.

        Args:
            sql_query: The SQL query to execute

        Returns:
            Dict containing status, data, and query information
        """
        try:
            # Create a new cursor for each query to avoid transaction issues
            with self.pg_connection.cursor() as cursor:
                cursor.execute(sql_query)
                try:
                    # Try to fetch results (for SELECT queries)
                    result = cursor.fetchall()
                    # # Convert result to JSON-serializable format
                    # serialized_result = json.dumps(
                    #     result, default=str, ensure_ascii=False
                    # )
                    df = pd.DataFrame(
                        result, columns=[desc[0] for desc in cursor.description]
                    )

                    # Commit the transaction
                    self.pg_connection.commit()

                    return {
                        "status": "success",
                        "data": df,
                        "query": sql_query,
                    }
                except psycopg2.ProgrammingError:
                    # This happens for non-SELECT queries (INSERT, UPDATE, etc.)
                    # so we don't need to commit the transaction
                    return {
                        "status": "error",
                        "message": "[non-SELECT queries (INSERT, UPDATE, etc.)]",
                    }
        except Exception as e:
            # Ensure any transaction is rolled back on error
            self.pg_connection.rollback()
            return {"status": "error", "message": str(e)}

    def test_connection(self) -> str:
        """Test the database connection and return status information."""
        try:
            with self.pg_connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS test")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return "Database connection successful. Test query returned: 1"
                else:
                    return f"Connection established but unexpected result: {result}"
        except Exception as e:
            self.pg_connection.rollback()
            return f"Database connection error: {str(e)}"

    def close(self):
        """Close the database connection."""
        if self.pg_connection:
            self.pg_connection.close()


# Create a singleton instance
db_tool = DatabaseTool()
