# Domínio 2 — Tool Design and Integration (22%)

**Código:** `src/ccdv/tools/` · **Testes:** `tests/test_tools.py` · **Projeto 3 (base):** `src/ccdv/tools/loop.py`
**Projeto 2 (saída estruturada):** `src/ccdv/projects/extraction.py`

Este é o domínio de maior peso. Trate tool use como o centro do estudo.

## Conceitos

**Ciclo de tool use.**
1. Você envia `tools` (nome, descrição, `input_schema`) e as mensagens.
2. O Claude responde com `stop_reason == "tool_use"` e um bloco `tool_use` (com `id`, `name`, `input`).
3. Você executa a função localmente.
4. Você devolve um bloco `tool_result` com o mesmo `tool_use_id`, dentro de uma mensagem `user`.
5. Repete até `stop_reason == "end_turn"`.

O ponto que mais cai: **a resposta do assistente com o `tool_use` precisa voltar ao histórico** antes do `tool_result`.
Sem ele, a API rejeita a requisição (`loop.py` faz isso).

**JSON Schema como contrato.** A `description` de cada campo é lida pelo modelo. Ela é documentação de verdade:
escreva como se fosse para um desenvolvedor que nunca viu a API. Use `enum`, `minimum`, `maximum`, `maxLength`
para restringir. `additionalProperties: false` rejeita campos inventados.

**Validação em duas camadas.** O schema orienta o modelo; a validação no seu código garante. Nunca confie só no schema:
ele é uma sugestão para o modelo, não uma garantia de execução.

**Erros como resultado, não como exceção.** Entrada inválida ou falha de execução devem voltar como
`tool_result` com `is_error: true`. O modelo lê o erro e pode corrigir os argumentos. Levantar exceção
até o usuário quebra o fluxo. Mas não vaze stack trace nem detalhes internos (`registry.py` só devolve o tipo do erro).

**Limites do loop.** Sem `max_turns`, um modelo confuso pode chamar tools para sempre. Sempre limite.

**Quando tool é ineficiente.** Tool para algo que o modelo sabe responder sem dados externos desperdiça latência.
Tool com retorno gigante encarece o contexto. Retorne só o necessário, paginado.

**Segurança de tools.** Tool que escreve, apaga ou acessa dados sensíveis precisa de autorização *fora* do modelo.
O modelo pode ser induzido por texto malicioso (prompt injection vindo de um documento ou página) a pedir qualquer ação.
A defesa está em limitar o que a tool pode fazer, não em confiar no modelo.

**Versionamento.** Mudar o nome ou o tipo de um campo quebra quem já usa a tool. Adicione campos opcionais e
crie uma tool nova (`search_v2`) quando a mudança for incompatível.

## Mapa do guia para o código

| Tema do guia | Onde está |
|---|---|
| Schema a partir de Pydantic, `extra="forbid"` | `ToolRegistry.schemas()` |
| Validação de entrada | `ToolRegistry.execute()` |
| Erro estruturado para o modelo | `_result(..., is_error=True)` |
| Tool SQL segura | `sql_tool.py`: autorizador + timeout, não regex |
| Loop com limite de turnos | `run_with_tools()` |
| Saída estruturada por tool forçada | `projects/extraction.py` (`tool_choice`) |

## Exercícios

1. Escreva um schema para uma API REST de pedidos (criar, consultar por id, cancelar). Quais campos são obrigatórios? Quais têm `enum`?
2. Adicione uma tool `get_weather` ao registro. Escreva dois testes: entrada válida e entrada com campo extra.
3. Rode o teste `test_writes_are_denied`. Depois, tente burlar o autorizador com `WITH ... DELETE` ou `REPLACE INTO`. Ele bloqueia? Por quê?
4. Escreva um cenário de tool chaining: a saída da tool A alimenta a tool B. Onde fica o `tool_use_id` de cada uma?

## Autoavaliação

- [ ] Descrevo os cinco passos do ciclo de tool use de cabeça.
- [ ] Sei por que a mensagem do assistente volta ao histórico antes do `tool_result`.
- [ ] Separo erro de entrada, erro de execução e tool inexistente.
- [ ] Explico por que validar só com regex ou só com o schema não basta.

Links relacionados: [[05-security]] (autorização e injeção), [[03-mcp]] (tools expostas via protocolo).
