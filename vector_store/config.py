"""Configuration settings for Vector Embeddings and ChromaDB vector store."""

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", BASE_DIR / "knowledge_base"))

# ChromaDB persistence directory
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", KB_DIR / "chroma_db"))

# Default collection name for agricultural intelligence
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "bangladesh_crop_intelligence")

# Input chunks source path
CHUNKS_PATH = Path(os.getenv("CHUNKS_PATH", KB_DIR / "chunks" / "chunks.json"))

# Catalog source path for BRRI rice variety fact sheets
VARIETIES_CATALOG_PATH = Path(
    os.getenv("VARIETIES_CATALOG_PATH", KB_DIR / "reports" / "brri_rice_varieties_catalog.json")
)

# Batch processing settings
DEFAULT_BATCH_SIZE = int(os.getenv("CHROMA_BATCH_SIZE", "500"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# Embedding Provider settings: 'default' (ONNX all-MiniLM-L6-v2), 'openai', or 'gemini'
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "default").lower()


class VectorStoreConfig(BaseModel):
    """Pydantic model validating vector store settings."""

    persist_dir: Path = Field(default=CHROMA_PERSIST_DIR)
    collection_name: str = Field(default=COLLECTION_NAME)
    chunks_path: Path = Field(default=CHUNKS_PATH)
    varieties_catalog_path: Path = Field(default=VARIETIES_CATALOG_PATH)
    batch_size: int = Field(default=DEFAULT_BATCH_SIZE, ge=10, le=5000)
    default_top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=50)
    embedding_provider: str = Field(default=EMBEDDING_PROVIDER)


default_config = VectorStoreConfig()
