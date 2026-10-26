from ccdv.fundamentals.chat import ask, count_tokens, stream_text, text_of
from ccdv.fundamentals.conversation import Conversation
from ccdv.client import MODEL_HAIKU
from tests.fakes import FakeClient, text_response, tool_use_response


def test_ask_returns_text_and_sends_user_message():
    client = FakeClient([text_response("4")])
    assert ask(client, "2+2?") == "4"
    assert client.calls[0]["messages"] == [{"role": "user", "content": "2+2?"}]


def test_text_of_ignores_non_text_blocks():
    resp = tool_use_response(("t1", "x", {}))
    assert text_of(resp) == ""


def test_stream_yields_chunks_in_order():
    client = FakeClient(stream_chunks=["Olá", ", ", "mundo"])
    assert "".join(stream_text(client, "oi")) == "Olá, mundo"


def test_count_tokens_returns_input_tokens():
    client = FakeClient(token_count=lambda m: 42)
    assert count_tokens(client, [{"role": "user", "content": "x"}]) == 42


def test_conversation_does_not_compact_under_limit():
    client = FakeClient([text_response("oi")], token_count=5)
    conv = Conversation(client=client, max_input_tokens=100)
    conv.send("olá")
    assert len(conv.messages) == 2  # user + assistant
    assert len(client.calls) == 1   # sem chamada de resumo


def test_conversation_compacts_and_keeps_alternation():
    # Cada turno do usuário conta como 1000 tokens: o histórico estoura em seguida.
    def count(messages):
        return 1000 * sum(1 for m in messages if m["role"] == "user")

    def responder(kwargs):
        if kwargs["model"] == MODEL_HAIKU:
            return text_response("RESUMO")
        return text_response("resposta")

    client = FakeClient(token_count=count, responder=responder)
    conv = Conversation(client=client, max_input_tokens=3000, keep_recent_turns=2)

    for i in range(6):
        conv.send(f"pergunta {i}")

    roles = [m["role"] for m in conv.messages]
    assert all(a != b for a, b in zip(roles, roles[1:])), "user/assistant devem alternar"
    assert conv.messages[0]["content"].startswith("Resumo da conversa anterior")
    assert conv.messages[-2]["content"] == "pergunta 5"
    # O resumo usa o modelo barato, não o modelo principal.
    summary_calls = [c for c in client.calls if c.get("model") == MODEL_HAIKU]
    assert len(summary_calls) >= 1
