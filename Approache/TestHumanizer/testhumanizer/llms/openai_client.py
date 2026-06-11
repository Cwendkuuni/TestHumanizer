from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

from testhumanizer.llms.base import LLMClient, LLMResponse
from testhumanizer.utils.tokens import count_tokens


class OpenAIChatClient(LLMClient):
    provider = "openai"

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key_env: str = "OPENAI_API_KEY",
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
            raise ValueError(f"Missing OpenAI API key in environment variable: {api_key_env}")

        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_wait_seconds = retry_wait_seconds
        self.timeout_seconds = timeout_seconds
        self.reserved_response_tokens = reserved_response_tokens
        self.max_total_tokens = max_total_tokens
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def _trim_prompt(self, prompt: str) -> tuple[str, bool, int, int]:
        max_prompt_tokens = self.max_total_tokens - self.reserved_response_tokens
        current_tokens = count_tokens(prompt, model=self.model)

        if current_tokens <= max_prompt_tokens:
            return prompt, False, current_tokens, current_tokens

        # tiktoken-based trimming
        import tiktoken

        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("o200k_base")

        tokens = encoding.encode(prompt)
        trimmed_prompt = encoding.decode(tokens[:max_prompt_tokens])
        return trimmed_prompt, True, current_tokens, max_prompt_tokens

    def complete(self, prompt: str) -> LLMResponse:
        prompt, was_trimmed, original_prompt_tokens, final_prompt_tokens = self._trim_prompt(prompt)

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.reserved_response_tokens,
                    temperature=self.temperature,
                )

                content = response.choices[0].message.content or ""
                usage = response.usage

                raw: Dict[str, Any] = {
                    "id": response.id,
                    "created": response.created,
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "was_prompt_trimmed": was_trimmed,
                    "original_prompt_tokens_estimated": original_prompt_tokens,
                    "final_prompt_tokens_estimated": final_prompt_tokens,
                }

                return LLMResponse(
                    provider=self.provider,
                    model=self.model,
                    content=content.strip(),
                    prompt_tokens=usage.prompt_tokens if usage else final_prompt_tokens,
                    completion_tokens=usage.completion_tokens if usage else None,
                    total_tokens=usage.total_tokens if usage else None,
                    raw=raw,
                )

            except AuthenticationError:
                raise

            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait_seconds)
                    continue
                raise

            except APIConnectionError as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_wait_seconds)
                    continue
                raise

            except APIError as e:
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
                raise RuntimeError(f"OpenAI completion failed after {self.max_retries} attempts: {last_error}")

        raise RuntimeError(f"OpenAI completion failed: {last_error}")
