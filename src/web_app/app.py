from fastapi import FastAPI, HTTPException

from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest
from models.rag import RagHandler
from utils.config_management import Config
from utils.log_management import  log, log_error

app = FastAPI()

config                  : Config                = Config()
llm_request_parser      : LlmRequestParser      = LlmRequestParser(config)
rag_handler             : RagHandler            = RagHandler(config)
llm_request_answerer    : LlmRequestAnswerer    = LlmRequestAnswerer(config)

log("Web application initialized", "info")

@app.post("/query")
def query(request: QueryRequest):
    """
    Handle incoming queries and return responses.
    TODO update and correct comment
    The response is computed by gpt model with the specific data related to the query: company-related data, metrics and template.

    Args:
        request (QueryRequest): Request containing the query and company ID.

    Returns:
        str: Response from the LLM.
    """
    try:
        log(f"Received query: {request.query} for company_id: {request.company_id}", "info")
        llm_request_parser  .parse_user_request(request)
        rag_handler         .set_context_related_to_request(llm_request_parser)

        response: str = llm_request_answerer.answer(llm_request_parser, rag_handler)

        log(f"Returning response: {response}", "info")
        return {"response": response}
    except Exception as e:
        log_error(f"Error handling query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
