"""Loop agentico: o Claude pede tools, executamos, devolvemos resultados, até responder em texto."""

from typing import Any

from ccdv.client import DEFAULT_MODEL
from ccdv.fundamentals.chat import text_of
from ccdv.tools.registry import ToolRegistry


def run_with_tools(
    client: Any,
    registry: ToolRegistry,
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_turns: int = 5,
    max_tokens: int = 1024,
) -> str:
    """Roda até `end_turn`. `max_turns` limita custo e loops infinitos."""
    messages: list[dict] = [{"role": "user", "content": prompt}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=registry.schemas(),
            messages=messages,
        )
        # A resposta do assistente (com os blocos tool_use) precisa voltar ao histórico,
        # senão o tool_result seguinte não tem a tool_use correspondente.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return text_of(response)

        results = [
            registry.execute(block.id, block.name, block.input)
            for block in response.content
            if block.type == "tool_use"
        ]
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"Limite de {max_turns} turnos atingido sem resposta final")
