import asyncio

from ccdv.mcp_server.client import call_tools, list_tool_names


def test_server_exposes_five_tools():
    names = asyncio.run(list_tool_names())
    assert set(names) == {"add_numbers", "save_note", "get_note", "list_notes", "delete_note"}


def test_round_trip_over_stdio():
    outputs = asyncio.run(
        call_tools(
            [
                ("save_note", {"key": "ideia", "text": "estudar MCP"}),
                ("get_note", {"key": "ideia"}),
                ("add_numbers", {"a": 2, "b": 3}),
            ]
        )
    )
    assert outputs[0] == (False, "salva: ideia")
    assert outputs[1] == (False, "estudar MCP")
    assert outputs[2][0] is False


def test_error_is_reported_as_is_error_without_crashing_server():
    outputs = asyncio.run(
        call_tools(
            [
                ("get_note", {"key": "inexistente"}),
                ("list_notes", {}),  # o servidor continua vivo depois do erro
            ]
        )
    )
    assert outputs[0][0] is True
    assert outputs[1][0] is False
