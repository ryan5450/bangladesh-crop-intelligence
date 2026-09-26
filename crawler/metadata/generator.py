"""Metadata generator, quality scoring, and canonical file renaming."""

import datetime
from pathlib import Path
from typing import Optional

from classifier.document_classifier import ClassificationResult
from metadata.schema import DocumentMetadata
from processor.text_extractor import ExtractedDocument
from utils.file_helper import sanitize_filename
from utils.hasher import hash_string


def calculate_quality_score(doc: ExtractedDocument, classification: ClassificationResult) -> float:
    """Calculate an objective document quality score between 0.0 and 1.0.
    
    Evaluates:
    - Word count and text volume
    - Multi-page structural completeness
    - Specificity of matched agronomic topics and crops
    """
    score = 0.0

    # 1. Word Count Density (40% weight)
    if doc.word_count >= 2500:
        score += 0.40
    elif doc.word_count >= 1000:
        score += 0.32
    elif doc.word_count >= 400:
        score += 0.24
    elif doc.word_count >= 100:
        score += 0.15
    else:
        score += 0.05

    # 2. Page Structure (25% weight)
    if doc.pages >= 10:
        score += 0.25
    elif doc.pages >= 3:
        score += 0.20
    elif doc.pages >= 1:
        score += 0.15

    # 3. Topic & Crop Relevance (35% weight)
    topic_count = len(classification.topics)
    if topic_count >= 3:
        score += 0.20
    elif topic_count >= 1:
        score += 0.12

    if classification.related_crops:
        score += 0.15

    # Round cleanly to 2 decimal places, bounded [0.10, 1.00]
    return max(0.10, min(1.0, round(score, 2)))


def generate_canonical_filename(
    source: str,
    title: str,
    primary_category: str,
    language: str,
    doc_hash: str,
) -> str:
    """Derive a standardized, human-readable canonical filename.
    
    Format:
        {source}_{slug_title}_{lang}_{hash[:6]}.pdf
        e.g., brri_modern_rice_cultivation_guide_bn_a4f91b.pdf
    """
    clean_src = sanitize_filename(source.lower(), max_length=10)
    clean_slug = sanitize_filename(title, max_length=50)

    # Normalize language code for filename
    clean_lang = language.replace("/", "_")

    short_hash = doc_hash[:6]

    return f"{clean_src}_{clean_slug}_{clean_lang}_{short_hash}.pdf"


def generate_document_metadata(
    doc: ExtractedDocument,
    classification: ClassificationResult,
    source: str,
    url: str,
    language: str,
    doc_hash: str,
    file_size_bytes: int,
) -> DocumentMetadata:
    """Compile comprehensive document metadata according to project specifications."""
    document_id = f"{source.lower()}_{doc_hash[:12]}"
    filename = generate_canonical_filename(
        source=source,
        title=doc.title,
        primary_category=classification.primary_category,
        language=language,
        doc_hash=doc_hash,
    )
    quality = calculate_quality_score(doc, classification)

    file_size_kb = round(file_size_bytes / 1024.0, 1)

    return DocumentMetadata(
        document_id=document_id,
        title=doc.title,
        source=source.upper(),
        url=url,
        language=language,
        categories=classification.categories,
        related_crops=classification.related_crops,
        topics=classification.topics,
        quality_score=quality,
        filename=filename,
        pages=doc.pages,
        file_size_kb=file_size_kb,
        author=doc.author,
        extracted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )

