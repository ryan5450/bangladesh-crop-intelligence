"""Multi-label document classifier mapping agricultural texts to the 24 categories."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from config import CATEGORIES
from .taxonomy import CROP_TAXONOMY, TOPIC_TAXONOMY


@dataclass
class ClassificationResult:
    """Outcome of document classification."""
    primary_category: str
    categories: List[str]
    related_crops: List[str]
    topics: List[str]
    scores: Dict[str, float] = field(default_factory=dict)


def detect_crops(text: str, title: str) -> List[str]:
    """Detect which Bangladesh crops are explicitly referenced in the title and text."""
    combined = f"{title}\n{text}".lower()
    matched_crops: Set[str] = set()

    for crop_name, details in CROP_TAXONOMY.items():
        aliases = details.get("aliases", [])
        for alias in aliases:
            # Word boundary matching where possible, or exact substring for Bengali
            pattern = rf"(?:\b|\s|^){re.escape(alias.lower())}(?:\b|\s|$)"
            if re.search(pattern, combined):
                matched_crops.add(crop_name)
                break

    # If sub-types are matched, ensure parent (e.g. "Rice") is also tracked
    for crop in list(matched_crops):
        if "Rice" in crop and "Rice" not in matched_crops:
            matched_crops.add("Rice")

    return sorted(list(matched_crops))


def score_categories(text: str, title: str, detected_crops: List[str]) -> Dict[str, float]:
    """Compute score for each of the 24 categories using weighted keyword matching."""
    scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORIES}

    title_lower = title.lower()
    text_lower = text[:15000].lower()  # First 15,000 characters (highest thematic density)

    for cat, data in TOPIC_TAXONOMY.items():
        if cat not in scores:
            continue
        keywords = data.get("keywords", [])
        weight = data.get("weight", 1.0)

        cat_score = 0.0
        for kw in keywords:
            kw_clean = kw.lower()
            # Title matches are weighted heavily (3.5x)
            if kw_clean in title_lower:
                cat_score += 3.5 * weight

            # Text body matches
            count = text_lower.count(kw_clean)
            if count > 0:
                cat_score += min(count, 10) * 0.4 * weight

        scores[cat] += cat_score

    # Factor in detected crops
    for crop in detected_crops:
        crop_info = CROP_TAXONOMY.get(crop, {})
        crop_cat = crop_info.get("category")
        if crop_cat and crop_cat in scores:
            scores[crop_cat] += 4.0

    return scores


def derive_topics(scores: Dict[str, float], detected_crops: List[str]) -> List[str]:
    """Generate human-readable topic labels based on high-scoring categories and crops."""
    topics: List[str] = []

    topic_label_map = {
        "fertilizer_management": "Fertilizer & Soil Nutrient Management",
        "pest_management": "Integrated Pest Management (IPM)",
        "diseases": "Crop Disease Diagnosis & Control",
        "irrigation_management": "Irrigation & Water Regimen (AWD)",
        "soil_management": "Soil Health & Salinity Management",
        "cultivation_methods": "Modern Agronomic Practices & Sowing",
        "seed_management": "Seed Selection & Preservation",
        "crop_calendar": "Seasonal Sowing & Harvesting Calendar",
        "climate_adaptation": "Climate Resilience & Stress Tolerance",
        "weed_management": "Weed Control & Herbicide Regimen",
        "organic_farming": "Organic & Vermicompost Systems",
        "harvesting": "Harvest Timing & Mechanization",
        "storage": "Grain Storage & Cold Preservation",
        "post_harvest": "Post-Harvest Processing & Milling",
        "greenhouse": "Controlled Environment & Polyhouse",
    }

    # Top scoring agronomic topics
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for cat, score in sorted_cats:
        if score >= 2.0 and cat in topic_label_map:
            topics.append(topic_label_map[cat])

    if not topics and detected_crops:
        topics.append(f"{detected_crops[0]} Cultivation Guide")

    return topics[:6]


def classify_document(text: str, title: str) -> ClassificationResult:
    """Classify agricultural text across the 24 categories."""
    detected_crops = detect_crops(text, title)
    scores = score_categories(text, title, detected_crops)

    # Sort categories by score descending
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Determine primary category (highest score, or default to crops/cereals)
    primary = sorted_cats[0][0]
    if sorted_cats[0][1] < 1.0:
        if "Rice" in detected_crops:
            primary = "cereals"
        else:
            primary = "cultivation_methods" if "cultivation" in text.lower() else "crops"

    # Select active categories (score > 1.5, always includes primary)
    selected_categories = [primary]
    for cat, score in sorted_cats:
        if score >= 1.5 and cat not in selected_categories:
            selected_categories.append(cat)

    # Ensure general 'crops' category is present if crops were detected
    if detected_crops and "crops" not in selected_categories:
        selected_categories.append("crops")

    topics = derive_topics(scores, detected_crops)

    return ClassificationResult(
        primary_category=primary,
        categories=selected_categories,
        related_crops=detected_crops,
        topics=topics,
        scores=scores,
    )

