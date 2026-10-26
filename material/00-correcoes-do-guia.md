# Correções ao guia-cert.md

O guia serve de ponto de partida, mas tem trechos desatualizados ou que não batem com as APIs reais.
Não copie os exemplos dele sem antes conferir aqui. Itens marcados com **verificar** dependem de documentação
que mudou depois do que consegui confirmar: confira na doc oficial antes do exame.

| # | Trecho do guia | Problema | O que usar no estudo |
|---|---|---|---|
| 1 | `claude-3-5-sonnet-20241022` em todos os exemplos; "Sempre use latest model (3.5 Sonnet > older)" | Modelo antigo e dica obsoleta | IDs da família atual, centralizados em `src/ccdv/client.py` |
| 2 | `from mcp import ClientSession, StdioTransport` / `StdioTransport(command=...)` | Não é a API do SDK Python oficial | `stdio_client` + `StdioServerParameters` (`src/ccdv/mcp_server/client.py`) |
| 3 | `pip install mcp` sem versão | Desde o `mcp` 2.x, `FastMCP` foi renomeado para `MCPServer`. Código da linha 1.x quebra | Fixar `mcp>=1.2,<2` (já feito no `pyproject.toml`) |
| 4 | "SSE é transport padrão, HTTP também suportado" | Mistura as coisas. SSE é transporte legado, e a spec atual privilegia Streamable HTTP. Para uso local, o comum é stdio | Estudar stdio (local) e Streamable HTTP (remoto). **verificar** a versão da spec |
| 5 | `validate_tool_input` que checa `"UPDATE" in query.upper()` | Falso positivo: `updated_at` é bloqueado. Falso negativo: qualquer escrita fora da lista passa (`PRAGMA`, `ATTACH`, `REPLACE`...) | Restringir no banco: autorizador do SQLite (`src/ccdv/tools/sql_tool.py`) e usuário de banco só com leitura |
| 6 | "Nunca confie em Claude para escapar SQL" | Correto, mas o guia não diz o que fazer | Parametrização + permissão mínima. Nunca montar SQL com texto do modelo |
| 7 | `validate_input` com regex de "union.*select", "drop table" | Blocklist de SQL não é defesa. Bloqueia textos legítimos e não bloqueia variações | Validação de tamanho e formato (`validation.py`) + defesa no ponto de execução |
| 8 | "PII detection é fuzzy" e `remove_pii` só com regex | Correto no diagnóstico, mas o guia não cobre CPF nem nomes | Regex para formatos conhecidos (inclui CPF) + detector dedicado para o resto (`pii.py`) |
| 9 | `tool_choice` ausente no exemplo de extração | Sem `tool_choice`, o modelo pode responder em texto e não chamar a tool | Forçar a tool com `tool_choice={"type": "tool", "name": ...}` (`projects/extraction.py`) |
| 10 | "Cache control requer acesso early access (verificar)" | Trate como histórico. **verificar** o status atual na doc | Assumir disponível; checar `usage` na resposta |
| 11 | "Caching economiza 90% de tokens se hit rate > 80%" | Número sem fonte. Leitura de cache é mais barata que entrada normal, mas escrita custa mais | Medir: `usage_report()` em `optimization/caching.py`. **verificar** preços |
| 12 | "Sonnet 10x melhor preço/perf que Opus" | Afirmação sem base. Depende da tarefa | Fazer benchmark com as suas evals (`optimization/benchmark.py`) |
| 13 | "Token counting é free" | Contagem tem endpoint próprio e limites próprios. **verificar** se é cobrada | Usar `count_tokens` para orçamento, sem assumir que é gratuita |
| 14 | Exemplo de cache com prompt curto | O cache só ativa acima de um tamanho mínimo por modelo. Abaixo disso, não há erro, só zero hit | Conferir o mínimo por modelo na doc. **verificar** |
| 15 | Especificações do exame (60 questões, 120 min, 720/1000, $125, 12 meses) | Não confirmei na fonte oficial | Conferir na página oficial de certificação antes de agendar |
| 16 | Exemplos usam só tool use para dados estruturados | Há também saída estruturada nativa da API. **verificar** o nome e status atual | Estudar as duas formas e quando cada uma é preferível |

## Como usar esta lista

Antes de cada módulo, leia a linha correspondente. Quando achar outra divergência, acrescente aqui com a
fonte usada. O material só fica confiável se cada afirmação tiver uma origem.
