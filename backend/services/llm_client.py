"""LLM client interface supporting local Ollama (Qwen 2.5 / Llama) and cloud fallbacks."""

import os
from typing import Any, Dict, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

# Default to local Ollama with 3B-7B open-source model
DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
DEFAULT_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))


class LLMClient:
    """Client for generating completions from local open-source LLMs or cloud endpoints."""

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 250
    ) -> str:
        """Send chat messages to the local Ollama LLM and return the assistant response.

        Args:
            messages: List of chat messages (e.g. system, user, assistant).
            temperature: Creativity control (low temperature = higher factual accuracy and speed).
            max_tokens: Maximum tokens in response (lower = faster response).

        Returns:
            The generated response text.
        """
        endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "repeat_penalty": 1.25,
                "top_k": 20,
                "top_p": 0.8
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            except httpx.ConnectError:
                logger.error(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
                raise ConnectionError(
                    f"Ollama server is not reachable at {self.base_url}. "
                    "Please ensure Ollama is running (`ollama serve`)."
                )
            except Exception as exc:
                logger.error(f"LLM generation failed: {exc}")
                raise RuntimeError(f"LLM generation error: {exc}")

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 220
    ):
        """Stream chat completions token-by-token from the local Ollama LLM.

        Yields:
            str: Token chunks as they arrive from the model.
        """
        import json
        endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "repeat_penalty": 1.25,
                "top_k": 20,
                "top_p": 0.8
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream("POST", endpoint, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
            except httpx.ConnectError:
                logger.error(f"Cannot connect to Ollama at {self.base_url}.")
                raise ConnectionError(
                    f"Ollama server is not reachable at {self.base_url}. "
                    "Please ensure Ollama is running (`ollama serve`)."
                )
            except Exception as exc:
                logger.error(f"LLM streaming failed: {exc}")
                raise RuntimeError(f"LLM streaming error: {exc}")



default_llm_client = LLMClient()
