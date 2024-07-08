"""
update_index_script.py
Connects to an existing opensearch service and updates it with the learning data related to the companies, the metrics and the templates.
"""

import os
from opensearchpy import OpenSearch
import json

from db_scripts.create_index_script import instantiate_open_search_client
from utils.config_management import log, log_error
from utils.config_management import Config
from models.llm_utils import get_embedding

def upload_company_data(config: Config, client: OpenSearch) -> None:
    """
    Upload learning data documents to an existing OpenSearch index.
    """
    index_name          : str = config.load_config(["database", "company_data", "index_name"])
    company_data_path   : str = config.load_config(["paths", "company_data_path"])

    log(f"Uploading company-related documents from {company_data_path} to index {index_name}", "info")

    for file_name in os.listdir(company_data_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(company_data_path, file_name)
            log(f"\n\nProcessing file: {file_path}", "info")
            with open(file_path, 'r') as file:
                content = file.read()

            doc_id = os.path.splitext(file_name)[0]
            #TODO Extract metadata (ex: data) by fetching each line using the templates
            document = {"company_id": int(doc_id), "financial_data": content}

            client.index(index=index_name, id=doc_id, body=document)
            log(f"Document {doc_id} indexed successfully", "info")

def upload_metrics_and_templates_data(config: Config, client: OpenSearch) -> None:
    """
    Upload metrics data documents to an existing OpenSearch index.
    """
    index_name_metrics      : str = config.load_config(["database", "metrics_data",     "index_name"])
    index_name_templates    : str = config.load_config(["database", "templates_data",   "index_name"])
    path_metrics            : str  = config.load_config(["paths", "metrics_data_path"])
    path_templates          : str  = config.load_config(["paths", "templates_data_path"])

    embedding = get_embedding(config, "Example document text").tolist()

    def upload_file(index_name: str, path: str, extra_param_embedding: str = ""):
        log(f"Uploading documents from {path} to index {index_name}", "info")


        with open(path, 'r') as metrics_file:
            content = json.load(metrics_file)

        for key, value in content.items():
            log(f"\t Uploading {key}", "info")
            if extra_param_embedding:
                value[extra_param_embedding] = embedding
            client.index(index=index_name, id=key, body=value)

    upload_file(index_name_metrics,     path_metrics)
    upload_file(index_name_templates,   path_templates, extra_param_embedding="template_embedding")

if __name__ == "__main__":
    try:
        _config : Config      = Config()
        _client : OpenSearch  = instantiate_open_search_client(_config)

        upload_company_data(_config, _client)
        upload_metrics_and_templates_data(_config, _client)
    except FileNotFoundError as e:
        log_error(f"File not found: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Failed to upload documents: {e}", exception_to_raise=RuntimeError)
