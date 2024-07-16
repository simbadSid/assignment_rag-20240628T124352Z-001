from xml.dom.minidom import Document

import pytest
from docx import Document

from models.llm_request_answerer import LlmRequestAnswerer
from models.llm_utils import QueryRequest
from utils.config_management import log, Config


config: Config = Config()

def get_user_request_list() -> list[str]:
    test_requests_path = config.load_config(["paths", "test_requests_path"])
    user_request_lines = []

    file = Document(test_requests_path)
    for para in file.paragraphs:
        # Split the paragraph into lines by newlines
        para_lines = para.text.split('\n')
        para_lines = list(filter(lambda s: not s.isspace() and s != "", para_lines))

        if not para_lines:
            continue
        # Extend the lines list with the lines from the current paragraph
        user_request_lines.extend(para_lines)
        break

    return user_request_lines


@pytest.fixture(scope="session")
def llm_request_answerer() -> LlmRequestAnswerer:
    return LlmRequestAnswerer(config)


@pytest.mark.parametrize("user_query",
                         [QueryRequest(company_id="642", query=data_line) for data_line in get_user_request_list()])
def test_llm_request_answerer(llm_request_answerer, user_query):
    log(f"Handling user request: {user_query}", "info")

    response: str = llm_request_answerer.handle_query(user_query)

    log(f"Answer: {response}", "info")
