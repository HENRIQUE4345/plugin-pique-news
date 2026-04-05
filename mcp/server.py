"""MCP server pra envio de mensagens WhatsApp via Evolution API (Pique Digital).

Expoe 1 tool pro Claude:
  - send_whatsapp_message: envia texto pro grupo/numero via Evolution API

Uso via Claude Code / Desktop (claude_desktop_config.json):

  {
    "mcpServers": {
      "pique-whatsapp": {
        "command": "python",
        "args": ["C:/Users/.../pique-whatsapp-mcp/mcp/server.py"],
        "env": {
          "EVOLUTION_URL": "https://evolution.pique.digital",
          "EVOLUTION_API_KEY": "...",
          "EVOLUTION_INSTANCE": "rique-tel",
          "DEFAULT_GROUP_ID": "120363407511722221@g.us"
        }
      }
    }
  }

Depois reiniciar Claude Code / Desktop. Tool aparece como
mcp__pique-whatsapp__send_whatsapp_message.
"""

from __future__ import annotations

import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

# --- config do ambiente ---
EVOLUTION_URL = os.environ.get("EVOLUTION_URL", "").rstrip("/")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "")
DEFAULT_GROUP_ID = os.environ.get("DEFAULT_GROUP_ID", "")

if not EVOLUTION_URL or not EVOLUTION_API_KEY or not EVOLUTION_INSTANCE:
    print(
        "[pique-whatsapp MCP] AVISO: EVOLUTION_URL, EVOLUTION_API_KEY ou "
        "EVOLUTION_INSTANCE nao definidos no ambiente. Chamadas vao falhar.",
        file=sys.stderr,
    )

mcp = FastMCP("pique-whatsapp")


@mcp.tool()
def send_whatsapp_message(
    text: str,
    group_id: str | None = None,
    instance: str | None = None,
) -> dict:
    """Envia uma mensagem de texto pelo WhatsApp via Evolution API.

    Aceita formatacao nativa do WhatsApp: *negrito*, _italico_, ~riscado~,
    ```monospace```, emojis unicode. Quebras de linha com \\n.

    Args:
        text: Conteudo da mensagem. Pode ter ate ~4000 chars. Para textos
              maiores, dividir em chamadas separadas (nao ha split automatico).
        group_id: ID do destinatario (grupo ou numero). Formato de grupo:
                  "120363407511722221@g.us". Formato de numero: "5511999999999".
                  Se omitido, usa DEFAULT_GROUP_ID do env.
        instance: Nome da instance da Evolution. Se omitido, usa
                  EVOLUTION_INSTANCE do env.

    Returns:
        dict com:
          - status: "sent"
          - group_id: destinatario final usado
          - instance: instance usada
          - http_code: codigo HTTP da Evolution (200/201)
          - message_key: chave da mensagem retornada pela Evolution (se houver)
    """
    if not text or not text.strip():
        raise ValueError("text vazio")

    inst = instance or EVOLUTION_INSTANCE
    gid = group_id or DEFAULT_GROUP_ID

    if not inst:
        raise ValueError("instance obrigatoria (nem DEFAULT EVOLUTION_INSTANCE foi setada)")
    if not gid:
        raise ValueError("group_id obrigatorio (nem DEFAULT_GROUP_ID foi setada)")
    if not EVOLUTION_URL or not EVOLUTION_API_KEY:
        raise RuntimeError("EVOLUTION_URL ou EVOLUTION_API_KEY nao configurados no env do MCP")

    endpoint = f"{EVOLUTION_URL}/message/sendText/{inst}"
    payload = {"number": gid, "text": text}

    try:
        response = httpx.post(
            endpoint,
            json=payload,
            headers={
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json; charset=utf-8",
            },
            timeout=30.0,
        )
    except httpx.RequestError as e:
        raise RuntimeError(f"Falha de rede na Evolution API: {e}") from e

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Evolution API retornou HTTP {response.status_code}: {response.text[:300]}"
        )

    try:
        data = response.json()
    except Exception:
        data = {}

    return {
        "status": "sent",
        "group_id": gid,
        "instance": inst,
        "http_code": response.status_code,
        "message_key": data.get("key", {}),
    }


if __name__ == "__main__":
    mcp.run()
