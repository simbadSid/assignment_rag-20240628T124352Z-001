from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.LLM_model import LLMHandler
from utils.log_management import  log, log_error

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    company_id: int


# TODO parametrize LLMHandler with the model instance
llm_handler = LLMHandler()
log("Web application initialized", "info")

@app.post("/query")
def query(request: QueryRequest):
    """
    Handle incoming queries and return responses.

    Args:
        request (QueryRequest): Request containing the query and company ID.

    Returns:
        str: Response from the LLM.
    """
    try:
        log(f"Received query: {request.query} for company_id: {request.company_id}", "info")
        response = llm_handler.handle_query(request.query, request.company_id)
        log(f"Returning response: {response}", "info")
        return {"response": response}
    except Exception as e:
        log_error(f"Error handling query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
