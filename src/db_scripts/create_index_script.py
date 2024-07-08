from opensearchpy import OpenSearch
from utils.config_management import Config
from utils.log_management import log, log_error


def instantiate_open_search_client(config: Config) -> OpenSearch:
    log("Creating OpenSearch client", "info")

    open_search_url         = config.load_config(["open_search", "open_search_url"])
    open_search_port        = config.load_config(["open_search", "open_search_port"])
    open_search_admin_login = config.load_config(["open_search", "open_search_admin_login"])
    open_search_admin_pwd   = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')

    return OpenSearch(
        # TODO            DB username and password from config.json,
        hosts           = [f"{open_search_url}:{open_search_port}"],
        http_auth       = (open_search_admin_login, open_search_admin_pwd),
        use_ssl         = True,
        verify_certs    = False,
        ssl_show_warn   = False,
    )


def create_index(client: OpenSearch, index_name: str, index_body: dict) -> None:
    """
    Create an index in OpenSearch.
    """

    log(f"\n\nCreating index: {index_name}", "info")

    client.indices.create(index=index_name, body=index_body)

    log(f"Index name \"{index_name}\" created successfully", "info")

if __name__ == "__main__":
    try:
        _config     : Config        = Config()
        _client      : OpenSearch    = instantiate_open_search_client(_config)

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
