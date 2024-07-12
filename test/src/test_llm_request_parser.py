import pytest

from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest
from utils.config_management import log, Config


config: Config = Config()
path_test_request: str = "test/data/input/test_requests.docx"

@pytest.fixture(scope="session")
def llm_request_parser():
    return LlmRequestParser(Config())


@pytest.mark.parametrize("user_query, expected_data_list", [
    ("What was the total revenue for the company in FY 1990?"                   , ["1990"]),
    ("What was the total revenue for the company in FY from 1990 until 2000?"   , ["1990", "2000"]),
    ("What was the total revenue for the company?"                              , [""])])
def test_parse_user_request(llm_request_parser, user_query, expected_data_list):
    log("Starting test: parse_user_request", "info")
    llm_request_parser = LlmRequestParser(config)
    query = QueryRequest(company_id=642, query=user_query)
    llm_request_parser.parse_user_request(query)


    for expected_data in expected_data_list:
        assert expected_data in llm_request_parser.request_context.date
    log("Completed test: parse_user_request", "info")
