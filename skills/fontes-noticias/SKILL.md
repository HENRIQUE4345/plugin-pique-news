---
name: fontes-noticias
description: Conhecimento sobre fontes de noticias, categorias de curadoria e criterios de relevancia para o briefing diario Pique News. Auto-invoca quando o usuario mencionar noticias, briefing, fontes, curadoria, ou Pique News.
---

# Fontes de Noticias — Pique News

## Categorias e fontes

### IA / Tech (core do negocio)
| Fonte | URL | Tipo | Frequencia |
|-------|-----|------|-----------|
| The Rundown AI | therundown.ai | Newsletter curada | Diaria |
| Anthropic Blog | anthropic.com/news | Oficial | Irregular |
| OpenAI Blog | openai.com/blog | Oficial | Irregular |
| Google AI Blog | blog.google/technology/ai/ | Oficial | Irregular |
| Ben's Bites | bensbites.com | Curadoria deep | Diaria |

### Tech Brasil
| Fonte | URL | Tipo | Frequencia |
|-------|-----|------|-----------|
| Tecnoblog | tecnoblog.net/noticias/ | Portal tech BR | Continua |
| Startups.com.br | startups.com.br/noticias/ | Ecossistema startup | Continua |

### Negocios / PME
| Fonte | URL | Tipo | Frequencia |
|-------|-----|------|-----------|
| Exame PME | exame.com/pme/ | Empreendedorismo | Continua |
| InfoMoney | infomoney.com.br/negocios/ | Financas/negocios | Continua |

### Marketing Digital
| Fonte | URL | Tipo | Frequencia |
|-------|-----|------|-----------|
| Search Engine Land | searchengineland.com | SEO, search, ads | Continua |
| Social Media Today | socialmediatoday.com | Redes sociais | Continua |

### Ferramentas / Produtos
| Fonte | URL | Tipo | Frequencia |
|-------|-----|------|-----------|
| Product Hunt | producthunt.com | Lancamentos | Diaria |
| Hacker News | news.ycombinator.com | Front page tech | Continua |

## Criterios de relevancia

O briefing NAO e um agregador. E um filtro inteligente. Relevancia e definida pelo cruzamento com o trabalho real da Pique:

### QUENTE (incluir com destaque)
- Lancamento de ferramenta que afeta stack da Pique ou dos clientes
- Mudanca de plataforma (Instagram, WhatsApp, Google) que afeta servicos
- Noticia sobre IA que muda o mercado de consultoria tech
- Movimento de concorrente direto ou indireto
- Regulamentacao que afeta PMEs ou tech no Brasil
- Desdobramento de tendencia ativa (tema que apareceu em 2+ briefings anteriores)

### RELEVANTE (incluir normal)
- Tendencia emergente que pode virar oportunidade em 3-6 meses
- Case de sucesso/fracasso de PME com tecnologia
- Dados de mercado sobre adocao de IA/automacao
- Lancamento de produto que pode servir como referencia

### FRIO (descartar)
- Noticia generica sem conexao com nosso trabalho
- Rumores sem confirmacao
- Conteudo duplicado entre fontes
- Tech hype sem aplicacao pratica pro nosso publico
- Noticia ja reportada em briefing anterior sem nenhum desdobramento novo

## Cruzamento com cerebro

Cada noticia relevante deve ser cruzada com:

1. **Pique (estrategia + clientes):** como afeta o roadmap, servicos, ou clientes atuais?
2. **Yabadoo (produto):** como se relaciona com o Arquiteto de Contexto?
3. **@iairique (conteudo):** vira pauta? Qual angulo dos 42 topicos?
4. **Gaps:** algo que o mercado faz e a Pique nao? Oportunidade de novo servico?

## Formato de entrega

- **HTML:** visual estilo Pique (blueprint dark + amber), salvo em `pique/briefings/`
- **WhatsApp:** versao texto com emojis, formatacao WhatsApp (*negrito*, _italico_)
- **Maximo:** 15 noticias por briefing, 1 manchete destaque, 1-3 gaps

## Historico e inteligencia acumulativa

Os briefings ficam salvos em `pique/briefings/YYYY-MM-DD-pique-news.html`.

### Leitura de briefings anteriores

O comando `/pique-news:news` le automaticamente os 3 briefings mais recentes antes de buscar noticias novas (Passo 1.5). Isso permite:

1. **Deduplicacao:** noticias ja reportadas nao se repetem — a menos que tenham desdobramento novo
2. **Tendencias:** temas que aparecem em 2+ briefings sao nomeados como TENDENCIA e acompanhados com timeline
3. **Gaps:** oportunidades identificadas sao rastreadas entre briefings ate serem resolvidas ou escaladas

### Regras de continuidade

- **Noticia repetida sem novidade:** descartar (classificar como FRIO)
- **Noticia repetida COM desdobramento:** incluir com tag "CONTINUACAO de DD/MM"
- **Tema em 2+ briefings:** promover a TENDENCIA com nome e timeline
- **Gap aberto 3+ dias sem acao:** escalar como GAP CRONICO — sugerir inclusao no planejamento semanal
- **Gap resolvido:** marcar como resolvido no metadata e no HTML

### Metadata no HTML

Cada briefing inclui um bloco `<!-- PIQUE-NEWS-METADATA -->` antes do `</body>` com dados estruturados (data, manchete, tendencias, gaps, noticias-chave). Isso permite leitura rapida sem parsear o HTML inteiro.

### Alimenta outros rituais

- `/social-radar` pode cruzar tendencias do news com trends de social media
- `/pique:review-semanal` pode referenciar gaps identificados na semana
- `/pique:planejamento-semanal` pode incluir gaps cronicos como tasks
