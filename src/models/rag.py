"""
This module provides functionality for fetching the known data (context) that will be used in answering the user request.
These fetched data are the company-related data, the templates and the metrics.
"""

import re
from opensearchpy import OpenSearch

from db_scripts.create_index_script import instantiate_open_search_client
from models.llm_request_parser import LlmRequestParser
from models.llm_utils import QueryRequest, get_embedding
from utils.config_management import Config
from utils.log_management import log, log_error


def keep_only_keywords(query: str) -> list:
    # TODO Find a better method
    non_key_word_list = ['in', 'a', 'the', 'at', 'from', "what", 'with', 'where', 'why', 'who', 'when', 'if',
                         'then', 'else', 'into', 'is', 'was', 'for', 'while']

    keywords = re.findall(r'\w+', query.lower())

    return [item for item in keywords if item not in non_key_word_list]


class RequestRelatedData:
    """
    Class that stores the data needed to answer a specific request
    """
    def __init__(self, company_data: list = [], metrics_data: dict = {}, templates_data : dict = {}):
        self.company_data   : list[str]         = company_data
        self.metrics_data   : dict[str, dict]   = metrics_data
        self.templates_data : dict              = templates_data


class RagHandler:
    """
    Class to handle Retrieval-Augmented Generation (RAG) operations.
    The objective is to fetch the known data (context) that will be used in answering the user request.
    These fetched data are the company-related data, the templates and the metrics.
    """

    def __init__(self, config: Config):
        """
        Initialize the RAG handler with OpenSearch client and configuration.
        """
        try:
            log("Initializing RAG handler", "info")

            self.client                 : OpenSearch            = instantiate_open_search_client(config)
            self.config                 : Config                = config
            self.request_related_data   : RequestRelatedData    = RequestRelatedData()

            log("RAG handler initialized successfully", "info")
        except Exception as e:
            log_error(f"Failed to initialize RAG handler: {e}", exception_to_raise=RuntimeError)

    def set_context_related_to_request(self, query_request: LlmRequestParser) -> None:
        """
        Fetch the context related to the client request from OpenSearch. Store the context in the internal attributes (company_data, metrics_data, templates_data)

        Args:
            query_request : The query request received from the client and preparsed.
        """

        log(f"{self.__class__.__name__}: Retrieving company-data, template and metrics related to query for company_id {query_request.request_context.company_id}: {query_request.request_context.query}", "info")

        self.request_related_data = RequestRelatedData(
            company_data    = self.fetch_company_data(query_request),
            metrics_data    = self.fetch_metrics(query_request),
            templates_data  = self.fetch_templates(query_request)
        )

        return

    def fetch_company_data(self, query_request: LlmRequestParser) -> list:
        """
        Fetch the company-related data from OpenSearch.
        Optimization: extracts from the query some data (period, metric, etc) and uses them to retrieve the company-related data from the index table.

        Args:
            query_request : The query request received from the client and preparsed.

        Returns:
            str: The company-related data.
        """

        log("Fetch company-related data relative to the query", "info")

        company_index: str = self.config.load_config(["database", "company_data", "index_name"])

        body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"company_id"     : query_request.request_context.company_id}},
                        {"match": {"current_period" : query_request.request_context.date}},

                        # TODO Find the metric in the request and use it in requesting the index
                        #{"match": {"metric_name": keyword}} for keyword in keywords
                    ]
                }
            }
        }

        response = self.client.search(index=company_index, body=body)
        response = [hit["_source"] for hit in response["hits"]["hits"]]
        return [data_dict['raw_data_line'] for data_dict in response]

    def fetch_metrics(self, query_request: LlmRequestParser) -> dict:
        """
        Fetch from the input  index tables the metrics related to the query from OpenSearch using
        keyword matching between the query and the metric_name parameter of the metrics table.

        Args:
            query_request : The query request received from the client and preparsed.

        Returns:
            dict[str, dict]: The list of all the metrics that match a keyword in the request (1 dictionary per metric).
        """

        log("Fetch metrics data relative to the query", "info")

        metrics_index   : str       = self.config.load_config(["database", "metrics_data", "index_name"])
        keywords        : list[str] = keep_only_keywords(query_request.request_context.query)

        # Construct a bool query to match any of the keywords in the metric_name field
        body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"metric_name": keyword}} for keyword in keywords
                    ]
                }
            }
        }

        response = self.client.search(index=metrics_index, body=body)
        metrics_list = [hit["_source"] for hit in response["hits"]["hits"]]
        return {metric['metric_name']: metric for metric in metrics_list}

    def fetch_templates(self, query_request: LlmRequestParser) -> dict:
        """
        Fetch from the input  index tables the templates related to the query from OpenSearch using
        semantic matching between the query and the analysis_type parameter of the templates table.

        Args:
            query_request : The query request received from the client and preparsed.

        Returns:
            dict[str, dict]: The list of all the templates that match the query (1 dictionary per template).
        """

        log("Fetch templates data relative to the query", "info")

        templates_index: str = self.config.load_config(["database", "templates_data", "index_name"])

        embedding = get_embedding(self.config, query_request.request_context.query)

        knn_param = 5 #TODO optimize

        query = {
            "size": knn_param,
            "query": {
                "knn": {
                    "template_embedding": {
                        "vector": embedding.tolist(),
                        "k": knn_param
                    }
                }
            }
        }

        response = self.client.search(index=templates_index, body=query)
        return response['hits']['hits']


# Example usage
if __name__ == "__main__":
    try:
        _config             : Config            = Config()
        _llm_request_parser : LlmRequestParser  = LlmRequestParser(_config)
        _rag                : RagHandler        = RagHandler(_config)

        _llm_request_parser.parse_user_request(QueryRequest(company_id = 642, query = "What was the total revenue for the company in FY 2023?"))
        _rag.set_context_related_to_request(_llm_request_parser)

    except Exception as _e:
        log_error(f"Failed to get context related to request: {_e}", exception_to_raise=RuntimeError)
