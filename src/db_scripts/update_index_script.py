import os
from opensearchpy import OpenSearch

from db_scripts.create_index_script import instantiate_open_search_client
from utils.config_management import log, log_error
from utils.config_management import Config

def upload_documents() -> None:
    """
    Upload documents to an existing OpenSearch index.
    """
    config                      : Config        = Config()
    client                      : OpenSearch    = instantiate_open_search_client(config)
    index_name                  : str           = config.load_config(["database", "index_name"])
    llm_learning_company_path   : str           = config.load_config(["paths", "llm_learning_company_path"])

    log(f"Uploading documents from {llm_learning_company_path} to index {index_name}", "info")

    for file_name in os.listdir(llm_learning_company_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(llm_learning_company_path, file_name)
            log(f"Processing file: {file_path}", "info")
            with open(file_path, 'r') as file:
                content = file.read()

            doc_id = os.path.splitext(file_name)[0]
            document = {"company_id": int(doc_id), "financial_data": content}

            client.index(index=index_name, id=doc_id, body=document)
            log(f"Document {doc_id} indexed successfully", "info")

if __name__ == "__main__":
    try:
        upload_documents()
    except FileNotFoundError as e:
        log_error(f"File not found: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Failed to upload documents: {e}", exception_to_raise=RuntimeError)
