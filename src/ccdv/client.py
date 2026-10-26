"""Configuração compartilhada: cliente Anthropic e IDs de modelo."""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# IDs de modelo da família atual. Confira sempre na documentação oficial antes do exame.
MODEL_OPUS = "claude-opus-5-5"
MODEL_SONNET = "claude-sonnet-5-5"
MODEL_HAIKU = "claude-haiku-5-5"

DEFAULT_MODEL = os.getenv("CCDV_MODEL", MODEL_SONNET)


def get_client() -> Anthropic:
    """Cria o cliente. O SDK lê ANTHROPIC_API_KEY do ambiente."""
    return Anthropic()
