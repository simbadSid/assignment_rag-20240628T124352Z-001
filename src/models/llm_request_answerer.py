import openai

from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest
from models.rag import RagHandler
from utils.config_management import Config
from utils.log_management import log, log_error


class LlmRequestAnswerer:
    def __init__(self, config: Config):
        """
        Initialize the LlmRequestAnswerer with configuration.
        """
        try:
            log(f"Initializing {self.__class__.__name__}", "info")

            log(f"Setting the OpenAI API key ", "info")
            openai.api_key = config.load_config_secret_key(config_id_key='openai_api_key_path')

            self.model_id           : str = config.load_config(["llm_request_answerer", "model"])
            self.llm_request_parser : LlmRequestParser = LlmRequestParser(config)
            self.rag_handler        : RagHandler = RagHandler(config)

            log(f"{self.__class__.__name__} initialized successfully", "info")
        except Exception as e:
            log_error(f"Failed to initialize {self.__class__.__name__}: {e}", exception_to_raise=RuntimeError)

    def handle_query(self, request: QueryRequest) -> str:
        """
        Handle user query with by requesting the configured LLM model.

        Args:
        request (QueryRequest): The incoming query request containing the company_id and raw query.

        Returns:
            str: Response from the LLM.
        """
        try:
            log(f"Answering to query for company_id {request.company_id}: {request.query}", "info")

            # Parse the user request and get info (date, related metrics, etc)
            self.llm_request_parser.parse_user_request(request)

            # Set context related to the request (company data, metrics files, etc)
            self.rag_handler.set_context_related_to_request(self.llm_request_parser)

            # Ping the model with the user request and the necessary data to answer it
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
                                   "Company-related data"                   + f": \"{self.rag_handler.request_related_data.company_data}\"."
                                   "Metrics"                                + f": \"{self.rag_handler.request_related_data.metrics_data}\"."
                                   "Templates you can use in your answer"   + f": \"{self.rag_handler.request_related_data.templates_data}\"."
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
