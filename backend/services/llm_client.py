"""LLM client interface supporting local Ollama (Qwen 2.5 / Llama) and cloud providers (Groq)."""

import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

# Environment variable configurations
DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
DEFAULT_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
GROQ_API_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "qwen/qwen3.8-27b"


class LLMClient:
    """Client for generating completions from local open-source LLMs (Ollama) or free cloud APIs (Groq)."""

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        groq_api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "").strip()

        # If Groq is active, use GROQ_MODEL or fallback to GROQ_DEFAULT_MODEL
        if self.groq_api_key:
            env_groq_model = os.getenv("GROQ_MODEL", "").strip()
            if env_groq_model and env_groq_model != "llama-3.1-8b-instant":
                self.model = env_groq_model
            else:
                self.model = GROQ_DEFAULT_MODEL
            logger.info(f"LLM Client initialized with Groq Cloud (Model: {self.model})")
        else:
            self.model = model
            logger.info(f"LLM Client initialized with local Ollama at {self.base_url} (Model: {self.model})")

    @property
    def is_groq(self) -> bool:
        """Check if Groq Cloud mode is enabled."""
        return bool(self.groq_api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 300
    ) -> str:
        """Send chat messages to either Groq Cloud or local Ollama and return response text."""
        if self.is_groq:
            return await self._chat_groq(messages, temperature, max_tokens)
        return await self._chat_ollama(messages, temperature, max_tokens)

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 300
    ) -> AsyncGenerator[str, None]:
        """Stream chat completions token-by-token from Groq Cloud or local Ollama."""
        if self.is_groq:
            async for token in self._stream_groq(messages, temperature, max_tokens):
                yield token
        else:
            async for token in self._stream_ollama(messages, temperature, max_tokens):
                yield token

    # --------------------------------------------------------------------------
    # Groq Cloud Implementation (100% Free, High-Speed Cloud LPU)
    # --------------------------------------------------------------------------
    async def _chat_groq(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        endpoint = f"{GROQ_API_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    err_detail = response.text
                    try:
                        err_detail = response.json().get("error", {}).get("message", response.text)
                    except Exception:
                        pass
                    raise RuntimeError(f"Groq API error ({response.status_code}): {err_detail}")
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as exc:
                logger.error(f"Groq generation failed: {exc}")
                raise RuntimeError(f"Groq API error: {exc}")

    async def _stream_groq(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        endpoint = f"{GROQ_API_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err_bytes = await response.aread()
                        err_text = err_bytes.decode("utf-8", errors="replace")
                        try:
                            err_text = json.loads(err_text).get("error", {}).get("message", err_text)
                        except Exception:
                            pass
                        raise RuntimeError(f"Groq Streaming error ({response.status_code}): {err_text}")
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        line_data = line[6:].strip()
                        if line_data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line_data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
            except Exception as exc:
                logger.error(f"Groq streaming failed: {exc}")
                raise RuntimeError(f"Groq streaming error: {exc}")

    # --------------------------------------------------------------------------
    # Ollama Local Implementation (Offline, Privacy-First)
    # --------------------------------------------------------------------------
    async def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
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
                logger.error(f"Cannot connect to Ollama at {self.base_url}.")
                raise ConnectionError(
                    f"Ollama server is not reachable at {self.base_url}. "
                    "Please ensure Ollama is running (`ollama serve`)."
                )
            except Exception as exc:
                logger.error(f"LLM generation failed: {exc}")
                raise RuntimeError(f"LLM generation error: {exc}")

    async def _stream_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
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
                    f"Ollama server is not reachable at {self.base_url}."
                )
            except Exception as exc:
                logger.error(f"LLM streaming failed: {exc}")
                raise RuntimeError(f"LLM streaming error: {exc}")


default_llm_client = LLMClient()
