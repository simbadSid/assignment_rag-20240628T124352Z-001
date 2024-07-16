import pytest
import json
from opensearchpy import OpenSearch

from db_scripts.create_index_script import create_index, instantiate_open_search_client
from db_scripts.update_index_script import upload_company_data, upload_metrics_and_templates_data
from utils.log_management import log
from utils.config_management import Config
from utils.template_management import get_template_keyword_list, match_company_data_line_with_template


config: Config = Config()
#run_opensearch_container(config)


@pytest.fixture(scope="session")
def opensearch_client():
    log("Setting up OpenSearch client fixture", "info")
    client: OpenSearch = instantiate_open_search_client(config)
    return client

@pytest.fixture(scope="session")
def templates_json():
    path_templates : str = config.load_config(["paths", "templates_data_path"])
    with open(path_templates, 'r') as metrics_file:
        templates_json = json.load(metrics_file)
    return templates_json

@pytest.mark.parametrize(
    "index_name,index_body",
    [
        (
            config.load_config(["database", "company_data", "index_name"]),
            config.load_config(["database", "company_data", "index_body"]),
        ),
        (
            config.load_config(["database", "metrics_data", "index_name"]),
            config.load_config(["database", "metrics_data", "index_body"])
        ),
        (
            config.load_config(["database", "templates_data", "index_name"]),
            config.load_config(["database", "templates_data", "index_body"])
        )
    ])
def test_create_index(opensearch_client: OpenSearch, index_name, index_body):
    log("Starting test: test_create_index", "info")
    create_index(opensearch_client, index_name, index_body)
    assert opensearch_client.indices.exists(index=index_name)
    log(f"Completed test: test_create_index: {index_name}", "info")


def test_upload_company_data(opensearch_client: OpenSearch, templates_json: dict):
    log("Starting test: upload_company_data", "info")
    index_name = config.load_config(["database", "company_data", "index_name"])
    index_body = config.load_config(["database", "company_data", "index_body"])

    create_index(opensearch_client, index_name, index_body)

    upload_company_data(config, opensearch_client, templates_json)

    response = opensearch_client.search(index=index_name, body={"query": {"match_all": {}}})
    assert response['hits']['total']['value'] > 0
    log("Completed test: test_upload_documents", "info")


def test_upload_metrics_and_templates_data(opensearch_client: OpenSearch):
    log("Starting test: upload_metrics_and_templates_data", "info")
    index_name = config.load_config(["database", "company_data", "index_name"])

    upload_metrics_and_templates_data(config, opensearch_client)

    opensearch_client.search(index=index_name, body={"query": {"match_all": {}}})
    log("Completed test: upload_metrics_and_templates_data", "info")


def test_match_company_data_line_with_template(templates_json: dict):
    """
    Test the match_template function to ensure it correctly identifies and extracts values from data_line (company-related data)
    based on template_phrase_list (templates.json).
    """
    data_line = "The company's Q1 2022 revenue was $50M, compared to Q1 2021 revenue in $45M, a YoY increase of 11.11%."

    expected_result = {
        "current_period": "Q1 2022",
        "metric_name": "revenue",
        "current_value": "$50M",
        "last_period": "Q1 2021",
        "last_value": "$45M",
        "increase_decrease_nochange": "increase",
        "pct_change": "11.11%"
    }

    matched, values = match_company_data_line_with_template(data_line, templates_json)

    assert matched is True
    assert values == expected_result


def test_get_template_keyword_list():
    """
    Test the get_template_keyword_list function to ensure it correctly extracts unique keywords from template phrases.
    """
    template_phrase_list = [
        "The company's {current_period} {metric_name} was {current_value}, compared to {last_period} {metric_name} in {last_value}, a YoY {increase_decrease_nochange} of {pct_change}.",
        "The company's {metric_name} {increased_decreased_remainedunchanged} from {last_value} in {last_period}, to {current_value} in {current_period}, a {timeframe} {increase_decrease_nochange} of {pct_change}.",
        "Against the industry benchmark{_for_the_metric}, the company performance in {last_snapshot_date} was {strong_weak_at_market_average} (percentile {percentile})."
    ]

    expected_keywords = [
        "current_period", "metric_name", "current_value", "last_period", "last_value",
        "increase_decrease_nochange", "pct_change", "increased_decreased_remainedunchanged",
        "timeframe", "_for_the_metric", "last_snapshot_date", "strong_weak_at_market_average", "percentile"
    ]

    # Get the result from the function
    result = get_template_keyword_list(template_phrase_list)

    # Assert that the result contains all the expected keywords
    assert sorted(result) == sorted(expected_keywords)
