"""BARI (Bangladesh Agricultural Research Institute) scraper and seed publications."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class BARICrawler(BaseSourceCrawler):
    """Scrapes horticulture, pulses, oilseeds, and tuber production guides from BARI."""

    def __init__(self):
        super().__init__(
            source_key="BARI",
            base_urls=[
                "https://bari.gov.bd/pages/publications",
                "https://bari.gov.bd/pages/annual-reports",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative BARI horticultural, tuber, pulse, and oilseed manuals."""
        return [
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bari/2026/8/173c3f11-9367-49d2-bdae-0d2978edb3a7.pdf",
                title="বারি বার্ষিক গবেষণা ও ফসল প্রযুক্তি সম্প্রসারণ প্রতিবেদন (BARI Annual Research & Crop Technology)",
                source="BARI",
                category_hint="crops",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bari/2024/12/6621e179345b4df787f5886eb6a71437.pdf",
                title="বারি উদ্ভাবিত ডাল, তেল ও মসলা জাতীয় ফসলের উৎপাদন নির্দেশিকা (BARI Crop Production Guidelines)",
                source="BARI",
                category_hint="pulses",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bari/2024/12/e14e1dbb7fee40888479648c17ae0356.pdf",
                title="বারি উদ্যানতত্ত্ব, ফল ও সবজি চাষাবাদ ব্যবস্থাপনা (BARI Horticulture & Vegetables Guidelines)",
                source="BARI",
                category_hint="fruits",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bari/2024/12/5a145b0d2d93478ea92fbb3d3cf063e1.pdf",
                title="বারি বার্ষিক কৃষি গবেষণা ও জাত উদ্ভাবন কার্যক্রম (BARI Varietal Development Report)",
                source="BARI",
                category_hint="seed_management",
            ),
        ]
