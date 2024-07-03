from opensearchpy import OpenSearch
from utils.utils import load_config, log, log_error

def create_index() -> None:
    """
    Create an index in OpenSearch.

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
