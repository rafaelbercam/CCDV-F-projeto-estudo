# Domínio 3 — Model Context Protocol (18%)

**Código:** `src/ccdv/mcp_server/` · **Testes:** `tests/test_mcp.py`
**Comandos:** `uv run python -m ccdv.mcp_server.server` (sobe o servidor) · `uv run pytest tests/test_mcp.py`

## Conceitos

**Arquitetura.** MCP separa três papéis: o **host** (a aplicação com o Claude, ex.: Claude Desktop ou seu app),
o **client** (conector que o host mantém com um servidor, uma sessão por servidor) e o **server** (expõe tools,
resources e prompts). Um host pode ter vários clients.

**Transporte.**
- **stdio:** o servidor é um subprocesso; comunicação por stdin/stdout. Comum para uso local.
- **Streamable HTTP:** servidor remoto por HTTP. É o transporte que a spec atual privilegia para remoto.
- **SSE:** transporte mais antigo, citado no guia. Conhecer, mas não tratar como padrão novo. **verificar** a spec vigente.

**Ciclo de vida.** Conexão → `initialize` (troca de versão e capacidades) → operações (`tools/list`, `tools/call`)
→ encerramento. Não chame operações antes de `initialize`.

**Definição de tool.** Nome, descrição e `inputSchema` (JSON Schema). É o mesmo conceito de tool use da API,
com um formato de transporte. Por isso o guia diz que deve "match Claude tool schema": na prática, o host
converte uma para a outra.

**Erros.** Tool que falha devolve resultado com `isError: true`, não derruba o servidor.
Falha de protocolo (JSON inválido, método inexistente) é um erro JSON-RPC. São casos diferentes; saiba distinguir.

**Confiabilidade.** Servidor stdio morre junto com o host. Timeout e reconexão são responsabilidade do client.
Chamadas com efeito colateral (criar, apagar) precisam ser idempotentes ou ter confirmação.

**Escalabilidade.** Stdio escala com um processo por cliente. Remoto escala com balanceamento e estado externo
(o estado em memória do `server.py` não sobrevive a múltiplas réplicas: é de propósito, para estudo).

**Versão do SDK.** `FastMCP` é da linha 1.x do SDK Python. A 2.x renomeou para `MCPServer`. Fixe a versão.

## Mapa do guia para o código

| Tema | Onde está |
|---|---|
| Servidor com 5 tools | `server.py` (`add_numbers`, `save_note`, `get_note`, `list_notes`, `delete_note`) |
| Cliente stdio | `client.py` (`stdio_client` + `ClientSession`) |
| Erro de tool sem derrubar servidor | `test_error_is_reported_as_is_error_without_crashing_server` |

## Exercícios

1. Adicione uma tool `search_notes(term)` que devolve as chaves cujo texto contém `term`. Escreva o teste de cliente.
2. Provoque um erro de protocolo: chame uma tool com argumento do tipo errado. Compare com um erro de execução. Qual campo muda?
3. Projeto 4 do guia: leve o servidor a 5+ tools com mensagens de erro úteis e um mecanismo de autenticação
   (ex.: token no `params` de inicialização, validado no servidor). Documente onde o segredo fica (nunca no código).
4. Desenhe um diagrama host ↔ client ↔ server para o seu caso e salve em `material/03-mcp/arquitetura.md`.

## Autoavaliação

- [ ] Nomeio os três papéis (host, client, server) e a diferença entre eles.
- [ ] Sei escolher stdio ou HTTP para um caso dado, com a justificativa.
- [ ] Diferencio `isError` de erro JSON-RPC.
- [ ] Sei por que o `initialize` vem antes de qualquer tool.

Links relacionados: [[02-tool-design]], [[05-security]] (autenticação do servidor).
