import pytest

from db_scripts.run_opensearch_container import run_opensearch_container
from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest
from utils.config_management import log, Config


config: Config = Config()


@pytest.fixture(scope="session")
def llm_request_parser():
    return LlmRequestParser(Config())


@pytest.mark.parametrize("user_query", [
    "What was the total revenue for the company in FY 1990?",
    "What was the total revenue for the company in FY from 1990 until 2000?",
    "What was the total revenue for the company?"])
def test_parse_user_request(llm_request_parser, user_query):
    log("Starting test: parse_user_request", "info")
    llm_request_parser = LlmRequestParser(config)
    query = QueryRequest(company_id=642, query=user_query)
    llm_request_parser.parse_user_request(query)



    assert isinstance(response, str)
    assert "revenue" in response.lower()
    log("Completed test: test_handle_query", "info")