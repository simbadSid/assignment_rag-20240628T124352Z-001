"""
This module provides functionality for handling query requests and generating embeddings using a pre-trained language model.
"""

from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel, PreTrainedTokenizer, PreTrainedModel
import torch

from utils.config_management import Config


class QueryRequest(BaseModel):
    """
    A data model for storing user query-requests.
    """
    query       : str   # The query string provided by the user
    company_id  : int   # The identifier for the company associated with the query


def get_embedding(config: Config, text: str):
    """
    Generate embeddings for a given text using a pre-trained language model.

    This function loads a pre-trained model and tokenizer specified in the configuration, processes the input text,
    and returns its embedding.

    Args:
        config (Config): Configuration object to load model settings.
        text (str): The input text to generate embeddings for.

    Returns:
        numpy.ndarray: The generated embedding for the input text.
    """
    # Load pre-trained model and tokenizer for semantic search within an OpenSearch table
    model_id    : str                   = config.load_config(["llm_semantic_matching", "model"])
    tokenizer   : PreTrainedTokenizer   = AutoTokenizer.from_pretrained(model_id)
    model       : PreTrainedModel       = AutoModel.from_pretrained(model_id)

    # Tokenize the input text and generate embeddings
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings.detach().numpy().flatten()
