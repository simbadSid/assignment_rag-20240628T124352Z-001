import os
from opensearchpy import OpenSearch
from utils.utils import load_config, log, log_error

def upload_documents() -> None:
    """
    Upload documents to an existing OpenSearch index.

    Returns:
        None
    """
    try:
        config = load_config()
        log("Creating OpenSearch client", "info")

        client = OpenSearch(
            hosts=[config["paths"]["open_search_url"]],
            http_auth=(config["database"]["username"], config["database"]["password"]),
        )

        llm_learning_company_path = config["paths"]["llm_learning_company_path"]
        index_name = config["database"]["index_name"]

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
    except FileNotFoundError as e:
        log_error(f"File not found: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Failed to upload documents: {e}", exception_to_raise=RuntimeError)

if __name__ == "__main__":
    upload_documents()
