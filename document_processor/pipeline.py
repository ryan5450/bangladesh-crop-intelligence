"""End-to-end execution pipeline for document processing and RAG preparation."""

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from document_processor.chunker import DocumentChunk, DocumentChunker
from document_processor.config import (
    CHUNKS_DIR,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    KNOWLEDGE_BASE_DIR,
    METADATA_DIR,
    PROCESSED_DIR,
    REJECTED_DIR,
    REPORTS_DIR,
)
from document_processor.extractor import extract_document
from document_processor.scanner import scan_knowledge_base
from document_processor.validator import move_to_rejected, validate_pdf


class DocumentProcessingPipeline:
    """Orchestrates recursive scanning, validation, extraction, cleaning, and chunking."""

    def __init__(
        self,
        knowledge_base_dir: Optional[Path] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.kb_dir = knowledge_base_dir or KNOWLEDGE_BASE_DIR
        self.processed_dir = self.kb_dir / "processed"
        self.chunks_dir = self.kb_dir / "chunks"
        self.metadata_dir = self.kb_dir / "metadata"
        self.reports_dir = self.kb_dir / "reports"
        self.rejected_dir = self.kb_dir / "rejected"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def _ensure_directories(self) -> None:
        """Create target storage folders if they do not exist."""
        for target_dir in [
            self.processed_dir,
            self.chunks_dir,
            self.metadata_dir,
            self.reports_dir,
            self.rejected_dir,
        ]:
            target_dir.mkdir(parents=True, exist_ok=True)

    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute the end-to-end processing pipeline."""
        start_time = time.time()
        self._ensure_directories()

        print("=" * 68)
        print(" BANGLADESH CROP INTELLIGENCE ASSISTANT — DOCUMENT PROCESSOR")
        print("=" * 68)
        print(f"Scanning Directory:  {self.kb_dir}")
        print(f"Chunk Size:          {self.chunk_size} chars")
        print(f"Chunk Overlap:       {self.chunk_overlap} chars")
        print(f"Dry Run Mode:        {dry_run}")
        print("-" * 68)

        candidates = scan_knowledge_base(self.kb_dir)
        total_scanned = len(candidates)
        print(f"Discovered {total_scanned} candidate publication files across categories.")

        all_chunks: List[Dict[str, Any]] = []
        all_metadata: List[Dict[str, Any]] = []
        rejected_records: List[Dict[str, Any]] = []

        total_pages = 0
        total_chars = 0
        total_words = 0

        by_category: Dict[str, int] = {}
        by_language: Dict[str, int] = {}
        by_source: Dict[str, int] = {}

        for idx, candidate in enumerate(candidates, start=1):
            print(f"[{idx}/{total_scanned}] Validating: {candidate.file_path.name[:45]}...")

            # Step 1: Validate PDF
            validation = validate_pdf(candidate.file_path)
            if not validation.is_valid:
                print(f"  [REJECTED] {validation.reason}")
                rejected_record = {
                    "filename": candidate.file_path.name,
                    "category": candidate.category,
                    "source": candidate.source,
                    "reason": validation.reason,
                    "rejected_at": datetime.now(timezone.utc).isoformat(),
                }
                rejected_records.append(rejected_record)

                if not dry_run:
                    move_to_rejected(
                        file_path=candidate.file_path,
                        reason=validation.reason,
                        rejected_dir=self.rejected_dir,
                        category=candidate.category,
                    )
                continue

            # Step 2: Extract & Clean Text using PyMuPDF
            try:
                doc = extract_document(
                    file_path=candidate.file_path,
                    category=candidate.category,
                    source=candidate.source,
                    document_id=candidate.document_id,
                )
            except Exception as exc:
                print(f"  [EXTRACTION FAILED] {exc}")
                rejected_record = {
                    "filename": candidate.file_path.name,
                    "category": candidate.category,
                    "source": candidate.source,
                    "reason": f"Extraction exception: {exc}",
                    "rejected_at": datetime.now(timezone.utc).isoformat(),
                }
                rejected_records.append(rejected_record)
                if not dry_run:
                    move_to_rejected(
                        file_path=candidate.file_path,
                        reason=f"Extraction exception: {exc}",
                        rejected_dir=self.rejected_dir,
                        category=candidate.category,
                    )
                continue

            # Step 3: Chunk Document
            doc_chunks = self.chunker.chunk_document(doc)
            chunk_dicts = [c.to_dict() for c in doc_chunks]
            all_chunks.extend(chunk_dicts)

            # Accumulate metrics
            total_pages += doc.page_count
            total_chars += doc.char_count
            total_words += doc.word_count

            by_category[doc.category] = by_category.get(doc.category, 0) + 1
            by_language[doc.language] = by_language.get(doc.language, 0) + 1
            by_source[doc.source] = by_source.get(doc.source, 0) + 1

            doc_meta = {
                "document_id": doc.document_id,
                "title": candidate.title,
                "source": doc.source,
                "category": doc.category,
                "language": doc.language,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "char_count": doc.char_count,
                "word_count": doc.word_count,
                "chunk_count": len(doc_chunks),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
            all_metadata.append(doc_meta)

            print(f"  [PROCESSED] {doc.page_count} pages | {len(doc_chunks)} chunks | Lang: {doc.language}")

            # Save per-document cleaned text and sidecar metadata in processed/
            if not dry_run:
                txt_dest = self.processed_dir / f"{doc.document_id}_cleaned.txt"
                txt_dest.write_text(doc.full_cleaned_text, encoding="utf-8")

                meta_dest = self.processed_dir / f"{doc.document_id}.json"
                meta_dest.write_text(json.dumps(doc_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        duration_sec = round(time.time() - start_time, 2)
        total_passed = len(all_metadata)
        total_chunks = len(all_chunks)
        avg_chunk_size = round(sum(c["char_count"] for c in all_chunks) / max(1, total_chunks), 1)

        # Generate output JSON files
        report = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration_sec,
            "configuration": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "knowledge_base_dir": str(self.kb_dir),
            },
            "summary": {
                "total_scanned": total_scanned,
                "total_passed": total_passed,
                "total_rejected": len(rejected_records),
                "total_pages_extracted": total_pages,
                "total_words_extracted": total_words,
                "total_chunks_generated": total_chunks,
                "avg_chunk_size_chars": avg_chunk_size,
            },
            "breakdown_by_category": by_category,
            "breakdown_by_language": by_language,
            "breakdown_by_source": by_source,
            "rejected_files": rejected_records,
        }

        if not dry_run:
            # 1. chunks.json
            chunks_file = self.chunks_dir / "chunks.json"
            chunks_file.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")

            # 2. metadata.json
            metadata_file = self.metadata_dir / "metadata.json"
            metadata_payload = {
                "total_documents": total_passed,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "documents": all_metadata,
            }
            metadata_file.write_text(json.dumps(metadata_payload, indent=2, ensure_ascii=False), encoding="utf-8")

            # 3. processing_report.json
            report_file = self.reports_dir / "processing_report.json"
            report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print("=" * 68)
        print(" PROCESSING COMPLETE")
        print(f" Total Files Scanned:       {total_scanned}")
        print(f" Successfully Processed:    {total_passed}")
        print(f" Files Rejected:            {len(rejected_records)}")
        print(f" Total Pages Extracted:     {total_pages}")
        print(f" Total Chunks Created:      {total_chunks}")
        print(f" Average Chunk Size:        {avg_chunk_size} chars")
        print(f" Processing Time:           {duration_sec} seconds")
        print("=" * 68)
        if not dry_run:
            print(f" Chunks File:     {self.chunks_dir / 'chunks.json'}")
            print(f" Metadata File:   {self.metadata_dir / 'metadata.json'}")
            print(f" Report File:     {self.reports_dir / 'processing_report.json'}")
            print(f" Processed Txt:   {self.processed_dir}/")
        print("=" * 68)

        return report
