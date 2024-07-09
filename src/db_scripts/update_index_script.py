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
from utils.template_management import match_company_data_line_with_template


def upload_company_data(config: Config, client: OpenSearch, templates_json: dict) -> None:
    """
    Upload learning data documents to an existing OpenSearch index.
    Use the keyword values in each data line as metadata

    Args:
        config (Config): The configuration object to load settings from.
        client (OpenSearch): The OpenSearch client.
        templates_json (dict): The json content of the template file.
    """
    index_name          : str = config.load_config(["database", "company_data", "index_name"])
    company_data_path   : str = config.load_config(["paths", "company_data_path"])

    log(f"Uploading company-related documents from {company_data_path} to index {index_name}", "info")

    for file_name in os.listdir(company_data_path):
        file_path = os.path.join(company_data_path, file_name)
        log(f"\n\nProcessing file: {file_path}", "info")
        doc_id = os.path.splitext(file_name)[0]

        with open(file_path, 'r') as file:
            for data_line in file:
                if data_line.isspace() or data_line == "":
                    continue
                _, key_word_values = match_company_data_line_with_template(data_line, templates_json)
                assert("company_id"     not in key_word_values)
                assert("raw_data_line"  not in key_word_values)
                key_word_values["company_id"]       = int(doc_id)
                key_word_values["raw_data_line"]    = data_line

                client.index(index=index_name, body=key_word_values)
        log(f"Document {doc_id} indexed successfully", "info")

def upload_metrics_and_templates_data(config: Config, client: OpenSearch) -> dict:
    """
    Upload metrics data documents to an existing OpenSearch index.

    Args:
        config (Config): The configuration object to load settings from.
        client (OpenSearch): The OpenSearch client.

    Returns:
        dict: the content of the template file.
    """
    index_name_metrics      : str = config.load_config(["database", "metrics_data",     "index_name"])
    index_name_templates    : str = config.load_config(["database", "templates_data",   "index_name"])
    path_metrics            : str  = config.load_config(["paths", "metrics_data_path"])
    path_templates          : str  = config.load_config(["paths", "templates_data_path"])

    embedding = get_embedding(config, "Example document text").tolist()

    def upload_file(index_name: str, path: str, extra_param_embedding: str = "") -> dict:
        log(f"Uploading documents from {path} to index {index_name}", "info")


        with open(path, 'r') as metrics_file:
            content = json.load(metrics_file)

        for key, value in content.items():
            log(f"\t Uploading {key}", "info")
            if extra_param_embedding:
                value[extra_param_embedding] = embedding
            client.index(index=index_name, id=key, body=value)
        return content

    _   = upload_file(index_name_metrics,     path_metrics)
    res = upload_file(index_name_templates,   path_templates, extra_param_embedding="template_embedding")

    return res


if __name__ == "__main__":
    try:
        _config : Config      = Config()
        _client : OpenSearch  = instantiate_open_search_client(_config)

        _templates_json: dict = upload_metrics_and_templates_data(_config, _client)
        upload_company_data(_config, _client, _templates_json)
    except FileNotFoundError as e:
        log_error(f"File not found: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Failed to upload documents to the OpenSearch index: {e}", exception_to_raise=RuntimeError)
