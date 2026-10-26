"""Módulo 05 — validação de entrada do usuário.

Validação de formato e tamanho é barata e deve sempre existir. Ela NÃO é defesa contra
injeção: blocklist de "DROP TABLE" não protege SQL nem prompt injection. Para SQL, a
proteção é parametrização + permissões mínimas (veja ccdv.tools.sql_tool). Para prompt
injection, a proteção é limitar o que as tools podem fazer, não filtrar texto.
"""

from dataclasses import dataclass

MAX_INPUT_CHARS = 10_000
_ALLOWED_CONTROL = {"\n", "\t", "\r"}


@dataclass(frozen=True)
class Validation:
    ok: bool
    reason: str | None = None


def validate_user_text(text: str, max_chars: int = MAX_INPUT_CHARS) -> Validation:
    if not text.strip():
        return Validation(False, "entrada vazia")
    if len(text) > max_chars:
        return Validation(False, f"entrada excede {max_chars} caracteres")
    if any(ord(ch) < 32 and ch not in _ALLOWED_CONTROL for ch in text):
        return Validation(False, "caracteres de controle não permitidos")
    return Validation(True)
