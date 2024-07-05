import pytest
from opensearchpy import OpenSearch
from db_scripts.create_index_script import create_index
from db_scripts.update_index_script import upload_documents
from utils.log_management import log, log_error
from utils.config_management import load_config

@pytest.fixture
def opensearch_client():
    config = load_config()
    log("Setting up OpenSearch client fixture", "info")

    open_search_url = config["open_search"]["open_search_url"]
    open_search_port = config["open_search"]["open_search_port"]
    client = OpenSearch(
        hosts=[f"{open_search_url}:{open_search_port}"],
        http_auth=(config["database"]["username"], config["database"]["password"]),
    )
    yield client
    log("Tearing down OpenSearch client fixture", "info")
    client.indices.delete(index=config["database"]["index_name"], ignore=[400, 404])

def test_create_index(opensearch_client):
    try:
        log("Starting test: test_create_index", "info")
        create_index()
        config = load_config()
        assert opensearch_client.indices.exists(index=config["database"]["index_name"])
        log("Completed test: test_create_index", "info")
    except Exception as e:
        log_error(f"Error in test_create_index: {e}", exception_to_raise=RuntimeError)

def test_upload_documents(opensearch_client):
    try:
        log("Starting test: test_upload_documents", "info")
        create_index()
        upload_documents()
        config = load_config()
        response = opensearch_client.search(index=config["database"]["index_name"], body={"query": {"match_all": {}}})
        assert response['hits']['total']['value'] > 0
        log("Completed test: test_upload_documents", "info")
    except Exception as e:
        log_error(f"Error in test_upload_documents: {e}", exception_to_raise=RuntimeError)
