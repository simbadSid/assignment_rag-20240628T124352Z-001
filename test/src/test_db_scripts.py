import pytest
from opensearchpy import OpenSearch
from src.db_scripts.create_index_script import create_index
from src.db_scripts.update_index_script import upload_documents
from utils.utils import load_config, log, log_error

@pytest.fixture
def opensearch_client():
    config = load_config()
    log("Setting up OpenSearch client fixture", "info")
    client = OpenSearch(
        hosts=[config["paths"]["open_search_url"]],
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
