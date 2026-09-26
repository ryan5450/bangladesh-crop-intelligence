"""CLI entrypoint for Bangladesh Crop Intelligence Vector Store management.

Usage:
    python -m vector_store.main --index
    python -m vector_store.main --index --reset
    python -m vector_store.main --query "ধানের ব্লাস্ট রোগের সমাধান কী?"
    python -m vector_store.main --query "BRRI dhan28 characteristics" --top-k 3
    python -m vector_store.main --stats
"""

import argparse
import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from vector_store.config import VectorStoreConfig, default_config
from vector_store.indexer import ChromaIndexer
from vector_store.retriever import ChromaRetriever


def print_banner():
    print("=" * 70)
    print(" BANGLADESH CROP INTELLIGENCE ASSISTANT — VECTOR STORE")
    print("=" * 70)


def cmd_stats(config: VectorStoreConfig):
    print_banner()
    try:
        retriever = ChromaRetriever(config=config)
        col = retriever.collection
        count = col.count()
        print(f"Collection Name:    {col.name}")
        print(f"Persistence Path:   {config.persist_dir}")
        print(f"Total Vector Count: {count:,}")
        print(f"Embedding Provider: {config.embedding_provider}")
        
        # Check report
        report_file = config.persist_dir.parent / "reports" / "vector_indexing_report.json"
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                rep = json.load(f)
            print("-" * 70)
            print(f"Last Indexed:       {rep.get('timestamp')}")
            print(f"Duration:           {rep.get('duration_seconds')} seconds")
            print(f"Doc Chunks:         {rep.get('doc_chunks_indexed', 0):,}")
            print(f"Variety Profiles:   {rep.get('variety_profiles_indexed', 0):,}")
    except Exception as exc:
        print(f"Error reading vector store: {exc}")
    print("=" * 70)


def cmd_index(args, config: VectorStoreConfig):
    print_banner()
    print(f"Target Database:    {config.persist_dir}")
    print(f"Collection:         {config.collection_name}")
    print(f"Batch Size:         {args.batch_size}")
    print(f"Reset Existing:     {args.reset}")
    print("-" * 70)

    indexer = ChromaIndexer(config=config)
    result = indexer.index(reset_existing=args.reset, batch_size=args.batch_size)

    print("=" * 70)
    print(" INDEXING COMPLETE")
    print(f" Total Indexed:      {result['total_chunks_indexed']:,} vectors")
    print(f" Total Duration:     {result['duration_seconds']} seconds")
    print(f" Average Speed:      {result['avg_speed_chunks_per_sec']} chunks/sec")
    print(f" Final Store Count:  {result['final_collection_count']:,} vectors")
    print(f" Database Path:      {result['persist_directory']}")
    print("=" * 70)


def cmd_query(args, config: VectorStoreConfig):
    print_banner()
    print(f"Query:       \"{args.query}\"")
    print(f"Top K:       {args.top_k}")
    if args.category:
        print(f"Category:    {args.category}")
    if args.source:
        print(f"Source:      {args.source}")
    print("-" * 70)

    try:
        retriever = ChromaRetriever(config=config)
        results = retriever.search(
            query=args.query,
            top_k=args.top_k,
            category=args.category,
            source=args.source
        )

        if not results:
            print("No matching knowledge documents found.")
            return

        print(f"Found {len(results)} relevant passages:\n")
        for i, r in enumerate(results, 1):
            print(f"[{i}] {r.citation()} | Relevance: {r.relevance_score:.1%} | Distance: {r.distance}")
            print(f"    Chunk ID:    {r.chunk_id}")
            print(f"    Language:    {r.language}")
            snippet = r.text.strip().replace("\n", " ")
            print(f"    Content:     {snippet[:280]}...")
            print()

        if args.show_context:
            print("=" * 70)
            print(" FORMATTED RAG CONTEXT BLOCK FOR LLM:")
            print("=" * 70)
            print(retriever.format_context_for_rag(results))
            print("=" * 70)

    except Exception as exc:
        print(f"Query error: {exc}")


def main():
    parser = argparse.ArgumentParser(
        description="Bangladesh Crop Intelligence Assistant — ChromaDB Vector Store CLI"
    )
    parser.add_argument("--index", action="store_true", help="Build or update vector index from chunks.json")
    parser.add_argument("--reset", action="store_true", help="Clear and rebuild collection from scratch")
    parser.add_argument("--batch-size", type=int, default=default_config.batch_size, help="ChromaDB insert batch size")
    parser.add_argument("--query", "-q", type=str, help="Search semantic vector index with a query string")
    parser.add_argument("--top-k", "-k", type=int, default=default_config.default_top_k, help="Number of results to retrieve")
    parser.add_argument("--category", type=str, help="Filter search by agricultural category")
    parser.add_argument("--source", type=str, help="Filter search by source institute (BRRI, BARI, DAE, BAMIS, FAO)")
    parser.add_argument("--stats", action="store_true", help="Show vector store collection statistics")
    parser.add_argument("--show-context", action="store_true", help="Display full formatted RAG prompt context block")

    args = parser.parse_args()

    if args.index:
        cmd_index(args, default_config)
    elif args.query:
        cmd_query(args, default_config)
    elif args.stats:
        cmd_stats(default_config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
