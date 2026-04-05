# Plugin Pique News

COMUNIQUE-SE SEMPRE EM PORTUGUES BRASIL.

Plugin de briefing diario de noticias da Pique Digital.
Scrapa portais, filtra pelo que importa, cruza com cerebro Pique/Yabadoo, gera HTML visual e envia no WhatsApp.

## Comando disponivel

- `/pique-news:news` — Roda o briefing completo (scrape → filtro → HTML → WhatsApp)

## Dependencias externas

- **Apify** (MCP bundled): scraping de portais via `apify/rag-web-browser`
- **docs-pique** (MCP user scope): upload de HTML pro dufs em docs.pique.digital
- **Evolution API** (via curl): envio de mensagens no WhatsApp
- **Cerebro Pique** (submodule): contexto de cruzamento
- **Credenciais Evolution:** `.suporte/credenciais.md` (fonte unica, gitignored)

## Onde salva

- **Backup local** (alimenta memoria acumulativa): `pique/briefings/YYYY-MM-DD-pique-news.html`
- **URL publica** (o que vai no WhatsApp): `https://docs.pique.digital/publico/pique/news/{slug}/`
- Template visual: `templates/briefing.html` (design-system-pique)

## Regras

1. NUNCA enviar mensagem no WhatsApp sem ter gerado o briefing completo primeiro
2. Se uma camada de scraping falhar, continuar com as demais
3. Mensagem WhatsApp = teaser curto + link publico. NAO e pra despejar o briefing todo no chat — quem quer ler abre o link.
4. Se docs-pique MCP falhar, enviar o teaser sem link (ou avisar que HTML ficou so local)
5. Se Evolution API falhar, salvar HTML e informar o usuario
6. Maximo 15 noticias no briefing, maximo 5 bullets no teaser
7. Todo insight deve ter cruzamento com cerebro real, nao generico
8. Formato WhatsApp: emojis + *negrito* + _italico_ + 1 link (o publico)
