"""Tools locales que exponen el núcleo determinista al agente.

Se suman a las tools del BOE (que llegan por MCP). Cada una envuelve una función
pura de ``boe_agent.core`` y devuelve texto legible para el modelo.
"""

from __future__ import annotations

import json

from langchain_core.tools import tool

from boe_agent.core import divulgacion, orientacion, verificacion, vigilancia

__all__ = ["LOCAL_TOOLS", "orientar_recursos", "evaluar_vigencia",
           "verificar_respaldo", "glosario_jerga", "explicar_termino"]


@tool
def orientar_recursos(problema: str) -> str:
    """Mapea un problema legal descrito en lenguaje natural a recursos de ayuda reales.

    Devuelve el tipo de recurso (priorizando los gratuitos: justicia gratuita/turno
    de oficio, OMIC, mediación, defensor del pueblo…) y cómo se accede en términos
    generales. NO da contactos concretos: hay que verificarlos en el punto local.
    """
    o = orientacion.orientar(problema)
    lineas = [f"Materia detectada: {o.materia}", "Recursos orientativos:"]
    for r in o.recursos:
        etiqueta = "GRATUITO" if r.gratuito else "puede tener coste"
        lineas.append(f"\n• {r.nombre} ({etiqueta})\n  {r.descripcion}\n  Cómo acceder: {r.como_acceder}")
    lineas.append(f"\nNota: {o.nota}")
    return "\n".join(lineas)


@tool
def evaluar_vigencia(law_id: str, metadata_json: str, analysis_json: str) -> str:
    """Determina si una norma sigue vigente cruzando sus metadatos y su análisis.

    Antes de llamar a esta tool, recupera del BOE los metadatos (get_law_metadata) y
    el análisis (get_law_analysis) de la norma y pásalos aquí como JSON (en
    'metadata_json' y 'analysis_json'). 'law_id' es el identificador BOE-A-...
    Devuelve estado de vigencia, normas que la afectan, alcance y artículos tocados.
    """
    def _parse(raw: str):
        try:
            return json.loads(raw) if raw and raw.strip() else None
        except json.JSONDecodeError:
            # El BOE/tool puede devolver texto no-JSON; lo pasamos como evidencia plana.
            return {"texto": raw}

    v = vigilancia.evaluar_vigencia(law_id, _parse(metadata_json), _parse(analysis_json))
    lineas = [
        f"Norma: {v.law_id}",
        f"Estado: {v.estado}" + (f"  (vigente={v.vigente})" if v.vigente is not None else "  (vigencia no confirmable)"),
    ]
    if v.estado_consolidacion:
        lineas.append(f"Estado de consolidación (metadatos): {v.estado_consolidacion}")
    if v.afectaciones:
        lineas.append("Afectada por:")
        for a in v.afectaciones:
            preceptos = f" [arts.: {', '.join(a.preceptos)}]" if a.preceptos else ""
            norma = f" por {a.norma}" if a.norma else ""
            lineas.append(f"  - {a.tipo} ({a.alcance}){norma}{preceptos}: {a.texto}")
    else:
        lineas.append("No constan afectaciones posteriores en el análisis recuperado.")
    lineas.append("\n" + v.fuente_oficial())
    return "\n".join(lineas)


@tool
def verificar_respaldo(respuesta: str, evidencia: list[str]) -> str:
    """Comprueba que las afirmaciones legales de 'respuesta' estén respaldadas por la evidencia.

    'evidencia' son las salidas de las tools del BOE usadas. Señala los
    identificadores BOE, artículos, cifras, fechas o plazos que NO aparezcan en la
    evidencia para que se marquen como NO confirmados o se recuperen del BOE.
    """
    reporte = verificacion.verificar_respaldo(respuesta, evidencia)
    return reporte.resumen()


@tool
def glosario_jerga(texto: str) -> str:
    """Lista los tecnicismos jurídicos presentes en 'texto' que NO van explicados al lado.

    Úsalo al divulgar: si devuelve términos, reescríbelos explicándolos.
    """
    sueltos = divulgacion.jerga_sin_explicar(texto)
    if not sueltos:
        return "No se detectan tecnicismos sin explicar."
    detalle = "\n".join(f"• {t}: {divulgacion.GLOSARIO[t]}" for t in sueltos)
    return "Tecnicismos sin explicar (explícalos en el texto):\n" + detalle


@tool
def explicar_termino(termino: str) -> str:
    """Da una explicación en lenguaje llano de un término jurídico, si está en el glosario."""
    exp = divulgacion.explicar(termino)
    return exp if exp else f"'{termino}' no está en el glosario base; explícalo con tus palabras y verifica su sentido en el texto del BOE."


LOCAL_TOOLS = [
    orientar_recursos,
    evaluar_vigencia,
    verificar_respaldo,
    glosario_jerga,
    explicar_termino,
]
