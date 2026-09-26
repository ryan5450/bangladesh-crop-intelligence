"""Downloader package providing rate-limited, streaming PDF downloads."""

from .pdf_downloader import PDFDownloader, DownloadResult
from .rate_limiter import DomainRateLimiter

__all__ = ["PDFDownloader", "DownloadResult", "DomainRateLimiter"]

