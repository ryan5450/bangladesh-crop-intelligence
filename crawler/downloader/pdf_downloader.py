"""Resilient streaming PDF downloader with retries and content verification."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import httpx

from config import DEFAULT_TIMEOUT, MAX_FILE_SIZE_BYTES, MAX_RETRIES, MIN_FILE_SIZE_BYTES, STAGING_DIR, USER_AGENT
from downloader.rate_limiter import DomainRateLimiter
from utils.file_helper import ensure_dir
from utils.hasher import hash_file, hash_string
from utils.logger import get_logger

logger = get_logger("downloader")


@dataclass
class DownloadResult:
    """Outcome of a PDF download attempt."""
    success: bool
    url: str
    file_path: Optional[Path] = None
    file_size_bytes: int = 0
    doc_hash: str = ""
    error: Optional[str] = None


class PDFDownloader:
    """Streams and verifies PDF documents from trusted agricultural portals."""

    def __init__(self, staging_dir: Optional[Path] = None):
        self.staging_dir = staging_dir or STAGING_DIR
        ensure_dir(self.staging_dir)
        self.rate_limiter = DomainRateLimiter()
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,application/octet-stream,*/*",
            "Accept-Encoding": "gzip, deflate, br",
        }

    async def download(self, url: str) -> DownloadResult:
        """Asynchronously stream a PDF to a temporary staging file."""
        clean_url = url.strip()
        temp_id = hash_string(clean_url)[:16]
        target_path = self.staging_dir / f"temp_{temp_id}.pdf"

        # Apply domain rate limiting
        await self.rate_limiter.wait_for_domain(clean_url)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    headers=self.headers,
                    timeout=DEFAULT_TIMEOUT,
                    follow_redirects=True,
                    verify=False,  # Government portals often have self-signed SSL chains
                ) as client:
                    async with client.stream("GET", clean_url) as response:
                        if response.status_code != 200:
                            if attempt == MAX_RETRIES:
                                return DownloadResult(
                                    success=False,
                                    url=clean_url,
                                    error=f"HTTP {response.status_code}",
                                )
                            await asyncio.sleep(2 ** attempt)
                            continue

                        # Check advertised content-length
                        content_length = response.headers.get("Content-Length")
                        if content_length and int(content_length) > MAX_FILE_SIZE_BYTES:
                            return DownloadResult(
                                success=False,
                                url=clean_url,
                                error=f"File exceeds max limit ({int(content_length)} bytes)",
                            )

                        # Stream file chunks to staging
                        total_bytes = 0
                        with open(target_path, "wb") as f:
                            async for chunk in response.aiter_bytes(chunk_size=16384):
                                total_bytes += len(chunk)
                                if total_bytes > MAX_FILE_SIZE_BYTES:
                                    target_path.unlink(missing_ok=True)
                                    return DownloadResult(
                                        success=False,
                                        url=clean_url,
                                        error="Stream exceeded maximum allowed file size",
                                    )
                                f.write(chunk)

                        if total_bytes < MIN_FILE_SIZE_BYTES:
                            target_path.unlink(missing_ok=True)
                            return DownloadResult(
                                success=False,
                                url=clean_url,
                                error=f"Downloaded file too small ({total_bytes} bytes), likely an error HTML page",
                            )

                        # Compute file hash
                        file_hash = hash_file(target_path)

                        return DownloadResult(
                            success=True,
                            url=clean_url,
                            file_path=target_path,
                            file_size_bytes=total_bytes,
                            doc_hash=file_hash,
                        )

            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                logger.warning(f"Download attempt {attempt}/{MAX_RETRIES} failed for {clean_url}: {net_err}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                else:
                    target_path.unlink(missing_ok=True)
                    return DownloadResult(success=False, url=clean_url, error=str(net_err))
            except Exception as exc:
                target_path.unlink(missing_ok=True)
                return DownloadResult(success=False, url=clean_url, error=str(exc))

        return DownloadResult(success=False, url=clean_url, error="Exceeded max retries")

