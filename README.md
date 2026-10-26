# CCDV-F — Projeto de estudo

Estudo ponto a ponto para a certificação **Claude Certified Developer - Foundations**. O guia de origem está em
[`guide-cert.md`](guide-cert.md). Este repositório junta o **material** (teoria e exercícios) e o **código executável**
(exemplos, projetos e testes) de cada domínio.

## Estrutura

```
material/                  teoria, cenários de prova e exercícios, uma pasta por domínio
  00-correcoes-do-guia.md  divergências do guia com a realidade das APIs (leia primeiro)
  01-api-fundamentals/     Messages API, streaming, tokens, modelos      (20%)
  02-tool-design/          tool use, JSON Schema, erros, loop            (22%)
  03-mcp/                  arquitetura, transporte, servidor e cliente   (18%)
  04-optimization/         prompt caching, batch, latência, custo        (20%)
  05-security/             validação, PII, rate limit, audit, segredos   (20%)

src/ccdv/                  código executável, uma pasta por domínio
  client.py                cliente e IDs de modelo (fonte única)
  fundamentals/            chat, streaming, tokens; Projeto 1 (conversation.py)
  tools/                   registro, loop agentico, tool SQL segura
  mcp_server/              servidor FastMCP e cliente stdio
  optimization/            cache, batch, benchmark
  security/                validação, PII, rate limit, audit
  projects/extraction.py   Projeto 2: extração com validação, retry e PII

tests/                     testes offline (cliente falso) + live (API real, opcional)
```

Cada `material/<domínio>/README.md` aponta para o código e os testes correspondentes.

## Como rodar

```bash
# 1. dependências (uv cria o .venv)
uv sync

# 2. testes offline: não gastam tokens e não precisam de chave
uv run pytest

# 3. testes com a API real (opcional, gasta poucos tokens)
cp .env.example .env        # preencha ANTHROPIC_API_KEY
uv run pytest -m live

# 4. servidor MCP isolado (para conectar em um host MCP)
uv run python -m ccdv.mcp_server.server
```

## Cronograma (8–10 semanas, do guia)

| Semana | Foco | Material | Código / entrega |
|---|---|---|---|
| 1–2 | Fundação API | `01-api-fundamentals` | `fundamentals/`, Projeto 1 |
| 3–4 | Tool design | `02-tool-design` | `tools/`, Projeto 3 (base) |
| 5–6 | MCP | `03-mcp` | `mcp_server/`, Projeto 4 (completar com 5+ tools e auth) |
| 7–8 | Otimização | `04-optimization` | `optimization/`, relatório de benchmark |
| 9–10 | Segurança e prova | `05-security` | `security/`, Projeto 2, simulados |

## Critério de prontidão (do guia)

- [ ] 3+ aplicações Claude funcionando (ou simuladas)
- [ ] 2+ tools complexas com validação completa
- [ ] 1+ servidor MCP implementado
- [ ] Cache implementado em uma aplicação real
- [ ] Filtro de entrada/saída e audit log funcionando
- [ ] 700+/1000 em 2 simulados
- [ ] Diferenças entre Sonnet, Opus e Haiku explicadas com dados
- [ ] Diagnóstico de latência e custo feito num caso real

## Próximos passos sugeridos

1. Ler `material/00-correcoes-do-guia.md` antes de tudo.
2. Rodar `uv run pytest` e entender cada teste que falha ao alterar o código.
3. Preencher os exercícios de cada domínio em `material/<domínio>/`.
4. Fazer os simulados. Os exercícios de prova ainda não estão escritos: esse é o próximo passo natural.
