"""Cliente falso que imita a forma das respostas do SDK. Permite testar sem rede e sem custo."""

from types import SimpleNamespace as NS
from typing import Any, Callable


def text_response(text: str, *, stop_reason: str = "end_turn", usage: Any = None) -> NS:
    return NS(
        content=[NS(type="text", text=text)],
        stop_reason=stop_reason,
        usage=usage or usage_obj(),
    )


def tool_use_response(*calls: tuple[str, str, dict]) -> NS:
    """calls: lista de (tool_use_id, nome, input)."""
    blocks = [NS(type="tool_use", id=i, name=n, input=inp) for i, n, inp in calls]
    return NS(content=blocks, stop_reason="tool_use", usage=usage_obj())


def usage_obj(
    input_tokens: int = 10,
    output_tokens: int = 5,
    cache_read: int = 0,
    cache_write: int = 0,
) -> NS:
    return NS(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read,
        cache_creation_input_tokens=cache_write,
    )


class _Stream:
    def __init__(self, chunks: list[str]) -> None:
        self.text_stream = iter(chunks)

    def __enter__(self) -> "_Stream":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _Messages:
    def __init__(self, parent: "FakeClient") -> None:
        self._p = parent
        self.batches = NS(create=self._batch_create, retrieve=None, results=None)

    def create(self, **kwargs: Any) -> Any:
        # Copia as mensagens no momento da chamada: o código sob teste muta a mesma lista depois.
        self._p.calls.append({**kwargs, "messages": list(kwargs.get("messages", []))})
        if self._p.responder is not None:
            return self._p.responder(kwargs)
        if not self._p.responses:
            raise AssertionError("FakeClient sem respostas programadas")
        return self._p.responses.pop(0)

    def count_tokens(self, **kwargs: Any) -> NS:
        counter: Callable[[list[dict]], int] = self._p.token_count
        return NS(input_tokens=counter(kwargs["messages"]))

    def stream(self, **kwargs: Any) -> _Stream:
        self._p.calls.append(kwargs)
        return _Stream(self._p.stream_chunks)

    def _batch_create(self, **kwargs: Any) -> NS:
        self._p.calls.append({"batch": kwargs})
        return NS(id="msgbatch_fake")


class FakeClient:
    """
    responses: respostas devolvidas por messages.create, na ordem.
    token_count: função(messages) -> int, para simular contagem de tokens.
    stream_chunks: pedaços devolvidos por messages.stream.
    """

    def __init__(
        self,
        responses: list[Any] | None = None,
        token_count: Callable[[list[dict]], int] | int = 10,
        stream_chunks: list[str] | None = None,
        responder: Callable[[dict], Any] | None = None,
    ) -> None:
        self.responses = list(responses or [])
        self.responder = responder  # se definido, decide a resposta pelos kwargs (ex.: pelo modelo)
        self.calls: list[dict] = []
        self.stream_chunks = stream_chunks or []
        if isinstance(token_count, int):
            value = token_count
            self.token_count = lambda _messages: value
        else:
            self.token_count = token_count
        self.messages = _Messages(self)
