"""Definición de los cinco subagentes con contexto aislado.

Cada subagente recibe solo el subconjunto de tools que necesita: las del BOE
(llegadas por MCP) más las locales pertinentes. Mantener el contexto acotado es
parte de lo que hace "deep" al agente.
"""

from __future__ import annotations

from deepagents import SubAgent

from boe_agent import prompts, tools as local

__all__ = ["build_subagents"]


def _pick(boe_tools, *names):
    """Selecciona tools del BOE por nombre (ignora las que no estén disponibles)."""
    wanted = set(names)
    return [t for t in boe_tools if getattr(t, "name", None) in wanted]


def build_subagents(boe_tools) -> list[SubAgent]:
    """Construye los subagentes a partir de las tools del BOE ya cargadas."""
    divulgador: SubAgent = {
        "name": "divulgador",
        "description": (
            "Reescribe texto legal en lenguaje llano para personas sin formación "
            "jurídica, marcando y explicando cada tecnicismo. Úsalo para TRADUCIR."
        ),
        "system_prompt": prompts.DIVULGADOR,
        "tools": _pick(boe_tools, "get_law_index", "get_law_block", "get_law")
        + [local.glosario_jerga, local.explicar_termino],
    }

    investigador: SubAgent = {
        "name": "investigador",
        "description": (
            "Localiza la norma aplicable a un problema: busca, recupera candidatas, "
            "teje relaciones y escribe un dossier. Úsalo para ENCONTRAR."
        ),
        "system_prompt": prompts.INVESTIGADOR,
        "tools": _pick(
            boe_tools,
            "search_legislation",
            "get_law_metadata",
            "get_law_index",
            "get_law_analysis",
            "get_law",
            "lookup_matters",
            "lookup_legal_ranges",
        ),
    }

    rastreador: SubAgent = {
        "name": "rastreador",
        "description": (
            "Determina si una norma sigue vigente cruzando metadatos y referencias "
            "posteriores; avisa de derogaciones y modificaciones. Úsalo para VIGILAR."
        ),
        "system_prompt": prompts.RASTREADOR,
        "tools": _pick(boe_tools, "get_law_metadata", "get_law_analysis")
        + [local.evaluar_vigencia],
    }

    orientador: SubAgent = {
        "name": "orientador",
        "description": (
            "Mapea el tipo de problema a recursos de ayuda reales (priorizando los "
            "gratuitos) y cómo se accede en general. Úsalo para ORIENTAR."
        ),
        "system_prompt": prompts.ORIENTADOR,
        "tools": [local.orientar_recursos],
    }

    verificador: SubAgent = {
        "name": "verificador",
        "description": (
            "Comprueba que cada afirmación legal de la respuesta esté respaldada por "
            "datos recuperados del BOE; marca lo no respaldado. Úsalo ANTES de cerrar."
        ),
        "system_prompt": prompts.VERIFICADOR,
        "tools": _pick(boe_tools, "get_law_metadata", "get_law_analysis", "get_law_block")
        + [local.verificar_respaldo],
    }

    return [divulgador, investigador, rastreador, orientador, verificador]
