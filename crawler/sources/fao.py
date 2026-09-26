"""FAO (Food and Agriculture Organization) Bangladesh publications scraper."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class FAOCrawler(BaseSourceCrawler):
    """Scrapes FAO Bangladesh country publications, post-harvest, and storage reports."""

    def __init__(self):
        super().__init__(
            source_key="FAO",
            base_urls=[
                "https://www.fao.org/bangladesh/resources/publications/en/",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative FAO Bangladesh agricultural and value chain reports."""
        return [
            CandidateDocument(
                url="https://faolex.fao.org/docs/pdf/bgd169557.pdf",
                title="FAO National Agricultural Policy of Bangladesh & Crop Diversification",
                source="FAO",
                category_hint="cultivation_methods",
            ),
            CandidateDocument(
                url="https://faolex.fao.org/docs/pdf/BGD214404.pdf",
                title="FAO Bangladesh Sustainable Irrigation & Soil Management Policy Framework",
                source="FAO",
                category_hint="irrigation_management",
            ),
            CandidateDocument(
                url="https://www.fao.org/giews/countrybrief/country/BGD/pdf_archive/BGD_Archive.pdf",
                title="FAO GIEWS Bangladesh Country Brief - Cereal Production & Food Supply Outlook",
                source="FAO",
                category_hint="cereals",
            ),
        ]
