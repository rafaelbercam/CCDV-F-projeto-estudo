"""Módulo 02 — registro de tools: schema gerado por Pydantic, validação e erros estruturados.

Regras que este módulo aplica:
- O schema enviado ao Claude sai do modelo Pydantic (fonte única da verdade).
- `extra="forbid"` gera `additionalProperties: false`: campos inventados são rejeitados.
- Entrada inválida ou erro de execução NÃO levanta exceção até o usuário:
  vira `tool_result` com `is_error=True`, e o Claude pode corrigir e tentar de novo.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError


@dataclass
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    func: Callable[[Any], Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func: Callable[[Any], Any],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"tool já registrada: {name}")
        self._tools[name] = Tool(name, description, input_model, func)

    def schemas(self) -> list[dict]:
        """Lista no formato do parâmetro `tools` da Messages API."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_model.model_json_schema(),
            }
            for tool in self._tools.values()
        ]

    def execute(self, tool_use_id: str, name: str, raw_input: dict) -> dict:
        """Executa uma tool_use e devolve o bloco `tool_result` correspondente."""
        tool = self._tools.get(name)
        if tool is None:
            return _result(tool_use_id, f"Tool desconhecida: {name}", is_error=True)

        try:
            args = tool.input_model.model_validate(raw_input)
        except ValidationError as exc:
            # include_context=False evita objetos não serializáveis no erro.
            details = exc.errors(include_url=False, include_context=False)
            return _result(tool_use_id, f"Entrada inválida: {details}", is_error=True)

        try:
            output = tool.func(args)
        except Exception as exc:
            # Só o tipo do erro volta ao modelo: stack trace e detalhes internos não vazam.
            return _result(tool_use_id, f"Erro ao executar {name}: {type(exc).__name__}", is_error=True)

        return _result(tool_use_id, str(output), is_error=False)


def _result(tool_use_id: str, content: str, is_error: bool) -> dict:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
        "is_error": is_error,
    }
