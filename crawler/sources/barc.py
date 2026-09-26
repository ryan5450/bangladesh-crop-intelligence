"""BARC (Bangladesh Agricultural Research Council) scraper and seed publications."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class BARCCrawler(BaseSourceCrawler):
    """Scrapes national fertilizer guides, AEZ monographs, and research reports from BARC."""

    def __init__(self):
        super().__init__(
            source_key="BARC",
            base_urls=[
                "https://barc.gov.bd/pages/publications",
                "https://barc.gov.bd/pages/annual-reports",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative BARC Fertilizer Recommendation Guides and AEZ reports."""
        return [
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/bc9819b7c5904b8ebeb0bb7a00fa0490.pdf",
                title="বাংলাদেশ কৃষি গবেষণা কাউন্সিল ও ডিএই সার ব্যবস্থাপনা নির্দেশিকা (BARC Fertilizer Recommendation & Soil Health)",
                source="BARC",
                category_hint="fertilizer_management",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/b955f5ee044f43498f5578401af186bf.pdf",
                title="কৃষি পরিবেশ অঞ্চলভিত্তিক মৃত্তিকা ও পুষ্টি উপাদান ব্যবস্থাপনা নির্দেশিকা (AEZ Soil Nutrient Management)",
                source="BARC",
                category_hint="soil_management",
            ),
        ]
