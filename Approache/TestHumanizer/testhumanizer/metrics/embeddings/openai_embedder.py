from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError


@dataclass
class OpenAIEmbeddingResult:
    embedding: np.ndarray
    model_name: str
    token_count: Optional[int]
    cached: bool


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


class OpenAIEmbeddingCache:
    def __init__(self, cache_dir: str | Path) -> None:
        self.cache_dir = Path(cache_dir).expanduser().resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, *, model_name: str, text: str) -> Path:
        key = sha256_text(model_name + "\n" + text)
        return self.cache_dir / f"{key}.json"

    def get(self, *, model_name: str, text: str) -> Optional[np.ndarray]:
        path = self._path(model_name=model_name, text=text)

        if not path.exists():
            return None

        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        return np.array(payload["embedding"], dtype=np.float32)

    def set(self, *, model_name: str, text: str, embedding: np.ndarray) -> None:
        path = self._path(model_name=model_name, text=text)

        payload = {
            "model_name": model_name,
            "text_sha256": sha256_text(text),
            "embedding": embedding.astype(float).tolist(),
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f)


class OpenAIEmbeddingClient:
    def __init__(
        self,
        *,
        model_name: str = "text-embedding-3-small",
        api_key_env: str = "OPENAI_API_KEY",
        max_retries: int = 30,
        retry_wait_seconds: int = 15,
        timeout_seconds: int = 120,
        cache_dir: str | Path | None = None,
        cache_enabled: bool = True,
    ) -> None:
        load_dotenv()

        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"Missing OpenAI API key in environment variable: {api_key_env}")

        self.model_name = model_name
        self.max_retries = int(max_retries)
        self.retry_wait_seconds = int(retry_wait_seconds)
        self.timeout_seconds = int(timeout_seconds)
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)

        self.cache_enabled = bool(cache_enabled)
        self.cache = OpenAIEmbeddingCache(cache_dir) if cache_enabled and cache_dir else None

    def embed(self, text: str) -> OpenAIEmbeddingResult | None:
        if not text or not text.strip():
            return None

        if self.cache is not None:
            cached_embedding = self.cache.get(model_name=self.model_name, text=text)
            if cached_embedding is not None:
                return OpenAIEmbeddingResult(
                    embedding=cached_embedding,
                    model_name=self.model_name,
                    token_count=None,
                    cached=True,
                )

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model_name,
                )

                embedding = np.array(response.data[0].embedding, dtype=np.float32)
                usage = getattr(response, "usage", None)
                token_count = getattr(usage, "total_tokens", None) if usage else None

                if self.cache is not None:
                    self.cache.set(
                        model_name=self.model_name,
                        text=text,
                        embedding=embedding,
                    )

                return OpenAIEmbeddingResult(
                    embedding=embedding,
                    model_name=self.model_name,
                    token_count=token_count,
                    cached=False,
                )

            except AuthenticationError:
                raise

            except (RateLimitError, APIConnectionError, APIError) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait_seconds)
                    continue
                raise

            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait_seconds)
                    continue
                raise RuntimeError(
                    f"OpenAI embedding failed after {self.max_retries} attempts: {last_error}"
                )

        raise RuntimeError(f"OpenAI embedding failed: {last_error}")
