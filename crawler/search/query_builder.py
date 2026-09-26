"""Bilingual query builder constructing targeted agricultural PDF search terms."""

from typing import Dict, List


class AgriculturalQueryBuilder:
    """Generates focused bilingual search queries for Bangladesh agriculture."""

    CROPS_BN = [
        "ধান", "বোরো ধান", "আমন ধান", "গম", "ভুট্টা",
        "আলু", "বেগুন", "টমেটো", "সরিষা", "মসুর",
        "পাট", "আম", "কলা", "পেঁয়াজ", "রসুন",
    ]

    CROPS_EN = [
        "Rice", "Boro Rice", "Aman Rice", "Wheat", "Maize",
        "Potato", "Brinjal", "Tomato", "Mustard", "Lentil",
        "Jute", "Mango", "Banana", "Onion", "Garlic",
    ]

    TOPICS_BN = [
        "চাষ পদ্ধতি", "রোগবালাই দমন", "সার ব্যবস্থাপনা",
        "সেচ ব্যবস্থাপনা", "কীটপতঙ্গ দমন", "ব্লাস্ট রোগ",
        "মৌসুমী ফসল দিনপঞ্জি", "জলবায়ু সহনশীল জাত",
    ]

    TOPICS_EN = [
        "Cultivation Guide", "Disease Management", "Fertilizer Recommendation",
        "Irrigation Management", "Pest Management", "Blast Disease",
        "Crop Calendar", "Climate Resilient Varieties",
    ]

    @classmethod
    def generate_portal_queries(cls, source_key: str) -> List[str]:
        """Generate focused queries for a specific portal."""
        queries: List[str] = []

        if source_key.upper() == "BRRI":
            queries = [
                "site:brri.gov.bd filetype:pdf",
                "site:brri.portal.gov.bd filetype:pdf",
                "BRRI আধুনিক ধান চাষ filetype:pdf",
                "BRRI ধানের জাত পরিচিতি filetype:pdf",
                "BRRI ধানের রোগবালাই ব্যবস্থাপনা filetype:pdf",
                "BRRI Fertilizer Management Rice filetype:pdf",
                "BRRI Boro Rice Cultivation filetype:pdf",
                "BRRI Annual Research Report filetype:pdf",
            ]
        elif source_key.upper() == "BARI":
            queries = [
                "site:bari.gov.bd filetype:pdf",
                "site:bari.portal.gov.bd filetype:pdf",
                "BARI সবজি চাষ নির্দেশিকা filetype:pdf",
                "BARI ডাল ও তৈলবীজ চাষ filetype:pdf",
                "BARI আলু ও মশলা ফসল উৎপাদন filetype:pdf",
                "BARI Horticulture Production Guide filetype:pdf",
                "BARI Technology Handbook filetype:pdf",
            ]
        elif source_key.upper() == "DAE":
            queries = [
                "site:dae.gov.bd filetype:pdf",
                "site:dae.portal.gov.bd filetype:pdf",
                "DAE কৃষি প্রযুক্তি হাতবই filetype:pdf",
                "DAE ফসল উৎপাদন নির্দেশিকা filetype:pdf",
                "DAE IPM বালাই ব্যবস্থাপনা filetype:pdf",
                "DAE Crop Calendar Bangladesh filetype:pdf",
            ]
        elif source_key.upper() == "BARC":
            queries = [
                "site:barc.gov.bd filetype:pdf",
                "site:barc.portal.gov.bd filetype:pdf",
                "BARC Fertilizer Recommendation Guide filetype:pdf",
                "BARC সার সুপারিশ মালা filetype:pdf",
                "BARC Agro-ecological Zones Bangladesh filetype:pdf",
            ]
        elif source_key.upper() == "BAMIS":
            queries = [
                "site:bamis.gov.bd filetype:pdf",
                "BAMIS Agrometeorological Advisory Bulletin filetype:pdf",
                "BAMIS কৃষি আবহাওয়া বুলেটিন filetype:pdf",
            ]
        elif source_key.upper() == "FAO":
            queries = [
                "site:fao.org Bangladesh agriculture crop filetype:pdf",
                "site:fao.org Bangladesh rice value chain filetype:pdf",
                "site:fao.org Bangladesh post harvest storage filetype:pdf",
            ]
        else:
            # General combined
            for c_en in cls.CROPS_EN[:5]:
                queries.append(f"Bangladesh {c_en} cultivation guide filetype:pdf")
            for c_bn in cls.CROPS_BN[:5]:
                queries.append(f"বাংলাদেশ {c_bn} চাষ নির্দেশিকা filetype:pdf")

        return queries

    @classmethod
    def generate_crop_queries(cls, crop_name: str) -> List[str]:
        """Generate targeted queries for a specific crop."""
        return [
            f"Bangladesh {crop_name} cultivation production manual filetype:pdf",
            f"Bangladesh {crop_name} disease pest management filetype:pdf",
            f"বাংলাদেশ {crop_name} চাষ পদ্ধতি রোগ দমন filetype:pdf",
            f"{crop_name} সার প্রয়োগ সেচ ব্যবস্থাপনা filetype:pdf",
        ]

