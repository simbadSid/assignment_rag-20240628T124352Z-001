"""
This module provides functionality for creating OpenSearch indices.
The script allows to create and configure indices to store the company-related data, templates and metrics.
"""

from opensearchpy import OpenSearch, RequestsHttpConnection
from utils.config_management import Config
from utils.log_management import log, log_error

def instantiate_open_search_client(config: Config) -> OpenSearch:
    """
    Create an OpenSearch client using configuration settings.

    Args:
        config (Config): The configuration object to load settings from.

    Returns:
        OpenSearch: The instantiated OpenSearch client.
    """
    log("Creating OpenSearch client", "info")

    open_search_client_config   = config.load_config(["open_search", "open_search_client_config"])
    open_search_admin_login     = config.load_config(["open_search", "open_search_admin_login"])
    open_search_admin_pwd       = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')

    # Format the opensearch config
    open_search_client_config["http_auth"]  = (open_search_admin_login, open_search_admin_pwd)

    # TODO to be integrated into the config file
    from opensearchpy import RequestsHttpConnection
    open_search_client_config["connection_class"] = RequestsHttpConnection

    return OpenSearch(**open_search_client_config)

def create_index(client: OpenSearch, index_name: str, index_body: dict) -> None:
    """
    Create an index in OpenSearch.

    Args:
        client (OpenSearch): The OpenSearch client.
        index_name (str): The name of the index to create.
        index_body (dict): The body of the index configuration.

    Returns:
        None
    """
    log(f"Creating index: {index_name}", "info")

    if client.indices.exists(index_name):
        log(f"Index name \"{index_name}\" exists already", "info")
    else:
        client.indices.create(index=index_name, body=index_body)
        log(f"Index name \"{index_name}\" created successfully", "info")

if __name__ == "__main__":
    try:
        _config     : Config        = Config()
        _client     : OpenSearch    = instantiate_open_search_client(_config)

        _index_name : str           = _config.load_config(["database", "company_data", "index_name"])
        _index_body : dict          = _config.load_config(["database", "company_data", "index_body"])
        create_index(_client, _index_name, _index_body)

        _index_name : str           = _config.load_config(["database", "metrics_data", "index_name"])
        _index_body : dict          = _config.load_config(["database", "metrics_data", "index_body"])
        create_index(_client, _index_name, _index_body)

        _index_name : str           = _config.load_config(["database", "templates_data", "index_name"])
        _index_body : dict          = _config.load_config(["database", "templates_data", "index_body"])
        create_index(_client, _index_name, _index_body)
    except Exception as e:
        log_error(f"Failed to create index: {e}", exception_to_raise=RuntimeError)
