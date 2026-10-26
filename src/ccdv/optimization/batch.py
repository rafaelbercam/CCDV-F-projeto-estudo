"""Módulo 04 — Message Batches: processamento assíncrono e mais barato para volume grande.

Use batch quando a latência não importa (classificação em massa, avaliações, backfill).
Para UX interativa, use chamadas normais com streaming.
"""

import time
from collections.abc import Iterable
from typing import Any

from ccdv.fundamentals.chat import text_of


def build_batch_requests(items: list[tuple[str, str]], model: str, max_tokens: int = 256) -> list[dict]:
    """items: lista de (custom_id, prompt). custom_id volta junto com o resultado."""
    return [
        {
            "custom_id": custom_id,
            "params": {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
        }
        for custom_id, prompt in items
    ]


def submit_batch(client: Any, requests: list[dict]) -> str:
    return client.messages.batches.create(requests=requests).id


def wait_for_batch(client: Any, batch_id: str, poll_seconds: float = 30.0) -> None:
    while client.messages.batches.retrieve(batch_id).processing_status != "ended":
        time.sleep(poll_seconds)


def collect_results(entries: Iterable[Any]) -> dict[str, str]:
    """Extrai texto dos resultados bem-sucedidos. Erros e cancelamentos ficam de fora."""
    out: dict[str, str] = {}
    for entry in entries:
        if entry.result.type == "succeeded":
            out[entry.custom_id] = text_of(entry.result.message)
    return out


def batch_results(client: Any, batch_id: str) -> dict[str, str]:
    return collect_results(client.messages.batches.results(batch_id))
