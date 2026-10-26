"""Testes que chamam a API real. Não rodam por padrão.

Execute com:  uv run pytest -m live
Precisa de ANTHROPIC_API_KEY no ambiente ou no .env. Gasta tokens (poucos).
"""

import os

import pytest

from ccdv.client import get_client
from ccdv.fundamentals.chat import ask, count_tokens

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="sem ANTHROPIC_API_KEY"),
]


def test_real_ask_returns_text():
    client = get_client()
    answer = ask(client, "Responda apenas com a palavra: ok", max_tokens=20)
    assert answer.strip()


def test_real_count_tokens_is_positive():
    client = get_client()
    assert count_tokens(client, [{"role": "user", "content": "Olá"}]) > 0
