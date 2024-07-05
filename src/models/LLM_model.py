import os
from langchain.llms import OpenAI
from utils.config_management import load_config_secret_key
from utils.log_management import log, log_error

class LLMHandler:
    def __init__(self):
        """
        Initialize the LLMHandler with configuration.
        """
        try:
            openai_api_key = load_config_secret_key(config_key_id='openai_api_key_path')

            # Set the OpenAI API key as an environment variable
            log("Set openAI API key as env variable (to handle mac os compatibility)", "info")
            os.environ['OPENAI_API_KEY'] = openai_api_key

            log("Initializing LLMHandler", "info")
            self.model = OpenAI(model="gpt-4")#, api_key=openai_api_key)
            self.memory = {}
            log("LLMHandler initialized successfully", "info")
        except Exception as e:
            log_error(f"Failed to initialize LLMHandler: {e}", exception_to_raise=RuntimeError)

    def handle_query(self, query: str, company_id: int) -> str:
        """
        Handle user query with the LLM.

        Args:
            query (str): User's query.
            company_id (int): ID of the company being queried.

        Returns:
            str: Response from the LLM.
        """
        try:
            log(f"Handling query for company_id {company_id}: {query}", "info")
            response = self.model.generate(query)
            log(f"Response: {response}", "info")
            return response
        except Exception as e:
            log_error(f"Error handling query: {e}", exception_to_raise=RuntimeError)

# Usage example
# llm_handler = LLMHandler()
# response = llm_handler.handle_query("What was the total revenue for the company in FY 2023?", 123)
