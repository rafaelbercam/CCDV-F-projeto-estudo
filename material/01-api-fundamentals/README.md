# Domínio 1 — Claude API Fundamentals (20%)

**Código:** `src/ccdv/fundamentals/` · **Testes:** `tests/test_fundamentals.py` · **Projeto 1:** `src/ccdv/fundamentals/conversation.py`

## Conceitos

**Messages API.** Cada chamada envia `model`, `max_tokens`, `messages` e, opcionalmente, `system`.
`messages` é uma lista de turnos com `role` (`user` ou `assistant`) e `content`. A resposta vem em `content`,
que é uma **lista de blocos** (`text`, `tool_use`...). Não assuma que `content[0].text` existe.

**Stateless.** A API não guarda histórico. Quem mantém a conversa é o seu código, que reenvia os turnos
anteriores a cada chamada. Isso é a origem de quase todo o custo de contexto.

**Streaming vs. não-streaming.**
- Streaming (`client.messages.stream`) entrega texto conforme é gerado. Melhora a latência *percebida*.
- Não-streaming devolve tudo de uma vez. Mais simples para processar resultado, e é o padrão para lote.
- O tempo total não muda muito. O que muda é quando o primeiro byte chega.

**Contagem de tokens.** `client.messages.count_tokens` diz quantos tokens de entrada uma requisição terá, sem gerar
resposta. Use para decidir compactação antes de estourar o limite.

**Escolha de modelo.** Família atual: Opus (mais capaz, mais caro e lento), Sonnet (equilíbrio), Haiku (rápido e barato).
A escolha se justifica com dados: qualidade na sua tarefa, latência, custo. Sem isso, "modelo melhor" não é argumento.

**Rate limits.** Limites por minuto de requisições e de tokens. Erro `429` pede backoff exponencial com jitter.
Não faça retry imediato em loop.

**Modelo não suporta feature.** Nem todo modelo suporta todas as features (ex.: certos recursos de tools, cache, thinking).
Confira a compatibilidade na doc antes de desenhar a solução.

## Cenários de prova (o que cobrar de si)

- Dado um requisito ("resposta em < 1s, custo baixo, tarefa de classificação"), escolher modelo e justificar.
- Dizer quando streaming é necessário e quando não é.
- Estimar tokens de uma requisição e decidir se cabe no limite.
- Identificar que um recurso não está disponível no modelo escolhido.
- Desenhar retry para `429` e erro `5xx`.

## Exercícios

1. Rode `ask` e `stream_text` com o mesmo prompt. Meça o tempo até o primeiro pedaço no streaming.
2. Leia `Conversation._split_index`. Por que o corte sempre cai num turno do *usuário*? O que quebraria se cortasse num `assistant`?
3. Adicione retry com backoff para `anthropic.RateLimitError`. Escreva o teste com um cliente falso que falha duas vezes.

## Autoavaliação

- [ ] Explico por que `content` é uma lista e como extrair só o texto.
- [ ] Sei que a API não guarda histórico e onde isso pesa no custo.
- [ ] Justifico a escolha de modelo com critérios, não com "o mais novo".
- [ ] Sei que `count_tokens` existe e para que serve.

Links relacionados: [[02-tool-design]] (tool use), [[04-optimization]] (custo e latência).
