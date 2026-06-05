"""Conexión stdio al servidor boe-mcp y carga de sus tools.

Reaprovecha el servidor MCP del BOE que ya existe. La forma de lanzarlo es
configurable por entorno (``.env``) para no atarnos a una instalación concreta:

  BOE_MCP_COMMAND   comando que arranca el servidor (por defecto "boe-mcp")
  BOE_MCP_ARGS      argumentos separados por espacios (opcional)
  BOE_MCP_CWD       directorio de trabajo del servidor (opcional)

Las tools entran vía ``langchain-mcp-adapters`` (MultiServerMCPClient).
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass

__all__ = ["BoeMcpConfig", "build_server_config", "get_boe_tools", "MCP_SETUP_HELP"]

MCP_SETUP_HELP = """\
No se pudo conectar con el servidor boe-mcp.

Comprueba que:
  1) boe-mcp está instalado y es ejecutable. Prueba en tu terminal:  boe-mcp --help
     (o instala el repo BoeMCP y usa  BOE_MCP_COMMAND=python  BOE_MCP_ARGS=-m boe_mcp.server).
  2) Las variables de entorno apuntan al lanzador correcto (ver .env.example):
       BOE_MCP_COMMAND, BOE_MCP_ARGS, BOE_MCP_CWD
  3) Tienes conexión a internet (boe-mcp consulta la API abierta del BOE).
"""


@dataclass(frozen=True)
class BoeMcpConfig:
    command: str
    args: list[str]
    cwd: str | None

    def to_adapter_dict(self) -> dict:
        """Formato que espera MultiServerMCPClient para un servidor stdio."""
        cfg: dict = {"command": self.command, "args": list(self.args), "transport": "stdio"}
        if self.cwd:
            cfg["cwd"] = self.cwd
        return cfg


def build_server_config(env: dict[str, str] | None = None) -> BoeMcpConfig:
    """Construye la configuración del servidor a partir del entorno (función pura, testeable)."""
    env = env if env is not None else dict(os.environ)
    command = env.get("BOE_MCP_COMMAND", "boe-mcp").strip() or "boe-mcp"
    args = shlex.split(env.get("BOE_MCP_ARGS", "").strip())
    cwd = env.get("BOE_MCP_CWD", "").strip() or None
    return BoeMcpConfig(command=command, args=args, cwd=cwd)


async def get_boe_tools(config: BoeMcpConfig | None = None):
    """Lanza boe-mcp por stdio y devuelve sus tools como LangChain tools.

    Lanza ``RuntimeError`` con ayuda de setup si la conexión falla.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient

    config = config or build_server_config()
    client = MultiServerMCPClient({"boe": config.to_adapter_dict()})
    try:
        return await client.get_tools()
    except Exception as exc:  # noqa: BLE001 — queremos un mensaje claro de setup
        raise RuntimeError(MCP_SETUP_HELP) from exc
