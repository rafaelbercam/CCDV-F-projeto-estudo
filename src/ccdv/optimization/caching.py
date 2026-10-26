"""Módulo 04 — prompt caching via `cache_control` e leitura do campo `usage`.

O cache só é ativado quando o prefixo marcado tem o tamanho mínimo exigido pelo modelo.
Prompt curto não gera cache hit: nada de erro, só `cache_read_input_tokens == 0`.
"""

from typing import Any

from ccdv.client import DEFAULT_MODEL
from ccdv.fundamentals.chat import text_of


def cached_ask(
    client: Any,
    system_text: str,
    user_text: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 512,
) -> tuple[str, dict]:
    """Chama o modelo marcando o system prompt para cache. Devolve (texto, relatório de uso)."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_text}],
    )
    return text_of(response), usage_report(response.usage)


def usage_report(usage: Any) -> dict:
    """Converte `usage` em números fáceis de comparar entre chamadas."""
    cache_read = usage.cache_read_input_tokens or 0
    cache_write = usage.cache_creation_input_tokens or 0
    # input_tokens NÃO inclui os tokens de cache; o total de entrada é a soma dos três.
    total_input = usage.input_tokens + cache_read + cache_write
    return {
        "input_tokens": usage.input_tokens,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "output_tokens": usage.output_tokens,
        "cache_hit_ratio": cache_read / total_input if total_input else 0.0,
    }
