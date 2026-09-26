"""Configurable, sentence-aware chunking engine for agricultural RAG pipelines."""

from dataclasses import asdict, dataclass
import re
from typing import Any, Dict, List
from document_processor.config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE
from document_processor.extractor import ExtractedDocument
from document_processor.language_detector import detect_language


@dataclass
class DocumentChunk:
    """RAG and ChromaDB compatible text chunk."""
    text: str
    source: str
    category: str
    page_number: int
    language: str
    chunk_id: str
    document_id: str
    chunk_index: int
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk into strict metadata dictionary."""
        return asdict(self)


class DocumentChunker:
    """Splits documents into overlapping semantic chunks with page-level provenance."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be strictly less than chunk_size ({chunk_size})")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Sentence splitting pattern supporting English periods/exclamations and Bengali dāri (।)
        self.sentence_delimiter = re.compile(r"(?<=[।\.\?!])\s+|\n{2,}")

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentence units preserving Bengali and English terminal punctuation."""
        raw_parts = self.sentence_delimiter.split(text)
        sentences: List[str] = []
        for part in raw_parts:
            s = part.strip()
            if s:
                sentences.append(s)
        return sentences

    def _chunk_page_text(self, text: str) -> List[str]:
        """Sliding-window chunking over sentences with configurable overlap."""
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        sentences = self._split_into_sentences(text)
        if not sentences:
            # Fallback to word splitting if no punctuation detected
            words = text.split()
            sentences = [" ".join(words[i : i + 20]) for i in range(0, len(words), 20)]

        chunks: List[str] = []
        current_chunk_sentences: List[str] = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence) + 1

            if current_len + sentence_len <= self.chunk_size or not current_chunk_sentences:
                current_chunk_sentences.append(sentence)
                current_len += sentence_len
            else:
                chunk_str = " ".join(current_chunk_sentences).strip()
                if len(chunk_str) >= MIN_CHUNK_SIZE:
                    chunks.append(chunk_str)

                # Determine overlap window from tail sentences
                overlap_sentences: List[str] = []
                overlap_len = 0
                for prev_sent in reversed(current_chunk_sentences):
                    if overlap_len + len(prev_sent) <= self.chunk_overlap:
                        overlap_sentences.insert(0, prev_sent)
                        overlap_len += len(prev_sent)
                    else:
                        break

                current_chunk_sentences = overlap_sentences + [sentence]
                current_len = sum(len(s) + 1 for s in current_chunk_sentences)

        if current_chunk_sentences:
            final_str = " ".join(current_chunk_sentences).strip()
            if len(final_str) >= MIN_CHUNK_SIZE and (not chunks or final_str != chunks[-1]):
                chunks.append(final_str)

        return chunks

    def chunk_document(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """Convert an extracted document into an ordered list of DocumentChunks."""
        all_chunks: List[DocumentChunk] = []
        chunk_counter = 0

        for page in doc.pages:
            cleaned_page_text = page.cleaned_text.strip()
            if not cleaned_page_text or len(cleaned_page_text) < 20:
                continue

            raw_chunks = self._chunk_page_text(cleaned_page_text)

            for raw_chunk in raw_chunks:
                chunk_lang = detect_language(raw_chunk) or doc.language
                chunk_counter += 1
                chunk_id = f"{doc.document_id}_p{page.page_number}_c{chunk_counter:03d}"

                chunk_obj = DocumentChunk(
                    text=raw_chunk,
                    source=doc.source,
                    category=doc.category,
                    page_number=page.page_number,
                    language=chunk_lang,
                    chunk_id=chunk_id,
                    document_id=doc.document_id,
                    chunk_index=chunk_counter,
                    char_count=len(raw_chunk),
                )
                all_chunks.append(chunk_obj)

        return all_chunks
