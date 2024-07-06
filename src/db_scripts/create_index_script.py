from opensearchpy import OpenSearch
from utils.config_management import Config
from utils.log_management import log, log_error


def instantiate_open_search_client(config: Config) -> OpenSearch:
    log("Creating OpenSearch client", "info")

    open_search_url         = config.load_config(["open_search", "open_search_url"])
    open_search_port        = config.load_config(["open_search", "open_search_port"])
    open_search_admin_login = config.load_config(["open_search", "open_search_admin_login"])
    open_search_admin_pwd   = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')

    client = OpenSearch(
        # TODO            DB username and password from config.json,
        hosts           = [f"{open_search_url}:{open_search_port}"],
        http_auth       = (open_search_admin_login, open_search_admin_pwd),
        use_ssl         = True,
        verify_certs    = False,
        ssl_show_warn   = False,
    )

    return client


def create_index() -> None:
    """
    Create an index in OpenSearch.
    """
    config      : Config        = Config()
    client      : OpenSearch    = instantiate_open_search_client(config)
    index_name  : str           = config.load_config(["database", "index_name"])
    index_body  : dict          = config.load_config(["database", "index_body"])

    log(f"Creating index: {index_name}", "info")

    client.indices.create(index=index_name, body=index_body)

    log(f"Index name \"{index_name}\" created successfully", "info")

if __name__ == "__main__":
    try:
        create_index()
    except Exception as e:
        log_error(f"Failed to create index: {e}", exception_to_raise=RuntimeError)
