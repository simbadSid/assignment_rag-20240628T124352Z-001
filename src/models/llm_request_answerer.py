import os
from langchain.llms import OpenAI

import openai

from models.llm_request_parser import LlmRequestParser
from models.rag import RagHandler
from utils.config_management import Config
from utils.log_management import log, log_error
from web_app.app import QueryRequest


class LlmRequestAnswerer:
    def __init__(self, config: Config):
        """
        Initialize the LlmRequestAnswerer with configuration.
        """
        try:
            log(f"Initializing {self.__class__.__name__}", "info")

            log(f"Setting the OpenAI API key ", "info")
            openai.api_key = config.load_config_secret_key(config_id_key='openai_api_key_path')

            self.model_id: str = config.load_config(["llm_request_answerer", "model"])

            log(f"{self.__class__.__name__} initialized successfully", "info")
        except Exception as e:
            log_error(f"Failed to initialize {self.__class__.__name__}: {e}", exception_to_raise=RuntimeError)

    def handle_query(self, request: LlmRequestParser, rag: RagHandler) -> str:
        """
        Handle user query with by requesting the configured LLM model.

        Args:
            request (QueryRequest): User's query (company_id, query).
            rag (RagHandler): Data related to the query ( company-related data, metrics and template).

        Returns:
            str: Response from the LLM.
        """
        try:
            log(f"Answering to query for company_id {request.company_id}: {request.query}", "info")

            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": f"You will be provided with a user request relative to a company {request.company_id}."
                                   "Your task is to answer to this request."
                                   "In order to answer, use the provided company-related data."
                                   "Also use the provided definition of the metrics used in the request."
                                   "Finally try to format your answer using the provided templates."
                    },
                    {
                        "role": "user",
                        "content": "User request"                           + f": \"{request.query}\"."
                                   "Company-related data"                   + f": \"{rag.company_data}\"."
                                   "Metrics"                                + f": \"{rag.metrics_data}\"."
                                   "Templates you can use in your answer"   + f": \"{rag.templates_data}\"."
                    }
                ],
                # temperature=0.7,
                # max_tokens=64,
                # top_p=1
            )
            response = response['choices'][0]['message']['content']
            log(f"Response: {response}", "info")
            return response
        except Exception as e:
            log_error(f"Error handling query: {e}", exception_to_raise=RuntimeError)
