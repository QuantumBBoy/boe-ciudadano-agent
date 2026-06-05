"""Ensamblado del deep agent: orquestador + subagentes + guardarraíl + skills.

``create_deep_agent`` (deepagents sobre LangGraph) provee el harness: subagentes
con contexto aislado, sistema de ficheros/memoria para investigaciones largas,
skills cargadas según necesidad y planificación multi-paso. Las tools del BOE
entran por MCP; las locales envuelven el núcleo determinista.
"""

from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from boe_agent import prompts
from boe_agent.guardrail_middleware import AntiAsesoramientoMiddleware
from boe_agent.mcp import BoeMcpConfig, get_boe_tools
from boe_agent.subagents import build_subagents
from boe_agent.tools import LOCAL_TOOLS

__all__ = ["assemble_agent", "build_agent", "PACKAGE_DIR", "SKILLS_SOURCE"]

PACKAGE_DIR = Path(__file__).resolve().parent
SKILLS_SOURCE = "skills"  # relativo a la raíz del backend (PACKAGE_DIR)


def _system_prompt() -> str:
    return prompts.ORQUESTADOR.format(disclaimer=prompts.DISCLAIMER)


def assemble_agent(boe_tools, model=None):
    """Construye el agente a partir de tools del BOE ya cargadas (sin tocar la red).

    Separado de ``build_agent`` para poder ensamblar el grafo en tests con tools y
    modelos simulados.
    """
    # virtual_mode=True confina las rutas a root_dir (las skills se cargan de disco
    # relativas a esa raíz) y evita que '..' o rutas absolutas escapen del paquete.
    backend = FilesystemBackend(root_dir=str(PACKAGE_DIR), virtual_mode=True)
    return create_deep_agent(
        model=model if model is not None else os.getenv("BOE_AGENT_MODEL") or None,
        tools=[*boe_tools, *LOCAL_TOOLS],
        system_prompt=_system_prompt(),
        subagents=build_subagents(boe_tools),
        middleware=[AntiAsesoramientoMiddleware()],
        skills=[SKILLS_SOURCE],
        backend=backend,
    )


async def build_agent(model=None, config: BoeMcpConfig | None = None):
    """Carga las tools del BOE por MCP y ensambla el agente. Async."""
    boe_tools = await get_boe_tools(config)
    return assemble_agent(boe_tools, model=model)
