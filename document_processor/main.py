"""Command-line interface for the Document Processing Pipeline."""

import argparse
import json
from pathlib import Path
import sys

# Ensure module path is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

from document_processor.config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    KNOWLEDGE_BASE_DIR,
    METADATA_DIR,
    REPORTS_DIR,
)
from document_processor.pipeline import DocumentProcessingPipeline


def print_stats(kb_dir: Path) -> None:
    """Display summary metrics from the last processing run."""
    report_file = kb_dir / "reports" / "processing_report.json"
    if not report_file.exists():
        print(f"No processing report found at {report_file}. Run the pipeline first.")
        return

    try:
        report = json.loads(report_file.read_text(encoding="utf-8"))
        summary = report.get("summary", {})
        print("=" * 65)
        print(" KNOWLEDGE BASE DOCUMENT PROCESSING METRICS")
        print("=" * 65)
        print(f" Execution Date:       {report.get('execution_timestamp', 'Unknown')}")
        print(f" Processing Duration:  {report.get('duration_seconds', 0)} seconds")
        print(f" Total Documents:      {summary.get('total_passed', 0)} passed ({summary.get('total_rejected', 0)} rejected)")
        print(f" Total Pages:          {summary.get('total_pages_extracted', 0)}")
        print(f" Total Words:          {summary.get('total_words_extracted', 0):,}")
        print(f" Total Chunks:         {summary.get('total_chunks_generated', 0)}")
        print(f" Avg Chunk Size:       {summary.get('avg_chunk_size_chars', 0)} chars")
        print("\n Category Breakdown:")
        for cat, cnt in sorted(report.get("breakdown_by_category", {}).items(), key=lambda x: x[1], reverse=True):
            print(f"   - {cat:<24} : {cnt} documents")

        print("\n Language Breakdown:")
        for lang, cnt in report.get("breakdown_by_language", {}).items():
            print(f"   - {lang:<24} : {cnt} documents")

        print("\n Source Breakdown:")
        for src, cnt in report.get("breakdown_by_source", {}).items():
            print(f"   - {src:<24} : {cnt} documents")

        rejected = report.get("rejected_files", [])
        if rejected:
            print(f"\n Rejected Documents ({len(rejected)}):")
            for r in rejected[:8]:
                print(f"   x {r.get('filename', '')} : {r.get('reason', '')}")
            if len(rejected) > 8:
                print(f"   ... and {len(rejected) - 8} more.")
        print("=" * 65)
    except Exception as exc:
        print(f"Error reading report: {exc}")


def main() -> None:
    """CLI Entrypoint."""
    parser = argparse.ArgumentParser(
        description="Bangladesh Crop Intelligence Assistant — Document Processing & Chunking Pipeline"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Target character length per chunk (default: {DEFAULT_CHUNK_SIZE})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help=f"Overlap characters between consecutive chunks (default: {DEFAULT_CHUNK_OVERLAP})",
    )
    parser.add_argument(
        "--kb-dir",
        type=str,
        default=str(KNOWLEDGE_BASE_DIR),
        help="Path to knowledge_base root directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing and print metrics without writing files",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display summary metrics from the last processing run and exit",
    )

    args = parser.parse_args()
    kb_path = Path(args.kb_dir).resolve()

    if args.stats:
        print_stats(kb_path)
        return

    pipeline = DocumentProcessingPipeline(
        knowledge_base_dir=kb_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    pipeline.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
