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
- **Cerebro Yabadoo:** `pique/produto-yabadoo/` do MEU-CEREBRO

---

## Passo 1 — Carregar contexto do cerebro (paralelo)

Leia TUDO em paralelo para ter contexto de cruzamento:

1. `pique/estrategia/roadmap.md` — fase atual, prioridades
2. `pique/clientes/pipeline.md` — prospects e clientes ativos
3. `pique/catalogo/componentes.md` — servicos oferecidos
4. `pique/identidade/modelo-de-negocio.md` — camadas do negocio
5. `pique/produto-yabadoo/yabadoo.md` — produto, visao, roadmap
6. `pique/produto-yabadoo/roadmap-metas-2026.md` — metas do ano
7. `conhecimento/ia/` — glob e ler titulos dos arquivos (temas que acompanhamos)
8. `conhecimento/marketing/` — glob e ler titulos dos arquivos
9. `projetos/marca-iairique/topicos-conteudo-henrique.md` — angulos de conteudo

Guarde os pontos-chave em memoria de trabalho. Voce vai precisar pra cruzar com as noticias.

---

## Passo 1.5 — Carregar memoria de briefings anteriores

Antes de buscar noticias novas, leia o que ja foi reportado:

1. **Glob** `pique/briefings/*-pique-news.html` — liste todos os briefings existentes.
2. **Leia os 3 mais recentes** (por data no nome do arquivo). Se houver menos de 3, leia todos. Se nao houver nenhum, pule este passo inteiro.
3. **De cada HTML, extraia:**
   - Bloco `<!-- PIQUE-NEWS-METADATA ... -->` (se existir) — parse direto dele
   - Se NAO tiver bloco de metadata (briefings antigos): ler os textos dentro de `.news-headline`, `.news-insight`, `.gap-title` + `.gap-action` do HTML
4. **Monte 3 listas de trabalho:**

### a) Noticias ja reportadas (titulos dos ultimos 3 dias)

Usar pra DEDUPLICAR no Passo 3:
- Se a mesma noticia (mesmo tema/evento) aparecer no scrape de hoje, NAO incluir de novo
- EXCECAO: se tem DESDOBRAMENTO NOVO (update, reacao do mercado, dados novos), incluir com tag "CONTINUACAO de DD/MM: [o que mudou]"

### b) Tendencias em formacao (temas que apareceram em 2+ briefings)

- Se o mesmo tema aparece em dias diferentes (ex: "computer use" em D-1 e D-2), e uma TENDENCIA
- Nomear explicitamente e acompanhar evolucao
- Formato: "TENDENCIA: [nome] — Dia 1 (DD/MM): [o que aconteceu] → Dia 2 (DD/MM): [o que evoluiu] → Hoje: [novo desenvolvimento]"

### c) Gaps e acoes pendentes (gaps dos briefings anteriores)

- Listar TODOS os gaps abertos dos ultimos 3 briefings
- No Passo 3, verificar se alguma noticia de hoje RESOLVE ou AVANCA algum gap anterior
- Se um gap apareceu em 3+ briefings sem acao concreta, ESCALAR: marcar como "GAP CRONICO" e sugerir inclusao no planejamento semanal
- Maximo 3 gaps cronicos por briefing — priorizar os mais antigos

Esse contexto vai ser usado nos Passos 3, 4 e 5.

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

### Cruzamento VERIFICAVEL (obrigatorio)

Para cada noticia QUENTE ou RELEVANTE, o cruzamento NAO pode ser generico. Cada insight deve apontar ARQUIVO + SECAO + ACAO CONCRETA:

1. **Conexao Pique — apontar arquivo:**
   - Se afeta servico: "`catalogo/componentes.md` — componente #X pode [acao]"
   - Se afeta cliente: "`clientes/pipeline.md` — prospect [nome] se beneficia porque [razao]"
   - Se afeta estrategia: "`estrategia/roadmap.md` — fase [X] precisa considerar [impacto]"
   - Se NAO conecta com nenhum arquivo especifico: admitir "sem conexao direta com Pique"

2. **Conexao Yabadoo — apontar roadmap:**
   - Se afeta produto: "`produto-yabadoo/roadmap-metas-2026.md` — fase [X], [impacto concreto]"
   - Se afeta posicionamento: "`produto-yabadoo/yabadoo.md` — secao [X], [como muda]"
   - Se NAO conecta: admitir "sem conexao direta com Yabadoo"

3. **Conexao @iairique — apontar topico:**
   - Se vira conteudo: "`topicos-conteudo-henrique.md` — topico [numero]: [nome]. Formato sugerido: [carrossel/reels/video]. Hook: [frase de abertura]"
   - Se NAO vira conteudo: omitir (nao forcar conexao)

4. **Continuidade com briefings anteriores** (obrigatorio se Passo 1.5 executou):
   - E repeticao? → NAO incluir. Excecao: desdobramento novo, marcar "CONTINUACAO de DD/MM: [o que mudou]"
   - Faz parte de tendencia? → Marcar "TENDENCIA [nome] — dia [N]: [evolucao]"
   - Resolve/avanca gap anterior? → Marcar "ATUALIZA gap de DD/MM: [nome do gap] — [status novo]"

5. **Gap identificado — acao concreta:**
   - Cada gap deve ter: QUEM faz + O QUE faz + SUGESTAO de quando
   - Exemplo bom: "→ Henrique: criar draft do componente AI Search em `catalogo/componentes.md`. Marco: incluir no pitch de prospeccao ate sexta."
   - Exemplo ruim: "→ Ficar de olho nessa tendencia." (vago demais — reescrever com acao concreta)

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

### Secao extra: Tendencias em Andamento

Se o Passo 1.5 identificou tendencias (tema em 2+ briefings), adicionar uma section `#tendencias` no HTML ENTRE a ultima categoria e os gaps. Usar o bloco de tendencia do template (`templates/briefing.html` section `#tendencias`). Cada tendencia mostra: nome, timeline (dia 1 → dia 2 → hoje), e status atual.

Se NAO houver tendencias (primeiro briefing ou nenhum tema repetido), omitir a section inteira.

### Bloco de metadata (obrigatorio)

Antes do `</body>`, SEMPRE inserir um bloco de metadata em comentario HTML para facilitar leitura por briefings futuros:

```html
<!-- PIQUE-NEWS-METADATA
data: YYYY-MM-DD
total: [numero de noticias curadas]
manchete: [titulo da manchete principal]
tendencias-ativas: [lista separada por virgula, ou "nenhuma"]
gaps-abertos: [lista separada por |, ou "nenhum"]
gaps-resolvidos: [lista separada por |, ou "nenhum"]
noticias-chave: [titulos curtos separados por |]
-->
```

Esse bloco permite que o Passo 1.5 de execucoes futuras leia apenas as ultimas linhas do HTML em vez do arquivo inteiro.

### Destino do arquivo

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

📈 *TENDENCIAS (acompanhamento)*
▸ {{tendencia}} — dia {{N}}: {{evolucao 1 linha}}
[repetir para cada tendencia ativa, ou omitir secao se nao houver]

✅ *GAPS ATUALIZADOS*
▸ {{gap}} — {{novo status: resolvido/avancou/cronico}}
[repetir para cada gap com mudanca de status, ou omitir secao se nenhum gap mudou]

📄 HTML completo salvo em: pique/briefings/{{data}}-pique-news.html
```

### Enviar via Evolution API

**IMPORTANTE — Encoding UTF-8:** No Windows, o curl inline quebra emojis. SEMPRE usar o metodo abaixo (arquivo temporario):

1. Use o **Write tool** para criar um arquivo temporario `_whatsapp_msg.json` na raiz do working directory:

```json
{
  "number": "WHATSAPP_GROUP_ID",
  "text": "MENSAGEM_COMPLETA_AQUI"
}
```

2. Use o **Bash tool** com `--data-binary @arquivo` para enviar:

```bash
curl -s -X POST "EVOLUTION_URL/message/sendText/EVOLUTION_INSTANCE" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "apikey: EVOLUTION_API_KEY" \
  --data-binary "@_whatsapp_msg.json"
```

3. Apague o arquivo temporario apos envio:

```bash
rm _whatsapp_msg.json
```

Substitua os placeholders pelos valores reais do config.local.md.

**Regras de formatacao:**
- Use `*texto*` para negrito no WhatsApp
- Use `_texto_` para italico
- Quebre linhas com `\n` dentro do JSON
- Se a mensagem for muito longa (>4000 chars), divida em 2 arquivos e envie com 2s de delay entre eles

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
