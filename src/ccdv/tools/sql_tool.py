"""Tool de consulta SQL segura.

A segurança vem do SQLite, não de regex sobre a string:
- `set_authorizer` permite apenas leitura (SELECT). INSERT/UPDATE/DELETE/DROP/PRAGMA/ATTACH
  são negados pelo próprio engine, mesmo que a string esteja mal formada ou ofuscada.
- `set_progress_handler` aborta a consulta após `timeout_seconds`.
- Só uma instrução por chamada (sqlite3 já recusa múltiplas statements em execute()).

Os guias que checam `"UPDATE" in query.upper()` erram nos dois sentidos:
bloqueiam `updated_at` (falso positivo) e deixam passar o que não está na lista.
"""

import sqlite3
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ccdv.tools.registry import ToolRegistry

MAX_ROWS = 100

_ALLOWED_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
}


class QueryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(max_length=1000, description="Consulta SQL. Somente SELECT.")
    timeout_seconds: int = Field(default=5, ge=1, le=30, description="Tempo máximo de execução.")


def _authorizer(action: int, arg1: Any, arg2: Any, db_name: Any, source: Any) -> int:
    return sqlite3.SQLITE_OK if action in _ALLOWED_ACTIONS else sqlite3.SQLITE_DENY


def run_query(conn: sqlite3.Connection, query: str, timeout_seconds: int = 5) -> str:
    deadline = time.monotonic() + timeout_seconds
    conn.set_authorizer(_authorizer)
    conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
    try:
        rows = conn.execute(query).fetchmany(MAX_ROWS)
    finally:
        conn.set_authorizer(None)
        conn.set_progress_handler(None, 0)
    return repr(rows)


def register_sql_tool(registry: ToolRegistry, conn: sqlite3.Connection) -> None:
    registry.register(
        name="database_query",
        description="Executa uma consulta SELECT no banco e devolve até 100 linhas.",
        input_model=QueryInput,
        func=lambda args: run_query(conn, args.query, args.timeout_seconds),
    )
