import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Use Railway's internal network to call the backend
# Default to localhost for local development
BACKEND_INTERNAL_URL = os.getenv(
    "BACKEND_INTERNAL_URL",
    "http://localhost:8000"
)
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "change-me-in-railway")


def execute_query(sql: str):
    """
    Execute a read-only SQL query by calling the backend's internal SQL endpoint.
    This avoids direct database file access and uses Railway's internal network.
    
    Returns a list of dict rows.
    """
    statement = sql.strip()
    if not statement.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    try:
        response = httpx.post(
            f"{BACKEND_INTERNAL_URL}/internal/execute-sql",
            json={"query": statement},
            headers={"x-internal-key": INTERNAL_API_KEY},
            timeout=15.0,
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise RuntimeError(f"SQL execution failed: {error_detail}")
        
        data = response.json()
        return data.get("rows", [])
    
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to connect to backend: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"SQL execution error: {str(e)}")
