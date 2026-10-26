# Domínio 4 — Optimization and Performance (20%)

**Código:** `src/ccdv/optimization/` · **Testes:** `tests/test_optimization.py`

## Conceitos

**Prompt caching.** Você marca um bloco (`cache_control: {"type": "ephemeral"}`) como cacheável. Nas chamadas
seguintes com o mesmo prefixo, esse bloco é lido do cache. Três pontos de prova:
- O cache vale para o **prefixo exato**. Mudar um caractere antes do bloco invalida tudo depois.
- Há um **tamanho mínimo** cacheável por modelo. Abaixo dele, não há erro, só zero hit.
- Escrever no cache custa mais que a entrada normal. Ler custa menos. Por isso o ganho depende de reuso.

**Ler o `usage`.** A resposta traz `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`
e `output_tokens`. Atenção: `input_tokens` **não inclui** os de cache. O total de entrada é a soma dos três
(`usage_report` faz isso). Errar essa conta é um erro clássico de prova.

**Batch.** Message Batches processa muitas requisições de forma assíncrona, com desconto em relação ao síncrono.
Cada item tem `custom_id` para correlacionar o resultado. Resultados podem vir com erro por item: trate cada um.
Use quando a latência não importa (classificação em massa, avaliação, backfill).

**Token budgeting.** Defina o orçamento por requisição: tamanho máximo de entrada, `max_tokens` de saída, e
quantos turnos de histórico entram. Orçamento não é só para custo; também controla latência.

**Latência.** Meça antes de otimizar. Olhe p50 e p95, não só a média: a cauda é o que o usuário sente.
Latência tem componentes: rede, fila, tempo até o primeiro token, tempo de geração. Cada um tem remédio diferente.

**Trade-off qualidade × custo × latência.** Modelo menor é mais rápido e barato, mas pode errar mais.
Modelo maior resolve mais, com custo maior. A decisão sai de uma eval com a sua tarefa, não de tabela.

**Monitoramento.** Registre tokens, cache hit ratio, latência e taxa de erro por rota. Sem isso, a regressão
aparece só na conta do fim do mês.

## Mapa do guia para o código

| Tema | Onde está |
|---|---|
| Cache de system prompt | `caching.py` → `cached_ask()` |
| Interpretação do `usage` | `caching.py` → `usage_report()` |
| Batch: montar, enviar, coletar | `batch.py` (`build_batch_requests`, `submit_batch`, `wait_for_batch`, `collect_results`) |
| Medir latência p50/p95 | `benchmark.py` → `time_calls()` |

## Exercícios

1. Monte um system prompt de pelo menos o tamanho mínimo do modelo que você usar (**verificar** o valor na doc). Rode duas vezes e compare `cache_read` e `cache_write`.
2. Altere uma palavra no início do system prompt. Confirme que o cache não é lido na segunda chamada.
3. Escreva um script que classifica 200 frases via batch. Compare custo estimado e tempo total com 200 chamadas síncronas.
4. Use `time_calls` para comparar Haiku e Sonnet na mesma tarefa. Decida qual usar e escreva a justificativa em uma linha, com números.
5. Projeto de otimização do guia (semana 7 e 8): implemente cache em 2 aplicações e registre o antes/depois.

## Autoavaliação

- [ ] Sei que `input_tokens` não inclui os tokens de cache e calculo o total certo.
- [ ] Sei o que invalida um cache (prefixo alterado) e por que o tamanho mínimo importa.
- [ ] Escolho entre síncrono e batch com critério de latência.
- [ ] Reporto p50 e p95, não só a média.

Links relacionados: [[01-api-fundamentals]] (contagem de tokens), [[02-tool-design]] (tool com retorno grande encarece contexto).
