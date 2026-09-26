"""Bangladesh Agriculture Knowledge Crawler & ETL Data Pipeline.

Autonomous ingestion, validation, extraction, classification, canonical renaming,
and metadata indexing for future RAG systems.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Ensure crawler package is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from classifier.document_classifier import classify_document
from config import CATEGORIES, MIN_EXTRACTED_TEXT_LENGTH, TRUSTED_SOURCES
from downloader.pdf_downloader import PDFDownloader
from metadata.catalog import CatalogManager
from metadata.generator import generate_document_metadata
from processor.language_detector import detect_language
from processor.text_extractor import extract_pdf_content
from processor.validator import remove_corrupt_file, validate_pdf
from search.query_builder import AgriculturalQueryBuilder
from search.search_engine import DocumentSearchEngine
from sources.bamis import BAMISCrawler
from sources.barc import BARCCrawler
from sources.bari import BARICrawler
from sources.base import BaseSourceCrawler, CandidateDocument
from sources.brri import BRRICrawler
from sources.dae import DAECrawler
from sources.fao import FAOCrawler
from utils.logger import get_logger

logger = get_logger("crawler.main")


class AgricultureKnowledgePipeline:
    """End-to-end pipeline orchestrator for agricultural document intelligence."""

    def __init__(self):
        self.catalog_manager = CatalogManager()
        self.downloader = PDFDownloader()
        self.search_engine = DocumentSearchEngine()

        self.scrapers: dict[str, BaseSourceCrawler] = {
            "BRRI": BRRICrawler(),
            "BARI": BARICrawler(),
            "DAE": DAECrawler(),
            "BARC": BARCCrawler(),
            "BAMIS": BAMISCrawler(),
            "FAO": FAOCrawler(),
        }

    async def run(
        self,
        source_filter: str = "ALL",
        query: str = "",
        limit: int = 15,
        dry_run: bool = False,
    ):
        """Execute the end-to-end knowledge gathering pipeline."""
        logger.info("=================================================================")
        logger.info("  BANGLADESH AGRICULTURE KNOWLEDGE CRAWLER & ETL PIPELINE v2.0   ")
        logger.info("=================================================================")

        # Step 1: Discover candidate publications
        candidates: List[CandidateDocument] = []

        active_sources = (
            list(self.scrapers.keys())
            if source_filter.upper() == "ALL"
            else [s for s in self.scrapers.keys() if s.upper() == source_filter.upper()]
        )

        if not active_sources:
            logger.error(f"Unknown source filter: '{source_filter}'. Valid choices: {list(self.scrapers.keys())} or 'ALL'")
            return

        # 1a. Scrape selected government portals
        for src_key in active_sources:
            scraper = self.scrapers[src_key]
            logger.info(f"[DISCOVERY] Initiating crawler for portal: {src_key} ({TRUSTED_SOURCES[src_key]['name']})")
            docs = await scraper.discover()
            candidates.extend(docs)

        # 1b. If custom query or targeted search requested, execute search engine
        if query:
            logger.info(f"[SEARCH ENGINE] Executing targeted discovery for query: '{query}'")
            search_urls = await self.search_engine.search_duckduckgo(f"{query} filetype:pdf", max_results=10)
            for u in search_urls:
                candidates.append(CandidateDocument(url=u, title=query, source="SEARCH"))
        elif source_filter.upper() != "ALL":
            queries = AgriculturalQueryBuilder.generate_portal_queries(source_filter)
            search_urls = await self.search_engine.discover_for_source(source_filter, queries[:3], max_per_query=5)
            for u in search_urls:
                candidates.append(CandidateDocument(url=u, title=f"{source_filter} Publication", source=source_filter))

        # Deduplicate candidate URLs
        unique_candidates: List[CandidateDocument] = []
        seen_urls = set()
        for c in candidates:
            clean_u = c.url.strip()
            if clean_u not in seen_urls:
                seen_urls.add(clean_u)
                unique_candidates.append(c)

        logger.info(f"[QUEUE] Total {len(unique_candidates)} unique candidate documents queued. Processing up to {limit}...")

        processed_count = 0
        success_count = 0
        corrupt_count = 0
        skipped_count = 0

        for idx, candidate in enumerate(unique_candidates, start=1):
            if processed_count >= limit:
                logger.info(f"[LIMIT REACHED] Processed requested limit of {limit} documents.")
                break

            logger.info("-" * 65)
            logger.info(f"[{idx}/{len(unique_candidates)}] Ingesting from {candidate.source}: {candidate.title[:50]}...")
            logger.info(f"URL: {candidate.url}")

            # Step 2: Download PDF to temporary staging
            dl_result = await self.downloader.download(candidate.url)
            if not dl_result.success or not dl_result.file_path:
                logger.warning(f"[DOWNLOAD FAILED] {dl_result.error or 'Unknown error'}")
                continue

            staged_path = dl_result.file_path
            doc_hash = dl_result.doc_hash

            # Step 2b: Deduplication Check against master catalog
            if self.catalog_manager.is_already_cataloged(doc_hash):
                logger.info(f"[DEDUPLICATION] Document hash {doc_hash[:12]} already in catalog. Skipping.")
                remove_corrupt_file(staged_path, "Duplicate file already cataloged")
                skipped_count += 1
                continue

            # Step 3: Validate PDF Integrity
            is_valid, reason = validate_pdf(staged_path)
            if not is_valid:
                logger.warning(f"[INTEGRITY CHECK FAILED] {reason}")
                remove_corrupt_file(staged_path, reason)
                corrupt_count += 1
                continue

            # Step 4: Extract Text & Structural Outlines
            try:
                extracted = extract_pdf_content(staged_path)
            except Exception as exc:
                logger.warning(f"[EXTRACTION ERROR] Failed to parse text: {exc}")
                remove_corrupt_file(staged_path, f"Extraction failed: {exc}")
                corrupt_count += 1
                continue

            # Step 4b: Check viability of extracted text
            if extracted.char_count < MIN_EXTRACTED_TEXT_LENGTH:
                logger.warning(
                    f"[EMPTY/SCANNED] Extracted text length ({extracted.char_count} chars) below threshold. "
                    "File appears to be scanned image or empty. Removing from pipeline."
                )
                remove_corrupt_file(staged_path, "Text below minimum viable length")
                corrupt_count += 1
                continue

            # Step 5: Detect Language (Bengali / English / Bilingual)
            lang = detect_language(extracted.full_text)

            # Step 6: Agricultural Taxonomy Classification (24 Categories)
            classification = classify_document(extracted.full_text, extracted.title or candidate.title)

            # Step 7 & 8: Generate Metadata & Canonical Renaming
            metadata = generate_document_metadata(
                doc=extracted,
                classification=classification,
                source=candidate.source,
                url=candidate.url,
                language=lang,
                doc_hash=doc_hash,
                file_size_bytes=dl_result.file_size_bytes,
            )

            if dry_run:
                logger.info(f"[DRY RUN] Would save: {metadata.filename} -> {classification.primary_category}/")
                logger.info(f"          Quality: {metadata.quality_score} | Language: {metadata.language}")
                logger.info(f"          Crops: {metadata.related_crops} | Categories: {metadata.categories}")
                remove_corrupt_file(staged_path, "Dry run cleanup")
                processed_count += 1
                continue

            # Step 9: Store in Knowledge Base (PDF + Metadata JSON + Clean TXT)
            saved_path = self.catalog_manager.save_document(
                staged_pdf_path=staged_path,
                cleaned_text=extracted.full_text,
                metadata=metadata,
                primary_category=classification.primary_category,
            )

            # Clean staging file
            staged_path.unlink(missing_ok=True)

            processed_count += 1
            success_count += 1

        # Summary output
        logger.info("=" * 65)
        logger.info("PIPELINE EXECUTION COMPLETE")
        logger.info(f"Total Successfully Processed & Cataloged: {success_count}")
        logger.info(f"Corrupt/Invalid Files Removed:             {corrupt_count}")
        logger.info(f"Duplicates Skipped:                       {skipped_count}")
        logger.info("=" * 65)

        self.print_stats()

    def print_stats(self):
        """Display formatted knowledge base summary."""
        summary = self.catalog_manager.get_summary()
        logger.info("\n[STATS] KNOWLEDGE BASE INVENTORY SUMMARY:")
        logger.info(f"  Total Cataloged Documents: {summary.get('total_documents', 0)}")
        logger.info(f"  Total Extracted Pages:     {summary.get('total_pages', 0)}")
        logger.info(f"  Total Storage Volume:      {summary.get('total_size_mb', 0)} MB")

        logger.info("\n  Breakdown by Category (24 Categories):")
        by_cat = summary.get("by_category", {})
        active_cats = {k: v for k, v in by_cat.items() if v > 0}
        if active_cats:
            for cat, count in sorted(active_cats.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"    - {cat:<24} : {count} documents")
        else:
            logger.info("    (No documents stored yet)")

        logger.info("\n  Breakdown by Language:")
        by_lang = summary.get("by_language", {})
        for lang, count in by_lang.items():
            label = "Bengali (Bangla)" if lang == "bn" else ("English" if lang == "en" else "Bilingual (BN/EN)")
            logger.info(f"    - {label:<24} : {count}")

        logger.info("\n  Breakdown by Source Institution:")
        by_src = summary.get("by_source", {})
        for src, count in by_src.items():
            logger.info(f"    - {src:<24} : {count}")
        logger.info("")


def main():
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        description="Bangladesh Agriculture Knowledge Crawler & ETL Data Pipeline (BRRI, BARI, DAE, BARC, BAMIS, FAO)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="ALL",
        choices=["ALL", "BRRI", "BARI", "DAE", "BARC", "BAMIS", "FAO"],
        help="Target trusted source portal (default: ALL)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum documents to process in this run (default: 10)",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Optional search keyword or specific crop to discover",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display current knowledge base statistics and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and classify without persisting files",
    )

    args = parser.parse_args()

    pipeline = AgricultureKnowledgePipeline()

    if args.stats:
        pipeline.print_stats()
        return

    asyncio.run(
        pipeline.run(
            source_filter=args.source,
            query=args.query,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
