"""Embedding function service managing local and cloud embedding providers."""

import os
from typing import Any, Optional
import chromadb
from chromadb.api.types import EmbeddingFunction

from vector_store.config import EMBEDDING_PROVIDER


def get_embedding_function(provider: Optional[str] = None) -> Optional[EmbeddingFunction]:
    """Retrieve the configured ChromaDB embedding function.

    Args:
        provider: 'default', 'openai', or 'gemini'. Defaults to EMBEDDING_PROVIDER env var.

    Returns:
        A ChromaDB EmbeddingFunction instance, or None to use collection default.
    """
    selected_provider = (provider or EMBEDDING_PROVIDER).lower()

    if selected_provider in ("default", "onnx", "local"):
        # Uses ChromaDB's optimized ONNX MiniLM engine (local, CPU-optimized, zero external calls)
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        return ONNXMiniLM_L6_V2()

    elif selected_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI embeddings.")
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddingFunction(api_key=api_key, model_name=model_name)

    elif selected_provider in ("gemini", "google"):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for Gemini embeddings.")
        from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
        model_name = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
        return GoogleGenerativeAiEmbeddingFunction(api_key=api_key, model_name=model_name)

    else:
        raise ValueError(
            f"Unsupported embedding provider: '{selected_provider}'. "
            "Supported providers: 'default', 'openai', 'gemini'."
        )
