"""Módulo 01 — Messages API: chamada simples, streaming e contagem de tokens."""

from collections.abc import Iterator
from typing import Any

from ccdv.client import DEFAULT_MODEL


def text_of(response: Any) -> str:
    """Concatena os blocos de texto da resposta. Ignora blocos tool_use e outros tipos."""
    return "".join(block.text for block in response.content if block.type == "text")


def ask(client: Any, prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 1024) -> str:
    """Chamada não-streaming: espera a resposta completa."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return text_of(response)


def stream_text(client: Any, prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 1024) -> Iterator[str]:
    """Chamada com streaming: devolve pedaços de texto conforme chegam (melhor latência percebida)."""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        yield from stream.text_stream


def count_tokens(
    client: Any,
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system: str | None = None,
) -> int:
    """Conta tokens de entrada sem gerar resposta. Útil para orçamento antes de enviar."""
    kwargs: dict[str, Any] = {"model": model, "messages": messages}
    if system is not None:
        kwargs["system"] = system
    return client.messages.count_tokens(**kwargs).input_tokens
