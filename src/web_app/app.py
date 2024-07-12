from fastapi import FastAPI, HTTPException

from models.llm_request_answerer import LlmRequestAnswerer
from models.llm_utils import QueryRequest
from utils.config_management import Config
from utils.log_management import log, log_error


# Initialize the different LLM models
config              : Config                = Config()
llm_request_answerer: LlmRequestAnswerer    = LlmRequestAnswerer(config)


# Initialize the FastAPI app
app = FastAPI()


# Log that the web application has been initialized
log("Web application initialized", "info")


@app.post("/query")
def query(request: QueryRequest) -> dict[str, str]:
    """
    Handle incoming queries to the /query endpoint.

    Args:
        request (QueryRequest): The incoming query request containing the company_id and raw query.

    Returns:
        dict: A dictionary containing the response string.

    Raises:
        HTTPException: If an error occurs while processing the request.
    """
    try:
        # Log the received query
        log(f"Received query: {request.query} for company_id: {request.company_id}", "info")

        # Handle the query and get the response
        response: str = llm_request_answerer.handle_query(request)

        # Log and return the response
        log(f"Returning response: {response}", "info")
        return {"response": response}
    except Exception as e:
        # Log the error and raise an HTTP exception
        log_error(f"Error handling query \"{request.query}\": {e}")
        HTTPException(status_code=500, detail=str(e))
