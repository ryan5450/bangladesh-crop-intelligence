"""Assistant router providing chat and agricultural intelligence query endpoints."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

try:
    from services.rag_service import default_rag_service, AssistantChatResponse
except ImportError:
    from backend.services.rag_service import default_rag_service, AssistantChatResponse
from vector_store.config import default_config
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])


class ChatMessageTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, description="User question in Bangla or English")
    category: Optional[str] = Field(None, description="Optional category filter (e.g. cereals, diseases)")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context passages to retrieve")
    conversation_history: Optional[List[ChatMessageTurn]] = Field(
        default=None, description="Previous conversation turns for context"
    )


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(payload: ChatRequest):
    """Chat with the Bangladesh Crop Intelligence Assistant.
    
    Supports queries in Bangla, English, or Banglish with cross-lingual RAG retrieval.
    """
    try:
        history = [
            {"role": turn.role, "content": turn.content}
            for turn in (payload.conversation_history or [])
        ]
        
        response = await default_rag_service.answer_question(
            query=payload.message,
            category=payload.category,
            top_k=payload.top_k,
            conversation_history=history
        )
        return response

    except ConnectionError as ce:
        logger.error(f"LLM Connection failed: {ce}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local LLM engine (Ollama) is not running: {ce}"
        )
    except Exception as exc:
        logger.error(f"Chat processing failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(exc)}"
        )


@router.post("/chat/stream")
async def chat_with_assistant_stream(payload: ChatRequest):
    """Stream chat response token-by-token using Server-Sent Events (SSE)."""
    import json
    from fastapi.responses import StreamingResponse

    history = [
        {"role": turn.role, "content": turn.content}
        for turn in (payload.conversation_history or [])
    ]

    async def event_generator():
        try:
            async for event in default_rag_service.stream_answer_question(
                query=payload.message,
                category=payload.category,
                top_k=payload.top_k,
                conversation_history=history
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except ConnectionError as ce:
            logger.error(f"Streaming LLM Connection failed: {ce}")
            err_payload = {"type": "error", "message": f"Local LLM engine (Ollama) is not running: {ce}"}
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
        except Exception as exc:
            logger.error(f"Streaming failed: {exc}", exc_info=True)
            err_payload = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/health")
async def assistant_health():
    """Health check validating ChromaDB vector store and Ollama LLM connectivity."""
    ollama_ok = False
    ollama_model = default_rag_service.llm.model
    vector_ok = False
    vector_count = 0

    # 1. Test Ollama connectivity
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{default_rag_service.llm.base_url}/api/tags")
            if res.status_code == 200:
                ollama_ok = True
    except Exception:
        ollama_ok = False

    # 2. Test ChromaDB connectivity
    try:
        vector_count = default_rag_service.retriever.collection.count()
        vector_ok = vector_count > 0
    except Exception:
        vector_ok = False

    return {
        "status": "healthy" if (ollama_ok and vector_ok) else "degraded",
        "llm_service": {
            "connected": ollama_ok,
            "engine": "Ollama",
            "model": ollama_model,
            "endpoint": default_rag_service.llm.base_url
        },
        "vector_store": {
            "connected": vector_ok,
            "engine": "ChromaDB",
            "collection": default_config.collection_name,
            "total_vectors": vector_count,
            "persistence_path": str(default_config.persist_dir)
        }
    }
