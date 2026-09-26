"""Bilingual dictionaries for Bangladesh crop taxonomy and 24 agronomic categories."""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Crop Entity Taxonomy (English & Bengali aliases and category mapping)
# ---------------------------------------------------------------------------
CROP_TAXONOMY: Dict[str, Dict[str, any]] = {
    "Rice": {
        "category": "cereals",
        "aliases": ["rice", "paddy", "oryza sativa", "ধান", "ধানের", "চাল"],
        "sub_types": ["Boro Rice", "Aman Rice", "Aus Rice"],
    },
    "Boro Rice": {
        "category": "cereals",
        "aliases": ["boro", "boro rice", "বোরো", "বোরো ধান", "বোরো ধানের"],
    },
    "Aman Rice": {
        "category": "cereals",
        "aliases": ["aman", "aman rice", "t.aman", "রোপা আমন", "আমন", "আমন ধান"],
    },
    "Aus Rice": {
        "category": "cereals",
        "aliases": ["aus", "aus rice", "আউশ", "আউশ ধান"],
    },
    "Wheat": {
        "category": "cereals",
        "aliases": ["wheat", "triticum aestivum", "গম", "গমের"],
    },
    "Maize": {
        "category": "cereals",
        "aliases": ["maize", "corn", "zea mays", "ভুট্টা", "ভুট্টার"],
    },
    "Jute": {
        "category": "fiber_crops",
        "aliases": ["jute", "corchorus", "golden fibre", "পাট", "পাটের", "তোষা পাট", "দেশী পাট"],
    },
    "Cotton": {
        "category": "fiber_crops",
        "aliases": ["cotton", "gossypium", "তুলা", "তুলার"],
    },
    "Potato": {
        "category": "vegetables",
        "aliases": ["potato", "solanum tuberosum", "আলু", "আলুর", "গোল আলু"],
    },
    "Brinjal": {
        "category": "vegetables",
        "aliases": ["brinjal", "eggplant", "aubergine", "solanum melongena", "বেগুন", "বেগুনের"],
    },
    "Tomato": {
        "category": "vegetables",
        "aliases": ["tomato", "solanum lycopersicum", "টমেটো", "টমেটোর"],
    },
    "Cabbage": {
        "category": "vegetables",
        "aliases": ["cabbage", "brassica oleracea", "বাঁধাকপি", "বাঁধাকপির"],
    },
    "Cauliflower": {
        "category": "vegetables",
        "aliases": ["cauliflower", "ফুলকপি", "ফুলকপির"],
    },
    "Chili": {
        "category": "spices",
        "aliases": ["chili", "chilli", "pepper", "capsicum", "মরিচ", "মরিচের", "লঙ্কা"],
    },
    "Onion": {
        "category": "spices",
        "aliases": ["onion", "allium cepa", "পেঁয়াজ", "পেঁয়াজের"],
    },
    "Garlic": {
        "category": "spices",
        "aliases": ["garlic", "allium sativum", "রসুন", "রসুনের"],
    },
    "Turmeric": {
        "category": "spices",
        "aliases": ["turmeric", "curcuma longa", "হলুদ", "হলুদের"],
    },
    "Ginger": {
        "category": "spices",
        "aliases": ["ginger", "zingiber officinale", "আদা", "আদার"],
    },
    "Mango": {
        "category": "fruits",
        "aliases": ["mango", "mangifera indica", "আম", "আমের", "আমবাগান"],
    },
    "Jackfruit": {
        "category": "fruits",
        "aliases": ["jackfruit", "artocarpus heterophyllus", "কাঁঠাল", "কাঁঠালের"],
    },
    "Banana": {
        "category": "fruits",
        "aliases": ["banana", "musa", "কলা", "কলার"],
    },
    "Guava": {
        "category": "fruits",
        "aliases": ["guava", "psidium guajava", "পেয়ারা", "পেয়ারার"],
    },
    "Litchi": {
        "category": "fruits",
        "aliases": ["litchi", "lychee", "litchi chinensis", "লিচু", "লিচুর"],
    },
    "Lentil": {
        "category": "pulses",
        "aliases": ["lentil", "lens culinaris", "masur", "মসুর", "মসুরের"],
    },
    "Chickpea": {
        "category": "pulses",
        "aliases": ["chickpea", "gram", "ছোলা", "ছোলার"],
    },
    "Mungbean": {
        "category": "pulses",
        "aliases": ["mungbean", "mung bean", "মুগ", "মুগডাল"],
    },
    "Mustard": {
        "category": "oil_crops",
        "aliases": ["mustard", "rapeseed", "brassica juncea", "সরিষা", "সরিষার", "রাই"],
    },
    "Soybean": {
        "category": "oil_crops",
        "aliases": ["soybean", "soya", "সয়াবিন", "সয়াবিনের"],
    },
    "Sunflower": {
        "category": "oil_crops",
        "aliases": ["sunflower", "helianthus", "সূর্যমুখী", "সূর্যমুখীর"],
    },
    "Sugarcane": {
        "category": "cash_crops",
        "aliases": ["sugarcane", "saccharum officinarum", "আখ", "আখের", "কুশিয়ার"],
    },
    "Tea": {
        "category": "cash_crops",
        "aliases": ["tea", "camellia sinensis", "চা", "চা বাগান", "চায়ের"],
    },
}


# ---------------------------------------------------------------------------
# Agronomic Category Keyword Vectors (24 Categories)
# ---------------------------------------------------------------------------
TOPIC_TAXONOMY: Dict[str, Dict[str, any]] = {
    "cereals": {
        "keywords": ["cereal", "grain", "rice", "wheat", "maize", "paddy", "দানাশস্য", "ধান", "গম", "ভুট্টা"],
        "weight": 1.2,
    },
    "fruits": {
        "keywords": ["fruit", "orchard", "mango", "banana", "jackfruit", "guava", "litchi", "ফল", "আম", "কলা", "কাঁঠাল"],
        "weight": 1.2,
    },
    "vegetables": {
        "keywords": ["vegetable", "tuber", "potato", "tomato", "brinjal", "cabbage", "সবজি", "শাকসবজি", "আলু", "বেগুন"],
        "weight": 1.2,
    },
    "pulses": {
        "keywords": ["pulse", "legume", "lentil", "chickpea", "mungbean", "ডাল", "মসুর", "ছোলা", "মুগ"],
        "weight": 1.2,
    },
    "oil_crops": {
        "keywords": ["oilseed", "oil crop", "mustard", "soybean", "sunflower", "sesame", "তৈলবীজ", "সরিষা", "তিল"],
        "weight": 1.2,
    },
    "fiber_crops": {
        "keywords": ["fiber", "fibre", "jute", "cotton", "kenaf", "আঁশ", "পাট", "তুলা"],
        "weight": 1.2,
    },
    "spices": {
        "keywords": ["spice", "chili", "onion", "garlic", "turmeric", "ginger", "মসলা", "মরিচ", "পেঁয়াজ", "রসুন", "হলুদ"],
        "weight": 1.2,
    },
    "cash_crops": {
        "keywords": ["cash crop", "commercial crop", "sugarcane", "tea", "tobacco", "অর্থকরী ফসল", "আখ", "চা"],
        "weight": 1.1,
    },
    "crops": {
        "keywords": ["crop", "botanical", "taxonomy", "variety", "agriculture", "ফসল", "জাত", "কৃষি"],
        "weight": 0.8,
    },
    "cultivation_methods": {
        "keywords": ["cultivation", "agronomy", "transplanting", "sowing", "seedbed", "sri", "dsr", "চাষ পদ্ধতি", "বপন", "রোপণ", "চারা"],
        "weight": 1.3,
    },
    "crop_calendar": {
        "keywords": ["calendar", "season", "rabi", "kharif", "kharif-1", "kharif-2", "planting time", "মৌসুম", "রবি", "খরিফ", "দিনপঞ্জিকা"],
        "weight": 1.3,
    },
    "soil_management": {
        "keywords": ["soil", "salinity", "acidity", "ph", "organic matter", "fertility", "texture", "loam", "মাটি", "মাটির স্বাস্থ্য", "লবণাক্ততা"],
        "weight": 1.3,
    },
    "fertilizer_management": {
        "keywords": ["fertilizer", "urea", "tsp", "mop", "dap", "gypsum", "zinc", "nitrogen", "npk", "সার", "ইউরিয়া", "টিএসপি", "পটাশ", "সুষম সার"],
        "weight": 1.4,
    },
    "irrigation_management": {
        "keywords": ["irrigation", "water management", "awd", "alternate wetting and drying", "drainage", "water requirement", "সেচ", "পরিমিত সেচ", "পানি ব্যবস্থাপনা"],
        "weight": 1.4,
    },
    "pest_management": {
        "keywords": ["pest", "insect", "stem borer", "planthopper", "armyworm", "ipm", "pesticide", "কীটপতঙ্গ", "মাজরা পোকা", "কারেন্ট পোকা", "বালাই ব্যবস্থাপনা"],
        "weight": 1.4,
    },
    "diseases": {
        "keywords": ["disease", "pathogen", "fungus", "bacterial", "blast", "blight", "rot", "canker", "wilt", "রোগ", "ব্লাস্ট", "ঝলসানো", "পচন", "ধ্বসা"],
        "weight": 1.4,
    },
    "weed_management": {
        "keywords": ["weed", "herbicide", "weeding", "unwanted plant", "আগাছা", "আগাছানাশক", "নিড়ানি"],
        "weight": 1.3,
    },
    "seed_management": {
        "keywords": ["seed", "germination", "seed preservation", "certified seed", "viability", "বীজ", "অঙ্কুরোদগম", "বীজ সংরক্ষণ", "বীজ শোধন"],
        "weight": 1.3,
    },
    "greenhouse": {
        "keywords": ["greenhouse", "polyhouse", "net house", "protected cultivation", "controlled environment", "গ্রিনহাউস", "পলিহাউস"],
        "weight": 1.2,
    },
    "organic_farming": {
        "keywords": ["organic", "compost", "vermicompost", "biofertilizer", "green manure", "জৈব কৃষি", "কেঁচো সার", "কম্পোস্ট", "সবুজ সার"],
        "weight": 1.3,
    },
    "climate_adaptation": {
        "keywords": ["climate", "adaptation", "drought", "submergence", "saline", "scuba rice", "flood", "cyclone", "জলবায়ু সহনশীল", "খরা", "বন্যা", "লবণাক্ততা সহনশীল"],
        "weight": 1.4,
    },
    "harvesting": {
        "keywords": ["harvest", "reaping", "combine harvester", "cutting", "maturity", "ফসল কর্তন", "মাড়াই", "পাকা ফসল"],
        "weight": 1.2,
    },
    "storage": {
        "keywords": ["storage", "silo", "warehouse", "cold storage", "hermetic", "সংরক্ষণ", "গুদামজাতকরণ", "হিমাগার"],
        "weight": 1.3,
    },
    "post_harvest": {
        "keywords": ["post harvest", "processing", "milling", "drying", "parboiling", "loss reduction", "value addition", "পোস্ট হারভেস্ট", "প্রক্রিয়াজাতকরণ", "শুকানো"],
        "weight": 1.3,
    },
}

