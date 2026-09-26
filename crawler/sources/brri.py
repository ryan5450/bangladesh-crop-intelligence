"""BRRI (Bangladesh Rice Research Institute) scraper and seed publications."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class BRRICrawler(BaseSourceCrawler):
    """Scrapes rice research handbooks, bulletins, and advisory PDFs from BRRI."""

    def __init__(self):
        super().__init__(
            source_key="BRRI",
            base_urls=[
                "https://brri.gov.bd/pages/publications",
                "https://brri.gov.bd/pages/annual-reports",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative, verified BRRI rice manuals and pathology guides."""
        return [
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-brri/2024/12/136eb09cdd0546a085f54110d4f21feb.pdf",
                title="বাংলাদেশ রাইস জার্নাল ও উন্নত আধুনিক ধান চাষ প্রযুক্তি নির্দেশিকা (BRRI Rice Journal & Agronomy)",
                source="BRRI",
                category_hint="cereals",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-brri/2024/12/fefc7e0a6d8e40ba9d8f1b1e0edcd635.pdf",
                title="বাংলাদেশ ধান গবেষণা ইনস্টিটিউট বার্ষিক গবেষণা ও প্রযুক্তি প্রতিবেদন (BRRI Annual Research Report)",
                source="BRRI",
                category_hint="cereals",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-brri/2024/12/88243bc3a1be497f9a569109e3941064.pdf",
                title="বোরো ও আমন ধানের রোগবালাই দমন ও সার ব্যবস্থাপনা (BRRI Crop Care Guidelines)",
                source="BRRI",
                category_hint="diseases",
            ),
        ]
