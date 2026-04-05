---
description: Briefing diario de noticias — scrapa portais, cruza com cerebro Pique/Yabadoo, gera HTML visual e envia resumo no WhatsApp.
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, mcp__plugin_plugin-pique-news_apify__call-actor, mcp__plugin_plugin-pique-news_apify__fetch-actor-details, mcp__plugin_plugin-pique-news_apify__get-actor-output, mcp__plugin_plugin-pique-news_apify__get-actor-run, mcp__plugin_plugin-pique-news_apify__search-actors, mcp__docs-pique__upload_page, mcp__docs-pique__get_page_url, mcp__plugin_plugin-pique-news_pique-whatsapp__send_whatsapp_message
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

## Passo 0 — Verificar MCPs disponiveis

Credenciais Evolution API NAO vivem mais no plugin — estao encapsuladas no MCP `pique-whatsapp` (env vars registradas no `.claude.json` / `claude_desktop_config.json`). O plugin so precisa chamar a tool.

**Verificar:**
- Tool `mcp__plugin_plugin-pique-news_pique-whatsapp__send_whatsapp_message` disponivel? (envio WhatsApp)
- Tool `mcp__docs-pique__upload_page` disponivel? (upload HTML)

Se qualquer uma estiver indisponivel, marcar e continuar — os fallbacks dos Passos 4/5 lidam com ausencia delas. O briefing em si nao depende de nenhuma das duas (sempre gera HTML e grava backup local quando possivel).

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

Antes de buscar noticias novas, leia o que ja foi reportado. Tem 2 fontes possiveis (tente nessa ordem):

### Fonte A — Drive local (Claude Code local)

1. **Glob** `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/*-pique-news.html`
2. Se a pasta nao existir ou nao retornar resultados: passar pra Fonte B.

### Fonte B — docs.pique.digital via WebFetch (qualquer ambiente, incluindo Desktop)

1. **WebFetch** `https://docs.pique.digital/publico/pique/news/?json` — retorna JSON com a lista de arquivos/pastas. Estrutura: `{"paths": [{"name": "2026-04-04-pique-news-abc123", "mtime": ..., "path_type": "Dir"}, ...]}`.
2. Ordenar por data no nome (ou `mtime`), pegar os 3 mais recentes.
3. Pra cada um, **WebFetch** `https://docs.pique.digital/publico/pique/news/{slug}/` — traz o HTML do briefing.
4. Se o fetch falhar (rede, 404, etc): pular este passo inteiro (briefing fresco sem memoria acumulativa).

### Extracao (comum as 2 fontes)

**Leia os 3 mais recentes.** Se houver menos de 3, leia todos. Se nao houver nenhum, pule este passo inteiro.

**De cada HTML, extraia:**
- Bloco `<!-- PIQUE-NEWS-METADATA ... -->` (se existir) — parse direto dele. Eh o mais eficiente.
- Se NAO tiver bloco de metadata (briefings antigos): ler os textos dentro de `.news-headline`, `.news-insight`, `.gap-title` + `.gap-action` do HTML

**Monte 3 listas de trabalho:**

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

### Destino do arquivo (backup local — opcional)

**Caminho:** `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/{{YYYY-MM-DD}}-pique-news.html`

Essa pasta eh o Drive compartilhado da Pique. Serve como backup acessivel pela equipe e pra memoria acumulativa do Passo 1.5.

**Regra:** so salvar se o path existir e for gravavel (Claude Code local com Drive sincronizado). Em Desktop/remoto o Drive nao esta montado — **pular o backup local silenciosamente** e depender 100% do upload pro docs.pique.digital (Passo seguinte).

**Verificacao rapida:** antes de salvar, `ls "G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/"` via Bash. Se retornar erro, pular. Se ok, Write no caminho.

**NAO salvar em `pique/briefings/` no cerebro** (comportamento antigo removido — briefings nao ficam mais no cerebro local).

### Upload pra docs.pique.digital

Apos salvar o backup local, subir o HTML pro dufs via MCP `docs-pique`:

```
mcp__docs-pique__upload_page(
  html="{conteudo completo do HTML}",
  folder="pique/news",
  visibility="publico",
  title="pique-news"
)
```

Resultado esperado: `{"url": "https://docs.pique.digital/publico/pique/news/YYYY-MM-DD-pique-news-{hash6}/", "status": "created", ...}`

**Guarde o `url` retornado** — ele e o ponto central do Passo 5 (mensagem WhatsApp).

**Fallbacks:**
- MCP `docs-pique` nao disponivel → pular upload, marcar no Passo 6 que o link publico nao foi gerado, e no Passo 5 enviar so o teaser sem link (ou com aviso "HTML salvo localmente — upload falhou")
- Upload retorna erro (401, 500, timeout) → mesmo comportamento

---

## Passo 5 — Enviar no WhatsApp (teaser, nao dump)

**Objetivo:** mensagem curta que gera curiosidade e manda pro link. NAO e pra entregar o briefing todo no WhatsApp — quem quiser o conteudo abre o link.

Monte uma mensagem teaser com esta estrutura (formatacao WhatsApp, sem HTML):

```
📡 *PIQUE NEWS — {{DATA_FORMATADA}}*
_{{subtitulo — 1 linha instigante sobre o tema dominante do dia}}_

🔥 *{{MANCHETE_TITULO}}*
{{hook de 1 linha — o *por que* a manchete importa, sem spoiler completo}}

📰 *No briefing de hoje*
▸ {{hook noticia 1 — 1 linha instigante, estilo headline}}
▸ {{hook noticia 2}}
▸ {{hook noticia 3}}
▸ {{hook noticia 4}}
▸ {{hook noticia 5}}

📈 *Tendencia em alta:* {{nome tendencia ativa}}
⚡ *Gap que pede acao:* {{gap titulo curto}}

👉 *Briefing completo:* {{URL_PUBLICO}}
```

### Regras do teaser

1. **Curiosidade > informacao completa.** Cada bullet e um *gancho*, nao um resumo. Estilo headline de jornal, nao paragrafo de noticia.
   - Bom: `"▸ Anthropic lancou algo que muda o jogo de agentes autonomos"`
   - Ruim: `"▸ Anthropic lancou Claude Agent SDK que permite criar agents com memoria persistente e ferramentas..."` (spoiler demais)
2. **Maximo 5 bullets** na secao "No briefing de hoje". Escolher os mais *instigantes*, nao necessariamente os mais importantes.
3. **Tendencia e Gap sao opcionais.** So incluir se houver tendencia ativa identificada pelo Passo 1.5 OU gap cronico/de alta prioridade. Se nao tiver, omitir as linhas inteiras.
4. **Sem links individuais por noticia.** So um link no final — o do briefing completo no docs.pique.digital.
5. **Meta de tamanho:** < 900 caracteres totais. Leitura de 20 segundos no celular.
6. **Tom:** direto, intrigante, sem hype gratuito. Nao usar "🚨 URGENTE" nem "VOCE PRECISA VER ISSO". O ganho e de curiosidade, nao de alarme.
7. **Se o upload docs-pique falhou** (URL nao disponivel): substituir a ultima linha por `"📄 HTML salvo no Drive (upload publico falhou — ver Pique News/{{data}}-pique-news.html)"`. Se o backup local tambem falhou (Desktop sem Drive): avisar `"⚠️ Briefing gerado mas nao foi possivel publicar (docs-pique + Drive indisponiveis)"`.

### Enviar via MCP pique-whatsapp

Chamar a tool diretamente — o MCP encapsula credenciais, endpoint e encoding UTF-8:

```
mcp__plugin_plugin-pique-news_pique-whatsapp__send_whatsapp_message(
  text="{{teaser completo montado acima}}"
)
```

O parametro `group_id` eh opcional — se omitido, a tool usa o `DEFAULT_GROUP_ID` do env do MCP (hoje: grupo Pique News). So passar `group_id` explicito se precisar enviar pra outro destino.

**Retorno esperado:** `{"status": "sent", "group_id": "...", "http_code": 200, "message_key": {...}}`.

**Se a tool retornar erro ou nao existir:**
- Erro de rede/HTTP: marcar falha, seguir pro Passo 6
- Tool indisponivel (MCP nao registrado): marcar pulado, seguir pro Passo 6
- NUNCA fazer fallback pra curl manual — o MCP eh a unica forma suportada

**Regras de formatacao (tudo ja no parametro `text`):**
- `*texto*` para negrito
- `_texto_` para italico
- Quebras de linha com `\n` literais no string
- Emojis unicode direto no texto (o MCP manda UTF-8 nativo)
- Se a mensagem passar de ~4000 chars, dividir em 2 chamadas separadas da tool

---

## Passo 6 — Confirmar

Apos envio, informe:
1. Total de noticias curadas
2. Caminho do HTML salvo (backup local)
3. URL publica no docs.pique.digital (ou aviso de falha de upload)
4. Status do envio WhatsApp (sucesso/falha)
5. Se alguma camada de scraping falhou

---

## Fallbacks

- **Apify MCP nao disponivel:** use WebFetch/WebSearch como alternativa
- **docs-pique MCP fora:** pule o upload, envie o teaser sem URL publica (ver Passo 5 regra 7), avise no Passo 6
- **pique-whatsapp MCP fora:** briefing ainda e gerado e publicado (se docs-pique funcionou); so o envio WhatsApp eh pulado. Avisar no Passo 6.
- **Nenhuma noticia relevante:** gere briefing minimo com "Dia calmo — nenhuma noticia com impacto direto identificada" e envie mesmo assim (manter o habito)
- **Cerebro nao acessivel:** gere briefing sem cruzamento, marcando "[sem cruzamento — cerebro indisponivel]" nos insights
