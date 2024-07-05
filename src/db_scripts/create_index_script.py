from opensearchpy import OpenSearch
from utils.config_management import load_config, load_config_secret_key
from utils.log_management import log, log_error

def create_index() -> None:
    """
    Create an index in OpenSearch.

    Returns:
        None
    """
    try:
        config = load_config()
        log("Creating OpenSearch client", "info")

        open_search_url = config["open_search"]["open_search_url"]
        open_search_port = config["open_search"]["open_search_port"]


        open_search_admin_pwd = load_config_secret_key(config_key_id='opensearch_admin_pwd_path')

        client = OpenSearch(
            hosts=[f"{open_search_url}:{open_search_port}"],
#            http_auth=(config["database"]["username"], config["database"]["password"]),
            http_auth=("admin", open_search_admin_pwd),
        )
        log(f"Creating index: {config['database']['index_name']}", "info")

        client.indices.create(
            index=config["database"]["index_name"],
            body=config["index_body"]
        )
        log(f"Index {config['database']['index_name']} created successfully", "info")
    except Exception as e:
        log_error(f"Failed to create index: {e}", exception_to_raise=RuntimeError)

if __name__ == "__main__":
    create_index()
