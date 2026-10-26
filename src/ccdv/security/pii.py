"""Módulo 05 — remoção de PII em texto livre (saída do modelo ou logs).

Regex pega formatos conhecidos, não pega nomes de pessoas nem formatos novos.
Em produção, combine com um detector de PII (NER / serviço dedicado) e teste com casos reais.
A ordem importa: padrões mais específicos (CPF, SSN) rodam antes do telefone, que é genérico.
"""

import re
from dataclasses import dataclass

PATTERNS: dict[str, re.Pattern[str]] = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PHONE": re.compile(r"(?:\+\d{1,3}[ -]?)?(?:\(\d{2}\)|\d{2})[ -]?\d{4,5}-?\d{4}\b"),
}


@dataclass(frozen=True)
class Redaction:
    text: str
    counts: dict[str, int]


def redact_pii(text: str) -> Redaction:
    counts: dict[str, int] = {}
    for label, pattern in PATTERNS.items():
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return Redaction(text, counts)
