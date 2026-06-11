from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


DeviceName = Literal["auto", "cpu", "cuda"]


@dataclass
class SIDEResult:
    ok: bool
    score: float | None
    model_dir: str
    device: str
    code_token_count: int
    summary_token_count: int
    code_truncated: bool
    summary_truncated: bool
    error: str = ""


class SIDEModel:
    """
    Official SIDE-style scorer.

    Computes cosine similarity between the model embeddings of:
      - source code
      - generated natural-language summary

    The implementation follows the local usage pattern from the previous SIDE
    script: AutoTokenizer + AutoModel + mean pooling + L2 normalization.
    """

    def __init__(
        self,
        *,
        model_dir: str | Path,
        device: DeviceName = "auto",
        max_length: int = 512,
        project_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root or ".").expanduser().resolve()
        self.model_dir = self._resolve_path(model_dir)
        self.max_length = int(max_length)

        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if not self.model_dir.exists():
            raise FileNotFoundError(f"SIDE model directory not found: {self.model_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))
        self.model = AutoModel.from_pretrained(str(self.model_dir)).to(self.device)
        self.model.eval()

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.project_root / p
        return p.absolute()

    def score(self, code: str, summary: str) -> SIDEResult:
        if not code or not code.strip():
            return SIDEResult(
                ok=False,
                score=None,
                model_dir=str(self.model_dir),
                device=self.device,
                code_token_count=0,
                summary_token_count=0,
                code_truncated=False,
                summary_truncated=False,
                error="Source code is empty.",
            )

        if not summary or not summary.strip():
            return SIDEResult(
                ok=False,
                score=None,
                model_dir=str(self.model_dir),
                device=self.device,
                code_token_count=0,
                summary_token_count=0,
                code_truncated=False,
                summary_truncated=False,
                error="Summary is empty.",
            )

        try:
            code_token_count = len(
                self.tokenizer.encode(
                    code,
                    add_special_tokens=True,
                    truncation=False,
                )
            )
            summary_token_count = len(
                self.tokenizer.encode(
                    summary,
                    add_special_tokens=True,
                    truncation=False,
                )
            )

            code_embedding = self._embed_text(code)
            summary_embedding = self._embed_text(summary)

            #similarity = torch.matmul(code_embedding, summary_embedding.T).item()
            similarity = torch.dot(code_embedding, summary_embedding).item()

            return SIDEResult(
                ok=True,
                score=float(similarity),
                model_dir=str(self.model_dir),
                device=self.device,
                code_token_count=code_token_count,
                summary_token_count=summary_token_count,
                code_truncated=code_token_count > self.max_length,
                summary_truncated=summary_token_count > self.max_length,
                error="",
            )

        except Exception as e:
            return SIDEResult(
                ok=False,
                score=None,
                model_dir=str(self.model_dir),
                device=self.device,
                code_token_count=0,
                summary_token_count=0,
                code_truncated=False,
                summary_truncated=False,
                error=f"{type(e).__name__}: {e}",
            )

    def _embed_text(self, text: str) -> torch.Tensor:
        encoded = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        encoded = {key: value.to(self.device) for key, value in encoded.items()}

        with torch.no_grad():
            model_output = self.model(**encoded)

        embeddings = self._mean_pooling(
            model_output=model_output,
            attention_mask=encoded["attention_mask"],
        )

        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings[0]

    @staticmethod
    def _mean_pooling(model_output, attention_mask: torch.Tensor) -> torch.Tensor:
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1)
            .expand(token_embeddings.size())
            .float()
        )

        return torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(
            input_mask_expanded.sum(dim=1),
            min=1e-9,
        )
