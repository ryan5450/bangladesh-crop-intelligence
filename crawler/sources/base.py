"""Base class and common models for trusted agricultural source scrapers."""

import abc
from dataclasses import dataclass
from typing import List, Optional, Set, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import httpx

from config import DEFAULT_TIMEOUT, USER_AGENT
from utils.file_helper import clean_title
from utils.hasher import normalize_url
from utils.logger import get_logger

logger = get_logger("sources.base")


@dataclass
class CandidateDocument:
    """Discovered candidate document prior to download and validation."""
    url: str
    title: str
    source: str
    category_hint: str = ""


class BaseSourceCrawler(abc.ABC):
    """Abstract base class for scraping documents from government and research portals."""

    def __init__(
        self,
        source_key: str,
        base_urls: Optional[Union[List[str], str]] = None,
        base_url: Optional[str] = None,
    ):
        self.source_key = source_key
        raw_urls = base_urls or base_url or []
        if isinstance(raw_urls, str):
            self.base_urls = [raw_urls]
        else:
            self.base_urls = list(raw_urls)

        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def scrape_portal_links(self, target_url: str) -> List[CandidateDocument]:
        """Fetch a portal webpage and extract all PDF download links and publication detail pages."""
        candidates: List[CandidateDocument] = []
        seen_urls: Set[str] = set()
        detail_urls: List[str] = []

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=DEFAULT_TIMEOUT,
                follow_redirects=True,
                verify=False,
            ) as client:
                resp = await client.get(target_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_key}] Received status {resp.status_code} from {target_url}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")

                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"].strip()
                    if not href or href.startswith("javascript:") or href.startswith("#"):
                        continue

                    full_url = urljoin(target_url, href)
                    clean_full = normalize_url(full_url)
                    url_lower = clean_full.lower()

                    # Match direct PDFs
                    if url_lower.endswith(".pdf") or ("/office-" in url_lower and url_lower.endswith(".pdf")):
                        if clean_full not in seen_urls:
                            seen_urls.add(clean_full)
                            link_text = a_tag.get_text(strip=True)
                            raw_title = link_text if len(link_text) > 3 else clean_full.split("/")[-1]
                            candidates.append(
                                CandidateDocument(
                                    url=clean_full,
                                    title=clean_title(raw_title),
                                    source=self.source_key,
                                )
                            )
                    # Check for publication detail pages
                    elif (
                        "/pages/publications/" in clean_full
                        or "/pages/annual-reports/" in clean_full
                    ):
                        if clean_full not in detail_urls and clean_full != target_url:
                            detail_urls.append(clean_full)

                # Follow detail pages to extract official titles and PDF download links
                for d_url in detail_urls[:10]:
                    try:
                        d_resp = await client.get(d_url)
                        if d_resp.status_code != 200:
                            continue
                        d_soup = BeautifulSoup(d_resp.text, "html.parser")

                        page_title = ""
                        if d_soup.title and d_soup.title.string:
                            page_title = d_soup.title.string.split("|")[0].strip()
                        if not page_title:
                            h1 = d_soup.find("h1")
                            if h1:
                                page_title = h1.get_text(strip=True)

                        for da in d_soup.find_all("a", href=True):
                            d_href = da["href"].strip()
                            pdf_candidate = urljoin(d_url, d_href)
                            clean_pdf = normalize_url(pdf_candidate)
                            pdf_lower = clean_pdf.lower()

                            if (
                                pdf_lower.endswith(".pdf")
                                or ("objectstorage" in pdf_lower and pdf_lower.endswith(".pdf"))
                            ):
                                if clean_pdf not in seen_urls:
                                    seen_urls.add(clean_pdf)
                                    doc_title = clean_title(page_title or clean_pdf.split("/")[-1])
                                    candidates.append(
                                        CandidateDocument(
                                            url=clean_pdf,
                                            title=doc_title,
                                            source=self.source_key,
                                        )
                                    )
                                    break
                    except Exception as detail_err:
                        logger.debug(f"Failed to scrape detail page {d_url}: {detail_err}")

        except Exception as exc:
            logger.warning(f"[{self.source_key}] Error scraping portal {target_url}: {exc}")

        return candidates

    @abc.abstractmethod
    def get_curated_seeds(self) -> List[CandidateDocument]:
        """Return authoritative, verified seed publications known for this institution."""
        pass

    async def discover(self) -> List[CandidateDocument]:
        """Combine scraped portal links and authoritative seed documents."""
        # 1. Start with curated seed documents
        results: List[CandidateDocument] = list(self.get_curated_seeds())
        seen_urls = {normalize_url(doc.url) for doc in results}

        # 2. Scrape all configured live portal publications pages
        for base_url in self.base_urls:
            scraped = await self.scrape_portal_links(base_url)
            for doc in scraped:
                clean = normalize_url(doc.url)
                if clean not in seen_urls:
                    seen_urls.add(clean)
                    results.append(doc)

        logger.info(f"[{self.source_key}] Total {len(results)} candidate publications ready for ingestion.")
        return results
