import pytest
from opensearchpy import OpenSearch
from db_scripts.create_index_script import create_index, instantiate_open_search_client
from db_scripts.update_index_script import upload_documents
from utils.log_management import log
from utils.config_management import Config


@pytest.fixture(scope="session")
def config() -> Config:
    """
    Create a session-scoped fixture to load the configuration once per test session.
    """
    log("Loading configuration", "info")
    return Config()


@pytest.fixture(scope="session")
def opensearch_client(config: Config):
    log("Setting up OpenSearch client fixture", "info")
    config      : Config        = Config()
    client      : OpenSearch    = instantiate_open_search_client(config)
    index_name  : str           = config.load_config(["database", "index_name"])
    yield client
    log("Tearing down OpenSearch client fixture", "info")
    client.indices.delete(index=index_name, ignore=[400, 404])

def test_create_index(opensearch_client: OpenSearch, config: Config):
    log("Starting test: test_create_index", "info")
    create_index()
    index_name = config.load_config(["database", "index_name"])
    assert opensearch_client.indices.exists(index=index_name)
    log("Completed test: test_create_index", "info")

def test_upload_documents(opensearch_client: OpenSearch, config):
    log("Starting test: test_upload_documents", "info")
    index_name = config.load_config(["database", "index_name"])
    create_index()
    upload_documents()
    response = opensearch_client.search(index=index_name, body={"query": {"match_all": {}}})
    assert response['hits']['total']['value'] > 0
    log("Completed test: test_upload_documents", "info")
