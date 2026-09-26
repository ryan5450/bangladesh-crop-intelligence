"""Web and portal search engine for discovering agricultural PDFs."""

import asyncio
import re
from typing import List, Set
from urllib.parse import parse_qs, unquote, urlparse
from bs4 import BeautifulSoup
import httpx

from config import DEFAULT_TIMEOUT, USER_AGENT
from utils.logger import get_logger

logger = get_logger("search.engine")


class DocumentSearchEngine:
    """Searches for agricultural publications across government domains."""

    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def search_duckduckgo(self, query: str, max_results: int = 15) -> List[str]:
        """Query DuckDuckGo HTML search for PDF document URLs."""
        pdf_urls: Set[str] = set()
        endpoint = "https://html.duckduckgo.com/html/"
        data = {"q": query, "b": ""}

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
                resp = await client.post(endpoint, data=data)
                if resp.status_code != 200:
                    logger.warning(f"Search query returned status {resp.status_code} for '{query}'")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                links = soup.find_all("a", class_="result__url") + soup.find_all("a", class_="result__snippet")

                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    # Extract target URL from DuckDuckGo redirect wrapper (/l/?kh=-1&uddg=...)
                    if "/l/?kh=" in href or "uddg=" in href:
                        parsed = urlparse(href)
                        qs = parse_qs(parsed.query)
                        if "uddg" in qs:
                            href = unquote(qs["uddg"][0])

                    # Verify if it points to a PDF
                    clean_href = href.split("?")[0].lower()
                    if clean_href.endswith(".pdf") or "/files/" in href.lower() or "download" in href.lower():
                        if href.startswith("http"):
                            pdf_urls.add(href)
                            if len(pdf_urls) >= max_results:
                                break

        except Exception as exc:
            logger.warning(f"Error querying search engine for '{query}': {exc}")

        return list(pdf_urls)

    async def discover_for_source(self, source_key: str, queries: List[str], max_per_query: int = 10) -> List[str]:
        """Run multiple queries for a source and aggregate discovered PDF URLs."""
        all_urls: Set[str] = set()

        for q in queries:
            logger.info(f"[SEARCHING] Query: {q}")
            results = await self.search_duckduckgo(q, max_results=max_per_query)
            all_urls.update(results)
            await asyncio.sleep(1.0)  # Politeness delay

        logger.info(f"Source [{source_key}] discovered {len(all_urls)} candidate document URLs.")
        return list(all_urls)

