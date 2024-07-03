import pytest
from src.models.LLM_handler import LLMHandler
from utils.utils import log, log_error

def test_handle_query():
    try:
        log("Starting test: test_handle_query", "info")
        llm_handler = LLMHandler()
        response = llm_handler.handle_query("What was the total revenue for the company in FY 2023?", 123)
        assert isinstance(response, str)
        assert "revenue" in response.lower()
        log("Completed test: test_handle_query", "info")
    except Exception as e:
        log_error(f"Error in test_handle_query: {e}", exception_to_raise=RuntimeError)
