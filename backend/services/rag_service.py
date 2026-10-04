"""RAG (Retrieval-Augmented Generation) Orchestration Service for Bangladesh Agriculture."""

import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from vector_store import get_retriever, SearchResult
from vector_store.cross_lingual import is_primarily_bangla
try:
    from services.llm_client import default_llm_client, LLMClient
    from services.search_service import default_search_service
except ImportError:
    from backend.services.llm_client import default_llm_client, LLMClient
    from backend.services.search_service import default_search_service


logger = logging.getLogger(__name__)

# Patterns for detecting greetings, pleasantries, or capability questions
# Patterns for detecting greetings, pleasantries, or capability questions
GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening|howdy)\b",
    r"how are you",
    r"who are you",
    r"what can you do",
    r"what is your name",
    r"(কেমন আছেন|কেমন আছো|হ্যালো|হাই|নমস্কার|সালাম|আসসালামু আলাইকুম|শুভ সকাল|শুভ অপরাহ্ন)",
    r"(আপনি কে|তুমি কে|তোমার কাজ কি|আপনার কাজ কি|আপনি কি করতে পারেন|তোমার নাম কি)",
]

AGRICULTURAL_DOMAIN_TERMS = {
    # English agricultural terms
    "crop", "crops", "rice", "paddy", "wheat", "maize", "corn", "potato", "jute",
    "mustard", "lentil", "pulse", "pulses", "onion", "garlic", "chili", "pepper",
    "tomato", "brinjal", "eggplant", "mango", "banana", "guava", "vegetable", "vegetables",
    "fruit", "fruits", "cereal", "cereals", "variety", "varieties", "cultivar", "hybrid",
    "seed", "seeds", "seedling", "seedlings", "nursery", "seedbed", "sowing", "planting",
    "transplant", "transplanting", "harvest", "harvesting", "yield", "yields", "duration",
    "season", "seasons", "boro", "aman", "aus", "rabi", "kharif",
    "fertilizer", "fertilizers", "urea", "tsp", "mop", "dap", "gypsum", "zinc", "nitrogen",
    "potassium", "phosphorus", "nutrient", "nutrients", "manure", "compost",
    "pesticide", "pesticides", "fungicide", "fungicides", "insecticide", "insecticides",
    "herbicide", "herbicides", "disease", "diseases", "pest", "pests", "insect", "insects",
    "blast", "blight", "rot", "spot", "tungro", "rust", "stem borer", "bph", "planthopper",
    "leaf folder", "leafhopper", "weed", "weeds", "infestation", "symptom", "symptoms",
    "remedy", "control", "treatment", "soil", "saline", "salinity", "irrigation",
    "water", "drainage", "drought", "flood", "submergence", "climate", "weather",
    "farming", "farmer", "farmers", "agriculture", "agricultural", "agronomy", "agronomist",
    "grow", "growing", "plant", "plants", "production",
    "brri", "bari", "dae", "bamis", "fao", "saao", "barc", "bigha", "hectare",
    # Bangla & Banglish agricultural terms (including common transliterations)
    "ধান", "চাল", "গম", "ভুট্টা", "আলু", "পাট", "সরিষা", "ডাল", "মরিচ", "টমেটো",
    "বেগুন", "আম", "কলা", "পেয়ারা", "ফসল", "সবজি", "শাকসবজি", "ফল", "জাত",
    "বীজ", "চারা", "বীজতলা", "রোপণ", "বপন", "ফলন", "জীবনকাল", "মৌসুম", "বোরো",
    "আমন", "আউশ", "রবি", "খরিপ", "সার", "ইউরিয়া", "টিএসপি", "পটাশ", "ডিএপি",
    "জিপসাম", "দস্তা", "জিংক", "কীটনাশক", "ছত্রাকনাশক", "বালাইনাশক", "আগাছানাশক",
    "কীটপতঙ্গ", "বালাই", "রোগ", "পোকা", "মাজরা", "গাছফড়িং", "ব্লাস্ট", "পাতা পোড়া",
    "খোল পোড়া", "বাদামী দাগ", "টুংরো", "মাটি", "লবণাক্ততা", "লবণাক্ত", "সেচ",
    "পানি", "নিষ্কাশন", "খরা", "বন্যা", "জলমগ্নতা", "কৃষি", "কৃষক", "চাষ", "চাষাবাদ",
    "ব্রি", "বিআর", "বারি", "ডিএই", "উপসহকারী", "বিঘা", "হেক্টর",
    # Transliterated phonetic terms
    "সিজন", "ক্রপ", "ক্রপস", "গ্রো", "ফার্টিলাইজার", "ভ্যারাইটি", "সিড", "ফার্মিং",
    "প্রোডাকশন", "ওয়েদার", "টেম্পারেচার", "ডিজিজ", "স্প্রে"
}


def is_conversational_greeting(text: str) -> bool:
    """Check if query is primarily a greeting, pleasantry, or bot capability inquiry."""
    cleaned = text.strip().lower()
    cleaned_no_punct = re.sub(r"[\?\.\!,]", " ", cleaned).strip()
    words = cleaned_no_punct.split()

    if any(w in AGRICULTURAL_DOMAIN_TERMS for w in words):
        return False

    if len(words) <= 5:
        for pat in GREETING_PATTERNS:
            if re.search(pat, cleaned, re.IGNORECASE):
                return True
    return False


def extract_effective_query(query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """If the current query is an elliptical follow-up or translation request, combine with previous context."""
    if not conversation_history:
        return query

    cleaned = query.strip().lower()
    words = cleaned.split()

    follow_up_cues = [
        "হ্যাঁ", "yes", "ইংলিশে", "বাংলায়", "english", "bangla", "translate",
        "বিস্তারিত", "more", "details", "উত্তর দাও", "বলো", "tell me", "explain",
        "why", "কেন", "কীভাবে", "how", "what about", "আর কি", "কোনটি", "what"
    ]
    is_brief_or_follow_up = len(words) <= 6 and any(cue in cleaned for cue in follow_up_cues)

    if is_brief_or_follow_up:
        # Search backwards for the last user message containing substantive question
        for turn in reversed(conversation_history):
            if turn.get("role") == "user" and turn.get("content"):
                prev_text = turn["content"].strip()
                return f"{prev_text} {query}"

    return query


def should_search_knowledge_base(
    query: str,
    category: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> bool:
    """Evaluate whether the user prompt requires agricultural document retrieval."""
    if category and category.strip():
        return True

    # Standalone greeting with no prior conversation history
    if is_conversational_greeting(query) and not conversation_history:
        return False

    effective_text = extract_effective_query(query, conversation_history).lower()

    # Check variety patterns like "brri dhan 28", "br24", "ব্রি ধান২৮"
    if re.search(r"\b(brri|bari|br)\s*dhan\s*\d+", effective_text) or re.search(r"ব্রি\s*ধান\s*[০-৯\d]+", effective_text):
        return True

    words = set(re.findall(r"[\w\u0980-\u09FF]+", effective_text))
    if words & AGRICULTURAL_DOMAIN_TERMS:
        return True

    return False


# ---------------------------------------------------------------------------
# Crop Media & Photo Lookup
# ---------------------------------------------------------------------------
CROP_ALIASES: Dict[str, List[str]] = {
    "Aman Rice": ["aman", "আমন", "আমন ধান", "aman rice", "ropa aman", "রোপা আমন", "dhan", "ধান"],
    "Boro Rice": ["boro", "বোরো", "বোরো ধান", "boro rice"],
    "Aus Rice": ["aus", "আউশ", "আউশ ধান", "aus rice"],
    "Potato": ["potato", "আলু", "alu"],
    "Wheat": ["wheat", "গম", "gom"],
    "Maize": ["maize", "corn", "ভুট্টা", "bhutta"],
    "Tomato": ["tomato", "টমেটো"],
    "Brinjal": ["brinjal", "eggplant", "বেগুন", "begun"],
    "Chili": ["chili", "chilli", "pepper", "মরিচ", "morich"],
    "Onion": ["onion", "পিঁয়াজ", "পেঁয়াজ", "peyaj"],
    "Garlic": ["garlic", "রসুন", "roshun"],
    "Mango": ["mango", "আম", "aam"],
    "Banana": ["banana", "কলা", "kola"],
    "Jackfruit": ["jackfruit", "কাঁঠাল", "kathal"],
    "Guava": ["guava", "পেয়ারা", "peyara"],
    "Litchi": ["litchi", "লিচু", "lichu"],
    "Cauliflower": ["cauliflower", "ফুলকপি", "fulkopi"],
    "Cabbage": ["cabbage", "বাঁধাকপি", "badhakopi"],
    "Cucumber": ["cucumber", "শসা", "shosha"],
    "Pumpkin": ["pumpkin", "মিষ্টি কুমড়া", "kumra"],
    "Jute": ["jute", "পাট", "paat"],
    "Mustard": ["mustard", "সরিষা", "sorisha"],
    "Lentil": ["lentil", "pulse", "মসুর", "mosur", "daal", "ডাল"],
    "Sugarcane": ["sugarcane", "আখ", "aakh"],
    "Turmeric": ["turmeric", "হলুদ", "holud"],
}

PHOTO_INTENT_WORDS = {
    "photo", "photos", "image", "images", "picture", "pictures", "pic", "pics",
    "look", "looks", "see", "show", "appearance", "view",
    "ছবি", "ফটোগ্রাফ", "পিকচার", "দেখাও", "দেখান", "দেখতে", "কেমন"
}

_crop_image_cache: Dict[str, str] = {}
_crop_cache_expiry: float = 0.0

def get_crop_image_map() -> Dict[str, str]:
    """Retrieve mapping of crop_name -> public image_url from Supabase or memory."""
    global _crop_image_cache, _crop_cache_expiry
    import time
    now = time.time()
    if _crop_image_cache and now < _crop_cache_expiry:
        return _crop_image_cache

    try:
        try:
            from supabase_client import supabase
        except ImportError:
            from backend.supabase_client import supabase
        
        res = supabase.table("crops").select("crop_name, image, image_url").execute()
        if res.data:
            cache = {}
            for item in res.data:
                name = item.get("crop_name")
                img = item.get("image_url") or item.get("image")
                if name and img and (img.startswith("http://") or img.startswith("https://")):
                    cache[name] = img
            if cache:
                _crop_image_cache = cache
                _crop_cache_expiry = now + 60.0  # Cache for 60 seconds
                return _crop_image_cache
    except Exception as exc:
        logger.debug(f"Could not load crop images from Supabase: {exc}")

    return _crop_image_cache

def find_crop_and_image(query: str):
    """Detect if query mentions a registered crop and has an official photo available."""
    q = query.lower()
    crop_images = get_crop_image_map()

    # Exact name check
    for crop_name, img_url in crop_images.items():
        if crop_name.lower() in q:
            return crop_name, img_url

    # Alias check
    for crop_name, aliases in CROP_ALIASES.items():
        for alias in aliases:
            pattern = r"(?:\b|^)" + re.escape(alias.lower()) + r"(?:\b|$)"
            if re.search(pattern, q):
                img_url = crop_images.get(crop_name)
                return crop_name, img_url

    return None, None

def is_asking_for_photo(query: str) -> bool:
    """Check if query is asking to see or view a photo/image."""
    q = query.lower()
    words = set(re.findall(r"[\w\u0980-\u09FF]+", q))
    return bool(words & PHOTO_INTENT_WORDS)


SYSTEM_PROMPT = """You are Bangladesh Crop Intelligence Assistant (বাংলাদেশ কৃষি বুদ্ধিমত্তা সহকারী), an official AI agricultural expert built to assist farmers, agronomists, extension officers, and researchers in Bangladesh.

BANGLADESH AGRONOMIC SEASONS & CALENDAR:
- Rabi (রবি) Season (Mid-October to Mid-March / কার্তিক-ফাল্গুন):
  Main crops: Boro rice (বোরো ধান), Wheat (গম), Maize (ভুট্টা), Mustard (সরিষা), Potato (আলু), Lentils/Pulses (মসুর, মুগ), Winter vegetables (ফুলকপি, বাঁধাকপি, মুলা, টমেটো, বেগুন, শিম, গাজর, লালশাক, পালংশাক).
- Kharif-1 (খরিপ-১) Season (Mid-March to Mid-July / চৈত্র-আষাঢ়):
  Main crops: Aus rice (আউশ ধান), Jute (পাট), Summer vegetables (ঝিঙ্গা, পটল, করলা, ঢেঁড়শ, চিচিঙ্গা).
- Kharif-2 (খরিপ-২) Season (Mid-July to Mid-October / শ্রাবণ-আশ্বিন):
  Main crops: Transplanted Aman rice (রোপা আমন ধান), Late summer vegetables.
- Current Season (September / October):
  Transition period from Late Kharif-2 into early Rabi season. Aman rice is standing in the field (tillering/flowering). Farmers are preparing land and sowing early Rabi crops (early winter vegetables, mustard, early potato).

CORE RULES & BEHAVIOR:
1. LANGUAGE ADAPTABILITY (PRIORITY #1):
   - If the user asks in English OR asks for an English reply (e.g. "in English", "ইংলিশে লেখো", "ইংলিশে উত্তর দাও"), you MUST reply in clear, accurate English.
   - If the user asks in Bangla OR asks for a Bangla reply (e.g. "বাংলায় লেখো", "বাংলায় বলো"), you MUST reply in natural, polite Bangla (প্রমিত ও কৃষিবান্ধব বাংলা).
   - If the user uses Banglish (Bangla in English alphabet), respond in clear Bangla or English.
   - Do NOT restrict your language based on the UI buttons. Always follow what the user actually asks for in the message.

2. CONVERSATIONAL CONTINUITY:
   - Always remember the previous conversation turns.
   - If the user says "Yes", "হ্যাঁ", "Tell me more", "Answer this in English", or asks a follow-up, refer to the previous discussion and directly provide what they requested.

3. CONCISENESS & QUALITY:
   - Provide direct, structured, bulleted advice with exact practical numbers (seed rates, fertilizer doses in kg/bigha, durations).
   - NEVER echo or repeat the user's prompt back to them.
   - NEVER repeat greeting boilerplate in the middle of a discussion. Only introduce yourself if the user explicitly greets you initially (e.g. "hello", "hi").
   - If official context is provided under "Official Knowledge Context", use it and cite the source [BRRI], [DAE], or [BARI]. If not present, answer accurately using the agronomic knowledge above.

4. WEB SEARCH & LIVE INFORMATION (DUCKDUCKGO):
   - When live web search results from DuckDuckGo are provided under "Live Web Information", integrate the up-to-date facts smoothly and reference the sources.
"""


class SourceCitation(BaseModel):
    """Citation metadata for retrieved agricultural documents."""
    source: str
    category: str
    page_number: int
    language: str
    document_id: str
    chunk_id: str
    relevance_score: float
    citation_text: str


class AssistantChatResponse(BaseModel):
    """Complete assistant response payload."""
    answer: str
    sources: List[SourceCitation]
    detected_language: str
    model: str
    image_url: Optional[str] = None
    crop_name: Optional[str] = None


def format_fast_context(results: List[SearchResult], max_chars_per_chunk: int = 350) -> str:
    """Format lean context snippets to minimize prompt parsing time and speed up generation."""
    if not results:
        return "No relevant agricultural documents found."
    lines = []
    for i, r in enumerate(results, 1):
        clean_text = " ".join(r.text.split())
        if len(clean_text) > max_chars_per_chunk:
            clean_text = clean_text[:max_chars_per_chunk] + "..."
        lines.append(f"[{i}] {r.citation()}: {clean_text}")
    return "\n".join(lines)


class RAGService:
    """Orchestrator retrieving semantic context and generating answers via LLM."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.retriever = get_retriever()
        self.llm = llm_client or default_llm_client

    async def answer_question(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 3,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AssistantChatResponse:
        """Process user query, evaluate need for search, and synthesize with LLM."""
        user_is_bangla = is_primarily_bangla(query)
        detected_lang = "Bangla" if user_is_bangla else "English"
        needs_search = should_search_knowledge_base(query, category, conversation_history)

        search_results: List[SearchResult] = []
        citations: List[SourceCitation] = []
        context_block = ""

        # 2. Only query vector database if evaluated as an agricultural query
        if needs_search:
            search_query = extract_effective_query(query, conversation_history)
            raw_results = self.retriever.search(
                query=search_query,
                top_k=top_k,
                category=category,
                expand_bilingual=True
            )
            # Only retain high-confidence passages (relevance >= 0.40)
            search_results = [r for r in raw_results if r.relevance_score >= 0.40]

            if search_results:
                context_block = format_fast_context(search_results, max_chars_per_chunk=350)
                citations = [
                    SourceCitation(
                        source=r.source,
                        category=r.category,
                        page_number=r.page_number,
                        language=r.language,
                        document_id=r.document_id,
                        chunk_id=r.chunk_id,
                        relevance_score=r.relevance_score,
                        citation_text=r.citation()
                    )
                    for r in search_results
                ]

        # DuckDuckGo Web Search is triggered ONLY IF:
        # 1. The user explicitly requests live web / internet / weather / current market price info, OR
        # 2. Local vector database retrieval returns no high-confidence results (the AI assistant doesn't know)
        web_context_block = ""
        is_web_query = default_search_service.is_explicit_web_search(query)
        ai_assistant_doesnt_know = needs_search and not search_results

        if is_web_query or ai_assistant_doesnt_know:
            web_results = await default_search_service.search_web_text(query, max_results=3)
            if web_results:
                web_context_block = "Live Web Information (DuckDuckGo Search):\n" + "\n".join([
                    f"- {w['title']}: {w['body']} (Link: {w['href']})"
                    for w in web_results
                ])
                for w in web_results:
                    citations.append(
                        SourceCitation(
                            source="DuckDuckGo Web Search",
                            category="live_web",
                            page_number=0,
                            language="en",
                            document_id=w["href"],
                            chunk_id=w["href"],
                            relevance_score=0.85,
                            citation_text=f"{w['title']}"
                        )
                    )

        # 3. Construct messages payload with up to 8 past turns for rich conversational memory
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for turn in conversation_history[-8:]:
                if turn.get("role") in ("user", "assistant") and turn.get("content"):
                    messages.append({"role": turn["role"], "content": turn["content"]})

        # Provide context if found; otherwise send the user query directly to let LLM decide
        context_parts = []
        if search_results and context_block:
            context_parts.append(f"Official Knowledge Context:\n{context_block}")
        if web_context_block:
            context_parts.append(web_context_block)

        if context_parts:
            prompt_content = "\n\n".join(context_parts) + f"\n\nUser Question: {query}"
        else:
            prompt_content = query

        messages.append({"role": "user", "content": prompt_content})

        # 4. Generate completion from LLM
        answer = await self.llm.chat(messages=messages, temperature=0.2, max_tokens=450)

        return AssistantChatResponse(
            answer=answer,
            sources=citations,
            detected_language=detected_lang,
            model=self.llm.model
        )

    async def stream_answer_question(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 3,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """Process user query, retrieve verified agricultural context if needed, and stream answer chunks."""
        user_is_bangla = is_primarily_bangla(query)
        detected_lang = "Bangla" if user_is_bangla else "English"
        needs_search = should_search_knowledge_base(query, category, conversation_history)

        search_results: List[SearchResult] = []
        context_block = ""

        # 2. Only query vector database if evaluated as an agricultural domain query
        if needs_search:
            search_query = extract_effective_query(query, conversation_history)
            raw_results = self.retriever.search(
                query=search_query,
                top_k=top_k,
                category=category,
                expand_bilingual=True
            )
            search_results = [r for r in raw_results if r.relevance_score >= 0.40]
            if search_results:
                context_block = format_fast_context(search_results, max_chars_per_chunk=350)

        # 3. Build citations list (only for relevant results)
        citations = [
            {
                "source": r.source,
                "category": r.category,
                "page_number": r.page_number,
                "language": r.language,
                "document_id": r.document_id,
                "chunk_id": r.chunk_id,
                "relevance_score": r.relevance_score,
                "citation_text": r.citation()
            }
            for r in search_results
        ]

        # DuckDuckGo Web Search is triggered ONLY IF:
        # 1. The user explicitly requests live web / internet / weather / current market price info, OR
        # 2. Local vector database retrieval returns no high-confidence results (the AI assistant doesn't know)
        web_context_block = ""
        is_web_query = default_search_service.is_explicit_web_search(query)
        ai_assistant_doesnt_know = needs_search and not search_results

        if is_web_query or ai_assistant_doesnt_know:
            web_results = await default_search_service.search_web_text(query, max_results=3)
            if web_results:
                web_context_block = "Live Web Information (DuckDuckGo Search):\n" + "\n".join([
                    f"- {w['title']}: {w['body']} (Link: {w['href']})"
                    for w in web_results
                ])
                for w in web_results:
                    citations.append({
                        "source": "DuckDuckGo Web Search",
                        "category": "live_web",
                        "page_number": 0,
                        "language": "en",
                        "document_id": w["href"],
                        "chunk_id": w["href"],
                        "relevance_score": 0.85,
                        "citation_text": f"{w['title']}"
                    })

        # First event: metadata (sources, detected language, model)
        yield {
            "type": "metadata",
            "sources": citations,
            "detected_language": detected_lang,
            "model": self.llm.model
        }

        # 4. Construct messages with up to 8 past turns for rich conversational memory
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for turn in conversation_history[-8:]:
                if turn.get("role") in ("user", "assistant") and turn.get("content"):
                    messages.append({"role": turn["role"], "content": turn["content"]})

        # Provide context if found; otherwise send the user query directly
        context_parts = []
        if search_results and context_block:
            context_parts.append(f"Official Knowledge Context:\n{context_block}")
        if web_context_block:
            context_parts.append(web_context_block)

        if context_parts:
            prompt_content = "\n\n".join(context_parts) + f"\n\nUser Question: {query}"
        else:
            prompt_content = query

        messages.append({"role": "user", "content": prompt_content})

        # 5. Stream tokens from LLM
        async for delta in self.llm.stream_chat(messages=messages, temperature=0.2, max_tokens=450):
            yield {
                "type": "delta",
                "content": delta
            }

        # Final event: done
        yield {"type": "done"}


default_rag_service = RAGService()

