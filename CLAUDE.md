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
- **Cerebro Pique** (submodule): contexto de cruzamento (so Claude Code local)
- **Google Drive sincronizado** (so local): backup HTMLs em `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/`

## Ambientes suportados

O plugin roda em 2 contextos:

| Ambiente | Cerebro | Drive | Credenciais |
|----------|---------|-------|-------------|
| Claude Code local (Windows Henrique) | ✓ | ✓ | `.suporte/credenciais.md` |
| Claude Desktop / remoto | ✗ | ✗ | `${CLAUDE_PLUGIN_ROOT}/config.local.md` OU env vars |

No Desktop, o backup local (Drive) e pulado e a memoria acumulativa vem via WebFetch do `docs.pique.digital/publico/pique/news/?json`.

## Onde salva

- **Backup local** (so Claude Code local): `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/YYYY-MM-DD-pique-news.html`
- **URL publica** (o que vai no WhatsApp, qualquer ambiente): `https://docs.pique.digital/publico/pique/news/{slug}/`
- Template visual: `${CLAUDE_PLUGIN_ROOT}/templates/briefing.html`

## Regras

1. NUNCA enviar mensagem no WhatsApp sem ter gerado o briefing completo primeiro
2. Se uma camada de scraping falhar, continuar com as demais
3. Mensagem WhatsApp = teaser curto + link publico. NAO e pra despejar o briefing todo no chat — quem quer ler abre o link.
4. Se docs-pique MCP falhar, enviar o teaser sem link (ou avisar que HTML ficou so local)
5. Se Evolution API falhar, salvar HTML e informar o usuario
6. Maximo 15 noticias no briefing, maximo 5 bullets no teaser
7. Todo insight deve ter cruzamento com cerebro real, nao generico
8. Formato WhatsApp: emojis + *negrito* + _italico_ + 1 link (o publico)
