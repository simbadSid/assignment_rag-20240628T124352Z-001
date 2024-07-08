"""
This module provides functionality for parsing user requests to extract the expected data.
These data are extracted using a pre-trained OpenAI model.

"""

import openai
from models.llm_utils import QueryRequest
from utils.config_management import Config
from utils.log_management import log, log_error

NO_DATE_FOUND_STRING = "NO DATE WAS FOUND IN THE USER REQUEST"


class LlmRequestParser:
    """
    A class to parse user requests and infer dates using a pre-trained language model.

    Attributes:
        model_id (str): The ID of the pre-trained model to use for inference.
        company_id (str): The company identifier from the request.
        date (int): The inferred date from the query.
        query (str): The user query.
    """

    def __init__(self, config: Config):
        """
        Initialize the LlmRequestParser with configuration settings.

        Args:
            config (Config): The configuration object to load settings from.

        Raises:
            RuntimeError: If initialization fails.
        """
        try:
            log(f"Initializing {self.__class__.__name__}", "info")

            log(f"Setting the OpenAI API key ", "info")
            openai.api_key = config.load_config_secret_key(config_id_key='openai_api_key_path')

            self.model_id: str = config.load_config(["llm_request_parser", "model"])

            self.company_id: str = ""
            self.date: int = -1
            self.query: str = ""

            log(f"{self.__class__.__name__} initialized successfully", "info")
        except Exception as e:
            log_error(f"Failed to initialize {self.__class__.__name__}: {e}", exception_to_raise=RuntimeError)

    def parse_user_request(self, request: QueryRequest):
        """
        Parse the user request to infer the date using the pre-trained language model.
        This method requests the OpenAI API.

        Args:
            request (QueryRequest): The user query request.

        Raises:
            RuntimeError: If date inference fails.
        """
        try:
            log(f"Infer the year from the query", "info")

            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You will be provided with a request, and your task is to infer the time period from the request."
                                   " Only return a date or a gap of dates with no extra text."
                                   f"If no period is provided in the request, then return: {NO_DATE_FOUND_STRING}"
                    },
                    {
                        "role": "user",
                        "content": f"{request.query}"
                    }
                ],
                # temperature=0.7,
                # max_tokens=64,
                # top_p=1
            )
            response_date = response['choices'][0]['message']['content']
            if response_date == NO_DATE_FOUND_STRING:
                response_date = ""

            log(f"The year was successfully inferred from the query: {response_date}", "info")

            self.company_id = request.company_id
            self.date = response_date
            self.query = request.query

        except Exception as e:
            log_error(f"Failed to Infer the year from the query: {e}", exception_to_raise=RuntimeError)


if __name__ == '__main__':
    _llm_request_parser = LlmRequestParser(Config())
    _query = QueryRequest(company_id=642, query="What was the total revenue for the company in FY 1990?")
    # _query = QueryRequest(company_id=642, query="What was the total revenue for the company in FY from 1990 until 2000?")
    # _query = QueryRequest(company_id=642, query="What was the total revenue for the company?")

    _llm_request_parser.parse_user_request(_query)
