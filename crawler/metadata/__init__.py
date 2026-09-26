"""Metadata models, generation, scoring, and catalog persistence."""

from .schema import DocumentMetadata
from .generator import generate_document_metadata, generate_canonical_filename
from .catalog import CatalogManager

__all__ = [
    "DocumentMetadata",
    "generate_document_metadata",
    "generate_canonical_filename",
    "CatalogManager",
]

