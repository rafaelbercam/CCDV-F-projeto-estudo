"""Projeto 2 — extração de dados com saída estruturada, validação, retry e remoção de PII.

Estratégia: forçar o Claude a "chamar" uma tool cujo input_schema é o modelo Pydantic.
A resposta vira um dicionário que validamos. Se falhar, devolvemos o erro ao modelo
como tool_result com is_error=True e tentamos de novo, até `max_attempts`.
"""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ccdv.client import DEFAULT_MODEL
from ccdv.security.pii import redact_pii
from ccdv.security.validation import validate_user_text

TOOL_NAME = "record_invoice"


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vendor: str = Field(min_length=1, max_length=200, description="Nome do fornecedor.")
    total: float = Field(ge=0, description="Valor total, sem separador de milhar.")
    currency: Literal["BRL", "USD", "EUR"]
    issued_on: date = Field(description="Data de emissão no formato AAAA-MM-DD.")


class ExtractionError(RuntimeError):
    pass


def _tool_definition() -> dict:
    return {
        "name": TOOL_NAME,
        "description": "Registra os dados extraídos de uma nota fiscal.",
        "input_schema": Invoice.model_json_schema(),
    }


def extract_invoice(
    client: Any,
    text: str,
    model: str = DEFAULT_MODEL,
    max_attempts: int = 3,
) -> Invoice:
    check = validate_user_text(text)
    if not check.ok:
        raise ValueError(f"entrada rejeitada: {check.reason}")

    messages: list[dict] = [{"role": "user", "content": f"Extraia os dados da nota:\n{text}"}]
    last_error = ""

    for _ in range(max_attempts):
        response = client.messages.create(
            model=model,
            max_tokens=512,
            tools=[_tool_definition()],
            tool_choice={"type": "tool", "name": TOOL_NAME},
            messages=messages,
        )
        block = next(b for b in response.content if b.type == "tool_use")

        try:
            invoice = Invoice.model_validate(block.input)
        except ValidationError as exc:
            last_error = str(exc)
            # Devolve o erro ao modelo para ele corrigir a própria saída.
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Erro de validação: {exc.errors(include_url=False, include_context=False)}",
                            "is_error": True,
                        }
                    ],
                }
            )
            continue

        # Saída passa pelo filtro de PII antes de sair do sistema.
        invoice.vendor = redact_pii(invoice.vendor).text
        return invoice

    raise ExtractionError(f"Falhou após {max_attempts} tentativas: {last_error}")
