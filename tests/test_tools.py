import sqlite3

import pytest
from pydantic import BaseModel, ConfigDict, Field

from ccdv.tools.loop import run_with_tools
from ccdv.tools.registry import ToolRegistry
from ccdv.tools.sql_tool import register_sql_tool
from tests.fakes import FakeClient, text_response, tool_use_response


class AddInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    a: int = Field(ge=0)
    b: int = Field(ge=0)


def make_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register("add", "Soma dois inteiros positivos.", AddInput, lambda args: args.a + args.b)

    def boom(_args):
        raise ZeroDivisionError("segredo interno")

    reg.register("boom", "Sempre falha.", AddInput, boom)
    return reg


def test_schema_forbids_extra_fields():
    schema = make_registry().schemas()[0]["input_schema"]
    assert schema["additionalProperties"] is False


def test_valid_input_executes():
    result = make_registry().execute("t1", "add", {"a": 2, "b": 3})
    assert result == {"type": "tool_result", "tool_use_id": "t1", "content": "5", "is_error": False}


def test_invalid_input_becomes_error_result_not_exception():
    result = make_registry().execute("t2", "add", {"a": -1, "b": 3, "extra": 1})
    assert result["is_error"] is True
    assert "Entrada inválida" in result["content"]


def test_execution_error_hides_internal_message():
    result = make_registry().execute("t3", "boom", {"a": 1, "b": 1})
    assert result["is_error"] is True
    assert "ZeroDivisionError" in result["content"]
    assert "segredo interno" not in result["content"]


def test_unknown_tool_is_error_result():
    result = make_registry().execute("t4", "nope", {})
    assert result["is_error"] is True


def test_duplicate_registration_rejected():
    reg = make_registry()
    with pytest.raises(ValueError):
        reg.register("add", "x", AddInput, lambda a: a)


def test_loop_runs_tool_then_returns_text():
    client = FakeClient(
        [
            tool_use_response(("tu_1", "add", {"a": 2, "b": 2})),
            text_response("O resultado é 4."),
        ]
    )
    answer = run_with_tools(client, make_registry(), "quanto é 2+2?")
    assert answer == "O resultado é 4."

    # O segundo pedido precisa conter o tool_result com o id correto.
    second_messages = client.calls[1]["messages"]
    tool_result = second_messages[-1]["content"][0]
    assert tool_result["tool_use_id"] == "tu_1"
    assert tool_result["content"] == "4"


def test_loop_stops_at_max_turns():
    client = FakeClient([tool_use_response(("x", "add", {"a": 1, "b": 1}))] * 3)
    with pytest.raises(RuntimeError):
        run_with_tools(client, make_registry(), "loop", max_turns=3)


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente TEXT, valor REAL, updated_at TEXT);
        INSERT INTO pedidos (cliente, valor, updated_at) VALUES ('ana', 10.5, '2026-01-01'), ('bruno', 3, '2026-01-02');
        """
    )
    yield conn
    conn.close()


@pytest.fixture
def sql_registry(db):
    reg = ToolRegistry()
    register_sql_tool(reg, db)
    return reg


def test_select_works(sql_registry):
    result = sql_registry.execute("q1", "database_query", {"query": "SELECT cliente FROM pedidos ORDER BY id"})
    assert result["is_error"] is False
    assert "ana" in result["content"] and "bruno" in result["content"]


def test_column_named_like_keyword_is_allowed(sql_registry):
    # Falso positivo do filtro por substring: 'updated_at' contém 'UPDATE'.
    result = sql_registry.execute("q2", "database_query", {"query": "SELECT updated_at FROM pedidos"})
    assert result["is_error"] is False


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO pedidos (cliente) VALUES ('x')",
        "UPDATE pedidos SET valor = 0",
        "DELETE FROM pedidos",
        "DROP TABLE pedidos",
        "SELECT 1; DELETE FROM pedidos",
        "PRAGMA table_info(pedidos)",
    ],
)
def test_writes_are_denied(sql_registry, db, query):
    result = sql_registry.execute("q3", "database_query", {"query": query})
    assert result["is_error"] is True
    # A tabela continua intacta.
    assert db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 2


def test_runaway_query_is_interrupted(sql_registry):
    slow = (
        "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) "
        "SELECT COUNT(*) FROM c"
    )
    result = sql_registry.execute("q4", "database_query", {"query": slow, "timeout_seconds": 1})
    assert result["is_error"] is True


def test_authorizer_is_removed_after_query(sql_registry, db):
    sql_registry.execute("q5", "database_query", {"query": "SELECT 1"})
    db.execute("CREATE TABLE auditoria (x INTEGER)")  # conexão livre de novo
