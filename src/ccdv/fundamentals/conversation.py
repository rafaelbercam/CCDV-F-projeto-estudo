"""Projeto 1 — chat multi-turno com contagem de tokens e compactação de contexto.

Quando o histórico passa de `max_input_tokens`, os turnos mais antigos são
resumidos por um modelo barato (Haiku) e substituídos por um único resumo.
Os últimos `keep_recent_turns` turnos do usuário são mantidos literalmente.
"""

from dataclasses import dataclass, field
from typing import Any

from ccdv.client import DEFAULT_MODEL, MODEL_HAIKU
from ccdv.fundamentals.chat import count_tokens, text_of


@dataclass
class Conversation:
    client: Any
    system: str = "Você é um assistente conciso."
    model: str = DEFAULT_MODEL
    summary_model: str = MODEL_HAIKU
    max_input_tokens: int = 100_000
    keep_recent_turns: int = 4
    messages: list[dict] = field(default_factory=list)

    def send(self, text: str, max_tokens: int = 1024) -> str:
        self.messages.append({"role": "user", "content": text})
        self._compact_if_needed()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=self.messages,
        )
        reply = text_of(response)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _compact_if_needed(self) -> None:
        tokens = count_tokens(self.client, self.messages, model=self.model, system=self.system)
        if tokens <= self.max_input_tokens:
            return

        split = self._split_index()
        if split == 0:
            return  # histórico curto demais para compactar; o chamador decide o que fazer

        old, recent = self.messages[:split], self.messages[split:]
        summary = self._summarize(old)
        # Mantém a alternância user/assistant exigida pela API.
        self.messages = [
            {"role": "user", "content": f"Resumo da conversa anterior:\n{summary}"},
            {"role": "assistant", "content": "Entendido, continuo a partir deste resumo."},
            *recent,
        ]

    def _split_index(self) -> int:
        """Índice do primeiro turno do usuário que deve ser mantido. 0 = nada a compactar."""
        user_turns = [i for i, m in enumerate(self.messages) if m["role"] == "user"]
        if len(user_turns) <= self.keep_recent_turns:
            return 0
        return user_turns[-self.keep_recent_turns]

    def _summarize(self, old: list[dict]) -> str:
        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
        response = self.client.messages.create(
            model=self.summary_model,
            max_tokens=500,
            system="Resuma a conversa preservando fatos, decisões, números e nomes.",
            messages=[{"role": "user", "content": transcript}],
        )
        return text_of(response)
