# Vector Embeddings & ChromaDB Storage Module

Vector search and embedding pipeline for the **Bangladesh Crop Intelligence Assistant**.

This module generates vector embeddings for agricultural knowledge chunks and persists them in a local, high-performance **ChromaDB** database for semantic retrieval in the RAG pipeline.

---

## Features

- **Local & Offline-Ready**: Powered by CPU-optimized ONNX runtime embeddings without external API keys or PyTorch dependencies.
- **Multilingual Support**: Supports both **Bangla** and **English** agriculture documents, queries, and technical terms.
- **BRRI Rice Variety Integration**: Automatically ingests 139 BRRI rice variety profiles alongside general document chunks.
- **Metadata-Filtered Semantic Search**: Supports exact filtering by agricultural `category`, `source` institute (BRRI, BARI, DAE, BAMIS, FAO), and `language`.
- **RAG-Ready Citations**: Automatically formats retrieved passages with academic/government source and page citations for LLM prompt augmentation.
- **Pluggable Architecture**: Easily switchable to OpenAI (`text-embedding-3-small`) or Google Gemini (`text-embedding-004`).

---

## Quickstart CLI Commands

```powershell
# 1. Build the vector database from knowledge_base/chunks/chunks.json
.\backend\.venv\Scripts\python.exe -m vector_store.main --index

# 2. View database statistics
.\backend\.venv\Scripts\python.exe -m vector_store.main --stats

# 3. Test semantic search (Bangla query)
.\backend\.venv\Scripts\python.exe -m vector_store.main --query "ধানের ব্লাস্ট রোগের লক্ষণ ও প্রতিকার কী?"

# 4. Test semantic search (English query with category filter)
.\backend\.venv\Scripts\python.exe -m vector_store.main --query "soil salinity management in coastal areas" --category soil_management

# 5. Search for a specific rice variety
.\backend\.venv\Scripts\python.exe -m vector_store.main --query "BRRI dhan28 characteristics and yield" --top-k 3

# 6. Reset and rebuild collection
.\backend\.venv\Scripts\python.exe -m vector_store.main --index --reset
```

---

## Python API Usage (for FastAPI Backend)

```python
from vector_store import get_retriever

# Initialize retriever
retriever = get_retriever()

# Perform semantic search
results = retriever.search(
    query="বোরো ধানের চারা রোপণ সময় ও সার প্রয়োগ",
    top_k=5,
    category="cereals"
)

# Access metadata and text
for r in results:
    print(f"[{r.source}] {r.citation()} (Score: {r.relevance_score:.1%})")
    print(r.text)

# Generate formatted prompt context for LLM
context_text = retriever.format_context_for_rag(results)
```
