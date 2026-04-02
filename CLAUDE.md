# Plugin Pique News

COMUNIQUE-SE SEMPRE EM PORTUGUES BRASIL.

Plugin de briefing diario de noticias da Pique Digital.
Scrapa portais, filtra pelo que importa, cruza com cerebro Pique/Yabadoo, gera HTML visual e envia no WhatsApp.

## Comando disponivel

- `/pique-news:news` — Roda o briefing completo (scrape → filtro → HTML → WhatsApp)

## Dependencias externas

- **Apify** (MCP bundled): scraping de portais via `apify/rag-web-browser`
- **Evolution API** (via curl): envio de mensagens no WhatsApp
- **Cerebro Pique** (submodule): contexto de cruzamento

## Onde salva

- HTML do briefing: `pique/briefings/YYYY-MM-DD-pique-news.html`
- Template visual: `templates/briefing.html` (design-system-pique)

## Regras

1. NUNCA enviar mensagem no WhatsApp sem ter gerado o briefing completo primeiro
2. Se uma camada de scraping falhar, continuar com as demais
3. Se Evolution API falhar, salvar HTML e informar o usuario
4. Maximo 15 noticias por briefing — qualidade > quantidade
5. Todo insight deve ter cruzamento com cerebro real, nao generico
6. Formato WhatsApp: emojis + *negrito* + _italico_ + links
