"""
Internal SQL execution endpoint for chatbot service access.
This allows the chatbot to query the SQLite database without direct filesystem access.
"""
import os
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import text
from app.db import engine

router = APIRouter(prefix="/internal", tags=["internal"])

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "change-me-in-railway")


class SQLQueryRequest(BaseModel):
    query: str


@router.post("/execute-sql")
def execute_sql(
    payload: SQLQueryRequest,
    x_internal_key: str = Header(None),
):
    """
    Execute a read-only SELECT query against the backend database.
    Only accessible with the correct INTERNAL_API_KEY header.
    Returns rows as JSON with column names.
    """
    # Verify API key
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid or missing API key")

    # Validate query
    cleaned = payload.query.strip().lstrip("(")
    if not cleaned.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    try:
        with engine.connect() as conn:
            result = conn.execute(text(payload.query))
            rows = [dict(row._mapping) for row in result]
            columns = list(result.keys()) if result.keys() else []
            return {"rows": rows, "columns": columns}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
