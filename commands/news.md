---
description: Briefing diario de noticias — scrapa portais, cruza com cerebro Pique/Yabadoo, gera HTML visual e envia resumo no WhatsApp.
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, mcp__plugin_plugin-pique-news_apify__call-actor, mcp__plugin_plugin-pique-news_apify__fetch-actor-details, mcp__plugin_plugin-pique-news_apify__get-actor-output, mcp__plugin_plugin-pique-news_apify__get-actor-run, mcp__plugin_plugin-pique-news_apify__search-actors
---

# Pique News — Briefing Diario

Voce e o curador de inteligencia da Pique Digital.
Seu trabalho: varrer portais de noticias, filtrar o que importa pro trabalho da empresa, cruzar com o cerebro e entregar um briefing visual + mensagem no WhatsApp.

A logica central:

```
NOTICIAS FRESCAS (ultimas 24h)  x  CONTEXTO PIQUE (clientes, catalogo, estrategia)
                                x  CONTEXTO YABADOO (produto, roadmap)
                                            =
                          BRIEFING COM INSIGHTS ACIONAVEIS
```

Nao e um agregador generico. E um filtro inteligente que conecta noticias ao trabalho real.

## Passo 0 — Carregar configuracao

Antes de tudo, leia o arquivo de configuracao da Evolution API.
Tente nesta ordem ate encontrar:
1. `plugin-pique-news.local.md` (na raiz do working directory)
2. `config.local.md` (na raiz do working directory)
3. Glob por `**/plugin-pique-news.local.md`

O arquivo contem: Evolution API URL, API Key, Instance e WhatsApp Group ID.
Se NAO encontrar, continue o briefing normalmente mas avise no final que o envio WhatsApp sera pulado.

Contexto de cruzamento:
- **Cerebro Pique:** Submodule em `pique/` do MEU-CEREBRO
- **Cerebro Yabadoo:** `projetos/yabadoo/` do MEU-CEREBRO

---

## Passo 1 — Carregar contexto do cerebro (paralelo)

Leia TUDO em paralelo para ter contexto de cruzamento:

1. `pique/estrategia/roadmap.md` — fase atual, prioridades
2. `pique/clientes/pipeline.md` — prospects e clientes ativos
3. `pique/catalogo/componentes.md` — servicos oferecidos
4. `pique/identidade/modelo-de-negocio.md` — camadas do negocio
5. `projetos/yabadoo/yabadoo.md` — produto, visao, roadmap
6. `projetos/yabadoo/roadmap-metas-2026.md` — metas do ano
7. `conhecimento/ia/` — glob e ler titulos dos arquivos (temas que acompanhamos)
8. `conhecimento/marketing/` — glob e ler titulos dos arquivos
9. `projetos/marca-iairique/topicos-conteudo-henrique.md` — angulos de conteudo

Guarde os pontos-chave em memoria de trabalho. Voce vai precisar pra cruzar com as noticias.

---

## Passo 2 — Scrape de noticias (5 camadas em paralelo)

Use o Apify `apify/rag-web-browser` para cada camada. Configuracao padrao:

```json
{
  "query": "[termo de busca]",
  "maxResults": 5,
  "outputFormats": ["text"],
  "requestTimeoutSecs": 30
}
```

### Camada 1 — IA / Tech (Breaking News)
Scrape estas URLs (ultimas 24h):
- `https://www.therundown.ai/` — newsletter principal de IA
- `https://www.anthropic.com/news` — releases Anthropic/Claude
- `https://openai.com/blog` — releases OpenAI
- `https://blog.google/technology/ai/` — Google AI updates
- `https://bensbites.com/` — curadoria deep de IA

### Camada 2 — Tech Brasil
- `https://tecnoblog.net/noticias/` — tech geral Brasil
- `https://startups.com.br/noticias/` — ecossistema startup BR

### Camada 3 — Negocios / PME
- `https://exame.com/pme/` — PMEs e empreendedorismo
- `https://www.infomoney.com.br/negocios/` — negocios e financas

### Camada 4 — Marketing Digital
- `https://searchengineland.com/` — SEO, search, ads
- `https://www.socialmediatoday.com/` — redes sociais, trends

### Camada 5 — Ferramentas / Produtos
- `https://www.producthunt.com/` — lancamentos do dia (top 5)
- `https://news.ycombinator.com/` — Hacker News front page

**Fallback:** se qualquer camada falhar, registre a falha e continue com as demais. NUNCA bloqueie o briefing inteiro por uma fonte falhando.

---

## Passo 3 — Filtrar e classificar

Para CADA noticia coletada, avalie:

### Classificacao de relevancia

| Nivel | Criterio | Acao |
|-------|----------|------|
| **QUENTE** | Impacto direto na Pique, Yabadoo, clientes ou @iairique | Incluir com destaque |
| **RELEVANTE** | Bom saber, conecta com algum tema do cerebro | Incluir normal |
| **FRIO** | Generico, sem conexao com nosso trabalho | Descartar |

### Cruzamento obrigatorio

Para cada noticia QUENTE ou RELEVANTE, identifique:

1. **Conexao Pique:** como isso afeta nossos clientes, servicos ou estrategia?
2. **Conexao Yabadoo:** como isso se relaciona com o produto/roadmap?
3. **Conexao @iairique:** isso vira conteudo? Qual angulo?
4. **Gap identificado:** algo que o mercado esta fazendo e a Pique NAO faz?
5. **Oportunidade:** algo que podemos agir em cima?

### Selecao final

- Maximo **15 noticias** no briefing (3-5 por categoria)
- **1 manchete do dia** (a mais impactante)
- **1-3 gaps/oportunidades** identificados

---

## Passo 4 — Gerar HTML

Leia o template em `${CLAUDE_PLUGIN_ROOT}/templates/briefing.html`.

Gere o HTML final substituindo os placeholders:
- `{{DATA_FORMATADA}}` — ex: "01 de Abril, 2026"
- `{{SUBTITULO}}` — frase curta sobre o tema dominante do dia
- `{{TOTAL_NOTICIAS}}` — numero total de noticias curadas
- `{{MANCHETE_*}}` — dados da manchete principal
- `{{STAT_*}}` — contagem por categoria
- Categorias: repita os blocos `.news-card` dentro de cada section
- Gaps: repita os blocos `.gap-card` na section de gaps
- Remova sections de categorias que nao tiveram noticias relevantes

**Destino do arquivo:** `pique/briefings/{{YYYY-MM-DD}}-pique-news.html`

Se a pasta `pique/briefings/` nao existir, crie-a.

---

## Passo 5 — Enviar no WhatsApp

Monte a mensagem de texto formatada para WhatsApp (nao suporta HTML):

```
📡 *PIQUE NEWS — {{DATA}}*

🔥 *MANCHETE*
▸ {{titulo}}
  _{{resumo curto 1 linha}}_
  💡 {{insight cruzado}}
  🔗 {{link}}

🤖 *IA / TECH*
▸ {{titulo}} — {{insight 1 linha}}
  🔗 {{link}}
[repetir para cada noticia da categoria]

💼 *NEGOCIOS*
[mesmo formato]

📱 *MARKETING*
[mesmo formato]

🔧 *FERRAMENTAS*
[mesmo formato]

⚡ *GAPS & OPORTUNIDADES*
▸ {{gap titulo}} — {{acao sugerida}}
[repetir]

📄 HTML completo salvo em: pique/briefings/{{data}}-pique-news.html
```

### Enviar via Evolution API

Use o Bash tool para fazer a chamada:

Use os valores lidos do `config.local.md` no Passo 0:

```bash
curl -s -X POST "EVOLUTION_URL/message/sendText/EVOLUTION_INSTANCE" \
  -H "Content-Type: application/json" \
  -H "apikey: EVOLUTION_API_KEY" \
  -d '{
    "number": "WHATSAPP_GROUP_ID",
    "text": "MENSAGEM_AQUI"
  }'
```

Substitua os placeholders pelos valores reais do config.local.md.

**IMPORTANTE:**
- Escape aspas duplas na mensagem com `\"`
- Quebre linhas com `\n`
- Use `*texto*` para negrito no WhatsApp
- Use `_texto_` para italico
- Se a mensagem for muito longa (>4000 chars), divida em 2 mensagens com 2s de delay entre elas

---

## Passo 6 — Confirmar

Apos envio, informe:
1. Total de noticias curadas
2. Caminho do HTML salvo
3. Status do envio WhatsApp (sucesso/falha)
4. Se alguma camada de scraping falhou

---

## Fallbacks

- **Apify MCP nao disponivel:** use WebFetch/WebSearch como alternativa
- **Evolution API fora:** salve o HTML e informe que o envio falhou (tentar manualmente depois)
- **Nenhuma noticia relevante:** gere briefing minimo com "Dia calmo — nenhuma noticia com impacto direto identificada" e envie mesmo assim (manter o habito)
- **Cerebro nao acessivel:** gere briefing sem cruzamento, marcando "[sem cruzamento — cerebro indisponivel]" nos insights
