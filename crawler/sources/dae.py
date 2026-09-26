"""DAE (Department of Agricultural Extension) scraper and seed publications."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class DAECrawler(BaseSourceCrawler):
    """Scrapes farmer manuals, seasonal crop calendars, and IPM bulletins from DAE."""

    def __init__(self):
        super().__init__(
            source_key="DAE",
            base_urls=[
                "https://dae.gov.bd/pages/publications",
                "https://dae.gov.bd/pages/annual-reports",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative DAE crop calendar, extension guides, and farmer manuals."""
        return [
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/dce9df0806534ce9ab179d0c8306b923.pdf",
                title="বাংলাদেশে ফসল, উদ্ভিদ ও উদ্ভিদজাত পণ্যের বালাই ও ক্ষতিকর পোকা তালিকা (DAE Pest Management)",
                source="DAE",
                category_hint="pest_management",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/1685439b65e84885a6f4a73f3792fc91.pdf",
                title="কৃষি সম্প্রসারণ ম্যানুয়াল ও মাঠ পর্যায় প্রযুক্তি নির্দেশিকা (Agricultural Extension Manual DAE)",
                source="DAE",
                category_hint="cultivation_methods",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/933242bef44b4c1fab23f84e2df35cd1.pdf",
                title="কৃষি পণ্য রপ্তানীর রোডম্যাপ ও উৎপাদন নির্দেশিকা (DAE Agricultural Export Roadmap)",
                source="DAE",
                category_hint="cash_crops",
            ),
            CandidateDocument(
                url="https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dae/2024/12/bc9819b7c5904b8ebeb0bb7a00fa0490.pdf",
                title="ডিএই বার্ষিক ফসল উৎপাদন মূল্যায়ন ও মাঠ প্রযুক্তি নির্দেশিকা (DAE Field Technology Manual)",
                source="DAE",
                category_hint="crops",
            ),
        ]
