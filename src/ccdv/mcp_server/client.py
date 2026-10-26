"""Módulo 03 — cliente MCP (Python SDK) que sobe o servidor de notas via stdio."""

import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["-m", "ccdv.mcp_server.server"],
)


async def list_tool_names(params: StdioServerParameters = SERVER_PARAMS) -> list[str]:
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return [tool.name for tool in result.tools]


async def call_tools(
    calls: list[tuple[str, dict[str, Any]]],
    params: StdioServerParameters = SERVER_PARAMS,
) -> list[tuple[bool, str]]:
    """Executa uma sequência de chamadas na mesma sessão. Devolve (is_error, texto) por chamada."""
    outputs: list[tuple[bool, str]] = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for name, arguments in calls:
                result = await session.call_tool(name, arguments)
                text = result.content[0].text if result.content else ""
                outputs.append((bool(result.isError), text))
    return outputs
