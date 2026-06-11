from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from mistralai.client import Mistral

from testhumanizer.llms.base import LLMClient, LLMResponse
from testhumanizer.utils.tokens import count_tokens


class MistralChatClient(LLMClient):
    provider = "mistral"

    def __init__(
        self,
        model: str = "mistral-large-2407",
        api_key_env: str = "MISTRAL_API_KEY",
        temperature: float = 0.1,
        max_retries: int = 30,
        retry_wait_seconds: int = 10,
        timeout_seconds: int = 120,
        reserved_response_tokens: int = 16000,
        max_total_tokens: int = 128000,
    ) -> None:
        load_dotenv()

        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"Missing Mistral API key in environment variable: {api_key_env}")

        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_wait_seconds = retry_wait_seconds
        self.timeout_seconds = timeout_seconds
        self.reserved_response_tokens = reserved_response_tokens
        self.max_total_tokens = max_total_tokens

        # The Mistral SDK supports client-level configuration through the client object.
        self.client = Mistral(api_key=api_key)

    def _trim_prompt(self, prompt: str) -> tuple[str, bool, int, int]:
        # For Mistral, tiktoken is only an approximation, but it is useful
        # for normalized budget tracking across providers.
        max_prompt_tokens = self.max_total_tokens - self.reserved_response_tokens
        estimated_tokens = count_tokens(prompt, model="gpt-4o")

        if estimated_tokens <= max_prompt_tokens:
            return prompt, False, estimated_tokens, estimated_tokens

        import tiktoken

        encoding = tiktoken.get_encoding("o200k_base")
        tokens = encoding.encode(prompt)
        trimmed_prompt = encoding.decode(tokens[:max_prompt_tokens])

        return trimmed_prompt, True, estimated_tokens, max_prompt_tokens

    def complete(self, prompt: str) -> LLMResponse:
        prompt, was_trimmed, original_prompt_tokens, final_prompt_tokens = self._trim_prompt(prompt)

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.complete(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.reserved_response_tokens,
                )

                content = response.choices[0].message.content or ""

                usage = getattr(response, "usage", None)

                raw: Dict[str, Any] = {
                    "id": getattr(response, "id", None),
                    "model": getattr(response, "model", self.model),
                    "finish_reason": getattr(response.choices[0], "finish_reason", None),
                    "was_prompt_trimmed": was_trimmed,
                    "original_prompt_tokens_estimated": original_prompt_tokens,
                    "final_prompt_tokens_estimated": final_prompt_tokens,
                }

                return LLMResponse(
                    provider=self.provider,
                    model=self.model,
                    content=content.strip(),
                    prompt_tokens=getattr(usage, "prompt_tokens", final_prompt_tokens) if usage else final_prompt_tokens,
                    completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
                    total_tokens=getattr(usage, "total_tokens", None) if usage else None,
                    raw=raw,
                )

            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait_seconds)
                    continue

                raise RuntimeError(
                    f"Mistral completion failed after {self.max_retries} attempts: {last_error}"
                )

        raise RuntimeError(f"Mistral completion failed: {last_error}")
