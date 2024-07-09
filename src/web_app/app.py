from fastapi import FastAPI, HTTPException

from models.llm_request_answerer import LlmRequestAnswerer
from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest
from models.rag import RagHandler
from utils.config_management import Config
from utils.log_management import log, log_error

# Initialize the FastAPI app
app = FastAPI()

config              : Config            = Config()
llm_request_parser  : LlmRequestParser  = LlmRequestParser(config)
rag_handler         : RagHandler        = RagHandler(config)
llm_request_answerer: LlmRequestAnswerer= LlmRequestAnswerer(config)

# Log that the web application has been initialized
log("Web application initialized", "info")


@app.post("/query")
def query(request: QueryRequest):
    """
    Handle incoming queries to the /query endpoint.

    Args:
        request (QueryRequest): The incoming query request containing the company_id and query.

    Returns:
        dict: A dictionary containing the response string.

    Raises:
        HTTPException: If an error occurs while processing the request.
    """
    try:
        # Log the received query
        log(f"Received query: {request.query} for company_id: {request.company_id}", "info")

        # Parse the user request and get info (date, related metrics, etc)
        llm_request_parser.parse_user_request(request)

        # Set context related to the request (company data, metrics files, etc)
        rag_handler.set_context_related_to_request(llm_request_parser)

        # Handle the query and get the response
        response: str = llm_request_answerer.handle_query(llm_request_parser, rag_handler)

        # Log and return the response
        log(f"Returning response: {response}", "info")
        return {"response": response}
    except Exception as e:
        # Log the error and raise an HTTP exception
        log_error(f"Error handling query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
