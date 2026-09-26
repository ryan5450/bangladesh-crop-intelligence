"""BAMIS (Bangladesh Agrometeorological Information System) scraper and bulletins."""

from typing import List
from sources.base import BaseSourceCrawler, CandidateDocument


class BAMISCrawler(BaseSourceCrawler):
    """Scrapes agrometeorological advisory bulletins and climate risk manuals from BAMIS."""

    def __init__(self):
        super().__init__(
            source_key="BAMIS",
            base_urls=[
                "https://www.bamis.gov.bd/page/project-publication/",
                "https://www.bamis.gov.bd/page/others-publication/",
            ],
        )

    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative BAMIS Agromet advisory bulletins and seasonal warnings."""
        return [
            CandidateDocument(
                url="https://www.bamis.gov.bd/res/attachment/2019/08/24/5146.pdf",
                title="বাংলাদেশ কৃষি আবহাওয়া তথ্য পদ্ধতি ও পরামর্শ বুলেটিন নির্দেশিকা (BAMIS Agromet Advisory Bulletin)",
                source="BAMIS",
                category_hint="climate_adaptation",
            ),
            CandidateDocument(
                url="https://www.bamis.gov.bd/res/attachment/2019/08/29/5284.pdf",
                title="জলবায়ু পরিবর্তন ঝুঁকি হ্রাস ও কৃষি সম্প্রসারণ গাইডলাইন (Climate Adaptation & Early Warning)",
                source="BAMIS",
                category_hint="climate_adaptation",
            ),
            CandidateDocument(
                url="https://www.bamis.gov.bd/res/attachment/2020/01/10/11804.pdf",
                title="কৃষি আবহাওয়া পূর্বাভাস, খরা ও বন্যা ব্যবস্থাপনা নির্দেশিকা (Agromet Weather Forecasting Manual)",
                source="BAMIS",
                category_hint="climate_adaptation",
            ),
            CandidateDocument(
                url="https://www.bamis.gov.bd/res/attachment/2019/08/24/5151.pdf",
                title="বামিস প্রকল্প গবেষণা প্রকাশনা ও ফসলের ক্ষয়ক্ষতি প্রশমন (BAMIS Crop Risk Mitigation Publication)",
                source="BAMIS",
                category_hint="crop_calendar",
            ),
        ]
