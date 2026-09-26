"""Cross-lingual agricultural term expansion for English <-> Bangla search."""

import re
from typing import Dict, List, Set

# Comprehensive English -> Bangla agricultural domain dictionary
ENG_TO_BN_TERMS = {
    # Crops
    "rice": "ধান",
    "paddy": "ধান",
    "wheat": "গম",
    "maize": "ভুট্টা",
    "corn": "ভুট্টা",
    "potato": "আলু",
    "jute": "পাট",
    "mustard": "সরিষা",
    "lentil": "মসুর ডাল",
    "pulse": "ডাল জাতীয় ফসল",
    "onion": "পেঁয়াজ",
    "garlic": "রসুন",
    "chili": "মরিচ",
    "mango": "আম",
    "banana": "কলা",
    "guava": "পেয়ারা",
    "tomato": "টমেটো",
    "brinjal": "বেগুন",
    "eggplant": "বেগুন",

    # Seasons & Cropping
    "boro": "বোরো",
    "aman": "আমন",
    "aus": "আউশ",
    "rabi": "রবি মৌসুম",
    "kharif": "খরিপ মৌসুম",

    # Diseases
    "blast": "ব্লাস্ট রোগ",
    "leaf blast": "পাতা ব্লাস্ট",
    "neck blast": "শীষ ব্লাস্ট",
    "blight": "ব্লাইট পাতা পোড়া",
    "bacterial leaf blight": "ব্যাকটেরিয়াল লিফ ব্লাইট পাতা পোড়া রোগ",
    "sheath blight": "খোল পোড়া রোগ",
    "sheath rot": "খোল পচা রোগ",
    "brown spot": "বাদামী দাগ রোগ",
    "tungro": "টুংরো রোগ",
    "rust": "মরিচা রোগ",
    "late blight": "নাবি ধসা রোগ",
    "disease": "রোগ বালাই",

    # Pests & Insects
    "brown planthopper": "বাদামী গাছফড়িং কারেন্ট পোকা",
    "bph": "বাদামী গাছফড়িং কারেন্ট পোকা",
    "stem borer": "মাজরা পোকা",
    "leaf folder": "পাতা মোড়ানো পোকা",
    "pest": "কীটপতঙ্গ বালাই",
    "insect": "পোকা মাকড়",
    "pesticide": "কীটনাশক বালাইনাশক",
    "fungicide": "ছত্রাকনাশক",

    # Stresses & Environment
    "drought": "খরা খরা সহনশীল",
    "saline": "লবণাক্ততা লবণাক্ত সহনশীল",
    "salinity": "লবণাক্ততা লবণাক্ত সহনশীল",
    "flood": "বন্যা জলমগ্নতা নিমজ্জিত",
    "submergence": "জলমগ্নতা সহনশীল",
    "cold": "শৈত্যপ্রবাহ ঠান্ডা সহনশীল",

    # Fertilizer & Soil
    "fertilizer": "সার প্রয়োগ সার ব্যবস্থাপনা",
    "urea": "ইউরিয়া সার",
    "potash": "পটাশ এমপি সার",
    "mop": "এমপি পটাশ সার",
    "tsp": "টিএসপি সার",
    "gypsum": "জিপসাম গন্ধক সার",
    "zinc": "জিঙ্ক সালফেট দস্তা সার",
    "compost": "কম্পোস্ট জৈব সার",
    "soil": "মাটি মৃত্তিকা ব্যবস্থাপনা",

    # Agronomy & Farming
    "seedling": "চারা বীজতলা",
    "seedbed": "বীজতলা",
    "transplanting": "চারা রোপণ",
    "sowing": "বীজ বপন",
    "weeding": "আগাছা দমন নিড়ানি",
    "harvest": "ফসল কর্তন ধান কাটা",
    "yield": "ফলন হেক্টর প্রতি ফলন",
    "duration": "জীবনকাল",
    "lifecycle": "জীবনকাল",
    "variety": "জাত উচ্চফলনশীল জাত",
    "hybrid": "হাইব্রিড জাত",
    "characteristics": "জাতের বৈশিষ্ট্য",
    "management": "ব্যবস্থাপনা ও পরিচর্যা",
    "symptoms": "লক্ষণ",
    "remedy": "প্রতিকার দমন ব্যবস্থা",
    "prevention": "প্রতিরোধ ব্যবস্থা",
    "cultivation": "চাষাবাদ পদ্ধতি",
}

# Invert for Bangla -> English expansion
BN_TO_ENG_TERMS = {
    "ধান": "rice paddy",
    "গম": "wheat",
    "ভুট্টা": "maize corn",
    "আলু": "potato",
    "পাট": "jute",
    "সরিষা": "mustard",
    "ডাল": "lentil pulse",
    "বোরো": "boro season rice",
    "আমন": "aman season rice",
    "আউশ": "aus season rice",
    "ব্লাস্ট": "blast disease pyricularia",
    "পাতা পোড়া": "leaf blight blb",
    "খোল পোড়া": "sheath blight",
    "পোকা": "pest insect",
    "মাজরা পোকা": "stem borer",
    "গাছফড়িং": "brown planthopper bph",
    "খরা": "drought tolerant",
    "লবণাক্ততা": "salinity tolerant saline",
    "বন্যা": "flood submergence",
    "জলমগ্নতা": "submergence tolerant",
    "সার": "fertilizer management urea tsp mop",
    "ইউরিয়া": "urea nitrogen fertilizer",
    "পটাশ": "potash mop potassium",
    "চারা": "seedling transplanting",
    "বীজতলা": "seedbed nursery",
    "রোপণ": "transplanting",
    "ফলন": "yield production",
    "জীবনকাল": "crop duration lifecycle",
    "জাত": "variety cultivar",
    "লক্ষণ": "symptoms identification",
    "প্রতিকার": "remedy control management prevention",
    "চাষাবাদ": "cultivation management",
}


BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def to_bangla_digits(num_str: str) -> str:
    """Convert ASCII digits to Bengali digits."""
    return num_str.translate(BN_DIGITS)


def to_english_digits(num_str: str) -> str:
    """Convert Bengali digits to ASCII digits."""
    return num_str.translate(EN_DIGITS)


def is_primarily_bangla(text: str) -> bool:
    """Check if text contains primarily Bengali characters."""
    bn_chars = len(re.findall(r"[\u0980-\u09FF]", text))
    en_chars = len(re.findall(r"[a-zA-Z]", text))
    return bn_chars > en_chars


def expand_query_bilingual(query: str) -> str:
    """Augment an English or Bangla query with cross-lingual domain terms and variety patterns.

    If query is in English: finds agricultural concepts and appends Bengali keywords.
    If query is in Bangla: finds agricultural concepts and appends English keywords.

    Args:
        query: Raw user query string.

    Returns:
        Expanded query string with high cross-lingual semantic matching power.
    """
    cleaned = query.strip()
    if not cleaned:
        return query

    matched_expansions: Set[str] = set()

    # 1. Match specific rice variety patterns (e.g. BRRI dhan 28 -> ব্রি ধান২৮)
    # Match "brri dhan 28", "brri dhan28", "brridhan28"
    m_bd = re.search(r"\bbrri\s*dhan\s*(\d+)\b", cleaned, re.IGNORECASE)
    if m_bd:
        v_num = m_bd.group(1)
        bn_num = to_bangla_digits(v_num)
        matched_expansions.add(f"BRRI dhan{v_num}")
        matched_expansions.add(f"ব্রি ধান{bn_num}")
        matched_expansions.add("ধানের জাত")

    # Match "br 24", "br24"
    m_br = re.search(r"\bbr\s*(\d+)\b", cleaned, re.IGNORECASE)
    if m_br:
        v_num = m_br.group(1)
        bn_num = to_bangla_digits(v_num)
        matched_expansions.add(f"BR{v_num}")
        matched_expansions.add(f"বিআর{bn_num}")

    # Match Bengali variety patterns: "ব্রি ধান২৮", "ব্রি ধান ২৮"
    m_bn_bd = re.search(r"ব্রি\s*ধান\s*([০-৯\d]+)", cleaned)
    if m_bn_bd:
        v_num = to_english_digits(m_bn_bd.group(1))
        matched_expansions.add(f"BRRI dhan{v_num}")
        matched_expansions.add(f"BRRI dhan {v_num}")

    if "bangabandhu" in cleaned.lower() or "বঙ্গবন্ধু" in cleaned:
        matched_expansions.add("Bangabandhu dhan100")
        matched_expansions.add("বঙ্গবন্ধু ধান১০০")

    # 2. General vocabulary expansion
    if is_primarily_bangla(cleaned):
        for bn_key, eng_val in BN_TO_ENG_TERMS.items():
            if bn_key in cleaned:
                matched_expansions.add(eng_val)
    else:
        lower_q = cleaned.lower()
        for eng_key in sorted(ENG_TO_BN_TERMS.keys(), key=len, reverse=True):
            pattern = r"\b" + re.escape(eng_key) + r"\b"
            if re.search(pattern, lower_q):
                matched_expansions.add(ENG_TO_BN_TERMS[eng_key])

    if not matched_expansions:
        return cleaned

    expansion_str = " ".join(matched_expansions)
    return f"{cleaned} {expansion_str}"
