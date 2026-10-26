"""Módulo 03 — servidor MCP com FastMCP, transporte stdio.

Rodar isolado:  uv run python -m ccdv.mcp_server.server

Ponto de atenção: quando uma tool levanta exceção, o FastMCP devolve o resultado com
`isError=True` e a mensagem. O cliente (e o Claude) recebe o erro sem derrubar o servidor.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ccdv-notes")

_notes: dict[str, str] = {}


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b


@mcp.tool()
def save_note(key: str, text: str) -> str:
    """Salva ou sobrescreve uma nota pela chave."""
    if not key.strip():
        raise ValueError("key não pode ser vazia")
    _notes[key] = text
    return f"salva: {key}"


@mcp.tool()
def get_note(key: str) -> str:
    """Devolve o texto de uma nota."""
    if key not in _notes:
        raise KeyError(f"nota não encontrada: {key}")
    return _notes[key]


@mcp.tool()
def list_notes() -> list[str]:
    """Lista as chaves de todas as notas, em ordem alfabética."""
    return sorted(_notes)


@mcp.tool()
def delete_note(key: str) -> str:
    """Remove uma nota pela chave."""
    if key not in _notes:
        raise KeyError(f"nota não encontrada: {key}")
    del _notes[key]
    return f"removida: {key}"


if __name__ == "__main__":
    mcp.run()  # transporte stdio por padrão
