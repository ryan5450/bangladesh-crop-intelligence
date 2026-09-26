"""Taxonomy definitions and multi-label agricultural document classifier."""

from .document_classifier import classify_document, ClassificationResult
from .taxonomy import CROP_TAXONOMY, TOPIC_TAXONOMY

__all__ = [
    "classify_document",
    "ClassificationResult",
    "CROP_TAXONOMY",
    "TOPIC_TAXONOMY",
]

