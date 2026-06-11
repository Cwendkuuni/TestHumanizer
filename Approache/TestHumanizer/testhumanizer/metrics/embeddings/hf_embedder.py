from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from transformers import AutoModel, AutoTokenizer, logging as hf_logging

hf_logging.set_verbosity_error()

DeviceName = Literal["auto", "cpu", "cuda"]


@dataclass
class HFEmbeddingResult:
    embedding: np.ndarray
    model_name: str
    device: str
    token_count: int
    truncated: bool


class HuggingFaceCodeEmbedder:
    def __init__(
        self,
        *,
        model_name: str,
        device: DeviceName = "auto",
        max_length: int = 512,
    ) -> None:
        self.model_name = model_name
        self.max_length = int(max_length)

        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def embed(self, code: str) -> HFEmbeddingResult | None:
        if not code or not code.strip():
            return None

        # encoded_no_trunc = self.tokenizer(
        #     code,
        #     return_tensors="pt",
        #     padding=False,
        #     truncation=False,
        # )

        # token_count = int(encoded_no_trunc["input_ids"].shape[1])
        # truncated = token_count > self.max_length

        token_ids = self.tokenizer.encode(
            code,
            add_special_tokens=True,
            truncation=False,
        )
        token_count = len(token_ids)
        truncated = token_count > self.max_length
        ######


        encoded = self.tokenizer(
            code,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
        )

        encoded = {k: v.to(self.device) for k, v in encoded.items()}

        with torch.no_grad():
            output = self.model(**encoded)

        # Mean pooling over tokens.
        embedding = output.last_hidden_state.mean(dim=1).detach().cpu().numpy()[0]

        return HFEmbeddingResult(
            embedding=embedding,
            model_name=self.model_name,
            device=self.device,
            token_count=token_count,
            truncated=truncated,
        )
