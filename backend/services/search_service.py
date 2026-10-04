import asyncio
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Fallback seasonal crops to query when the user asks generically for "more crops" or "other crops"
POPULAR_BANGLADESH_CROPS = [
    {
        "name": "Mustard (সরিষা)",
        "query": "Mustard crop field Bangladesh",
        "fallback_image": "https://img.freepik.com/premium-photo/field-mustard-bangladesh_659722-4860.jpg?w=2000"
    },
    {
        "name": "Potato (আলু)",
        "query": "Potato crop harvest Bangladesh",
        "fallback_image": "https://c8.alamy.com/comp/2J0JFHR/farmers-are-busy-harvesting-potatoes-from-the-crop-field-at-sirajdikhan-munshiganj-district-in-bangladesh-2J0JFHR.jpg"
    },
    {
        "name": "Wheat (গম)",
        "query": "Wheat crop field Bangladesh",
        "fallback_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Wheat_P1090485.jpg/800px-Wheat_P1090485.jpg"
    },
    {
        "name": "Boro Rice (বোরো ধান)",
        "query": "Boro rice field seedlings Bangladesh",
        "fallback_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Rice_fields_in_Bangladesh_02.jpg/800px-Rice_fields_in_Bangladesh_02.jpg"
    },
    {
        "name": "Maize (ভুট্টা)",
        "query": "Maize corn field Bangladesh",
        "fallback_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Corn_field_Bangladesh.jpg/800px-Corn_field_Bangladesh.jpg"
    },
]

WEB_SEARCH_TRIGGERS = {
    "google", "গুগল", "internet", "ইন্টারনেট", "search web", "search the web", "search internet",
    "search online", "ওয়েব সার্চ", "live search", "web search", "latest news", "news",
    "current price", "market price", "দাম কত", "বাজার দর", "বর্তমান দর", "weather",
    "forecast", "আবহাওয়া", "পূর্বাভাস", "recent", "আজকের", "today"
}


class SearchService:
    """Provides on-the-fly, zero-database Web and Image search via DuckDuckGo."""

    def __init__(self):
        self.enabled = True

    def is_explicit_web_search(self, query: str) -> bool:
        """Check if user query explicitly asks for web search or real-time info."""
        q = query.lower()
        return any(trigger in q for trigger in WEB_SEARCH_TRIGGERS)

    async def search_web_text(
        self,
        query: str,
        max_results: int = 3,
        timeout_seconds: float = 6.0
    ) -> List[Dict[str, str]]:
        """Run a non-blocking web text search. Returns list of {title, href, body}."""
        if not self.enabled:
            return []

        def _do_text_search():
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                # Add agricultural geographic focus if not specified
                effective_query = query
                if not any(k in query.lower() for k in ["bangladesh", "বাংলাদেশ", "brri", "bari", "dae"]):
                    effective_query = f"{query} Bangladesh agriculture"
                return list(ddgs.text(effective_query, max_results=max_results))

        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(_do_text_search),
                timeout=timeout_seconds
            )
            clean_results = []
            for r in results:
                title = r.get("title") or ""
                href = r.get("href") or ""
                body = r.get("body") or ""
                if href and (title or body):
                    clean_results.append({
                        "title": title.strip(),
                        "href": href.strip(),
                        "body": body.strip()
                    })
            return clean_results
        except Exception as exc:
            logger.warning(f"DuckDuckGo web text search failed or timed out: {exc}")
            return []

    async def search_web_images(
        self,
        query: str,
        max_results: int = 2,
        timeout_seconds: float = 6.0
    ) -> List[Dict[str, str]]:
        """Run a non-blocking web image search. Returns list of {title, image, thumbnail, source}."""
        if not self.enabled:
            return []

        def _do_image_search():
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                effective_query = query
                if not any(k in query.lower() for k in ["bangladesh", "বাংলাদেশ"]):
                    effective_query = f"{query} Bangladesh"
                return list(ddgs.images(effective_query, max_results=max_results))

        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(_do_image_search),
                timeout=timeout_seconds
            )
            clean_images = []
            for r in results:
                img_url = r.get("image") or ""
                if img_url and (img_url.startswith("http://") or img_url.startswith("https://")):
                    clean_images.append({
                        "title": (r.get("title") or "Crop Photo").strip(),
                        "image": img_url.strip(),
                        "thumbnail": r.get("thumbnail") or img_url,
                        "source": r.get("source") or "web"
                    })
            return clean_images
        except Exception as exc:
            logger.warning(f"DuckDuckGo image search failed or timed out for '{query}': {exc}")
            return []

    async def get_crop_photos(
        self,
        query: str,
        detected_crop: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Retrieve photos for a specific crop or multiple crops if generically requested."""
        q = query.lower()
        photos = []

        # Case 1: Specific crop detected
        if detected_crop:
            img_url = None
            try:
                res = await self.search_web_images(f"{detected_crop} crop field Bangladesh", max_results=1)
                if res:
                    img_url = res[0]["image"]
            except Exception:
                pass
            if not img_url:
                for target in POPULAR_BANGLADESH_CROPS:
                    if detected_crop.lower() in target["name"].lower():
                        img_url = target.get("fallback_image")
                        break
            if img_url:
                photos.append({
                    "crop_name": detected_crop,
                    "title": detected_crop,
                    "image_url": img_url
                })
            return photos

        # Case 2: User asking for generic "more crops", "other crops", "different crops", "বিভিন্ন ফসল"
        is_asking_more = any(phrase in q for phrase in [
            "more crops", "other crops", "all crops", "different crops", "another crop",
            "more crop", "আরও ফসল", "অন্যান্য ফসল", "বিভিন্ন ফসল", "আর কোনো ফসল", "অন্য ফসল"
        ])

        if is_asking_more:
            # Pick 2 key complementary crops to retrieve
            targets = POPULAR_BANGLADESH_CROPS[:2]
            for target in targets:
                img_url = None
                try:
                    res = await self.search_web_images(target["query"], max_results=1)
                    if res:
                        img_url = res[0]["image"]
                except Exception:
                    pass
                if not img_url:
                    img_url = target.get("fallback_image")
                if img_url:
                    photos.append({
                        "crop_name": target["name"],
                        "title": target["name"],
                        "image_url": img_url
                    })
            return photos

        # Case 3: Generic photo query without specific crop name (e.g. "show me photos")
        try:
            res = await self.search_web_images(f"{query} Bangladesh agriculture", max_results=2)
            for r in res:
                photos.append({
                    "crop_name": r["title"][:40],
                    "title": r["title"],
                    "image_url": r["image"]
                })
        except Exception:
            pass

        if not photos:
            for target in POPULAR_BANGLADESH_CROPS[:2]:
                photos.append({
                    "crop_name": target["name"],
                    "title": target["name"],
                    "image_url": target["fallback_image"]
                })

        return photos


default_search_service = SearchService()
