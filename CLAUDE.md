# Plugin Pique News

COMUNIQUE-SE SEMPRE EM PORTUGUES BRASIL.

Plugin de briefing diario de noticias da Pique Digital.
Scrapa portais, filtra pelo que importa, cruza com cerebro Pique/Yabadoo, gera HTML visual e envia no WhatsApp.

## Comando disponivel

- `/pique-news:news` — Roda o briefing completo (scrape → filtro → HTML → WhatsApp)

## Dependencias externas

- **Apify** (MCP bundled): scraping de portais via `apify/rag-web-browser`
- **docs-pique** (MCP user scope): upload de HTML pro dufs em docs.pique.digital
- **pique-whatsapp** (MCP user scope): envio de mensagens WhatsApp via Evolution API (credenciais encapsuladas no env do MCP — plugin nao precisa carregar nada)
- **Cerebro Pique** (submodule): contexto de cruzamento (so Claude Code local)
- **Google Drive sincronizado** (so local): backup HTMLs em `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/`

## Ambientes suportados

O plugin roda em 2 contextos:

| Ambiente | Cerebro | Drive | Credenciais WhatsApp |
|----------|---------|-------|---------------------|
| Claude Code local (Windows Henrique) | ✓ | ✓ | MCP pique-whatsapp |
| Claude Desktop / cowork | ✗ | ✗ | MCP pique-whatsapp |

Em ambos os casos, o envio WhatsApp passa pelo MCP `pique-whatsapp` — credenciais vivem no env do MCP (registrado em `.claude.json` e `claude_desktop_config.json`), nao no plugin.

No Desktop, o backup local (Drive) e pulado e a memoria acumulativa vem via WebFetch do `docs.pique.digital/publico/pique/news/?json`.

## Onde salva

- **Backup local** (so Claude Code local): `G:/Drives compartilhados/Pique Digital/Pique Digital/Pique News/YYYY-MM-DD-pique-news.html`
- **URL publica** (o que vai no WhatsApp, qualquer ambiente): `https://docs.pique.digital/publico/pique/news/{slug}/`
- Template visual: `${CLAUDE_PLUGIN_ROOT}/templates/briefing.html`

## Regras

1. NUNCA enviar mensagem no WhatsApp sem ter gerado o briefing completo primeiro
2. Se uma camada de scraping falhar, continuar com as demais
3. Mensagem WhatsApp = teaser curto + link publico. NAO e pra despejar o briefing todo no chat — quem quer ler abre o link.
4. Envio WhatsApp SEMPRE via `mcp__pique-whatsapp__send_whatsapp_message`. Nunca curl direto.
5. Se docs-pique MCP falhar, enviar o teaser sem link (ou avisar que HTML ficou so local)
6. Se pique-whatsapp MCP falhar, briefing ainda publica no docs.pique.digital — so o envio e pulado
7. Maximo 15 noticias no briefing, maximo 5 bullets no teaser
8. Todo insight deve ter cruzamento com cerebro real, nao generico
9. Formato WhatsApp: emojis + *negrito* + _italico_ + 1 link (o publico)
