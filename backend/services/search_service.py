"""DuckDuckGo Web Search Service for real-time agricultural information fallback."""

import asyncio
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

WEB_SEARCH_TRIGGERS = {
    "google", "গুগল", "internet", "ইন্টারনেট", "search web", "search the web", "search internet",
    "search online", "ওয়েব সার্চ", "live search", "web search", "latest news", "news",
    "current price", "market price", "দাম কত", "বাজার দর", "বর্তমান দর", "weather",
    "forecast", "আবহাওয়া", "পূর্বাভাস", "recent", "আজকের", "today"
}


class SearchService:
    """Provides on-the-fly web text search via DuckDuckGo when local knowledge is missing."""

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


default_search_service = SearchService()
