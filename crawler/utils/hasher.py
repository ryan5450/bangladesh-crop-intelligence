"""Cryptographic hashing and URL canonicalization for document deduplication."""

import hashlib
from pathlib import Path
from typing import Union
from urllib.parse import urlparse, urlunparse


def hash_file(file_path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of byte contents."""
    return hashlib.sha256(data).hexdigest()


def hash_string(text: str) -> str:
    """Compute SHA-256 hash of a text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_url(url: str) -> str:
    """Canonicalize a URL by standardizing protocol, lowercase hostname, and removing tracking parameters."""
    if not url:
        return ""

    parsed = urlparse(url.strip())
    # Standardize scheme and lowercased netloc
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()

    # Remove trailing slashes on root path
    path = parsed.path
    if path == "/":
        path = ""

    # Reconstruct clean URL without fragment
    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))

