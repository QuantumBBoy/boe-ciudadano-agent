"""Guardarraíl anti-asesoramiento aplicado.

El límite del agente está *construido*, no pegado como disclaimer: cuando una
consulta pide una **decisión sobre el caso personal** del usuario ("¿tengo que
pagar?", "¿puedo despedirle?", "¿me conviene firmar?"), detectamos el patrón y
recalibramos el modo de respuesta. En vez de un veredicto, la respuesta debe dar:

  (a) la información normativa relevante explicada en lenguaje llano,
  (b) los factores concretos de los que depende la respuesta en su caso, y
  (c) la orientación al recurso que sí puede resolverlo.

Este módulo es Python puro y determinista: lo prueban los tests y lo consume el
middleware del agente (``boe_agent.guardrail_middleware``). Separar la *detección*
de la *generación* hace el límite auditable.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

__all__ = ["AdviceSignal", "detect_applied_advice", "recalibration_directive"]


def _normalize(text: str) -> str:
    """Minúsculas y sin acentos, para que los patrones no dependan de tildes."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text


# Patrones de "decisión sobre MI caso". La señal fuerte es la primera/segunda
# persona ("tengo", "puedo", "me", "mi") combinada con un verbo de decisión o
# una pregunta de sí/no sobre una acción concreta.
_DECISION_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\btengo que (pagar|devolver|presentar|firmar|declarar|indemnizar|irme|marcharme)\b", "obligacion-personal"),
    (r"\bestoy obligad[oa] a\b", "obligacion-personal"),
    (r"\b(puedo|podria) (despedir|reclamar|denunciar|recurrir|demandar|echar|desahuciar|no pagar|dejar de pagar)\b", "accion-personal"),
    (r"\bme (conviene|interesa|compensa) (firmar|aceptar|recurrir|denunciar|demandar|renunciar)\b", "conveniencia-personal"),
    (r"\b(debo|deberia) (firmar|aceptar|pagar|recurrir|denunciar|aceptarlo|rechazar)\b", "deber-personal"),
    (r"\bque (hago|debo hacer|me conviene)\b", "decision-personal"),
    (r"\bme pueden (despedir|echar|desahuciar|embargar|multar|sancionar|reclamar)\b", "riesgo-personal"),
    (r"\btengo derecho a\b", "derecho-personal"),
    (r"\b(gano|ganaria|pierdo|perderia) (el|un|mi) juicio\b", "pronostico-personal"),
    (r"\bes legal que me\b", "legalidad-caso"),
    (r"\b(cuanto|que) me (corresponde|deben pagar|tienen que pagar|indemniza)\b", "cuantia-personal"),
)

# Marcas de que la consulta es sobre el caso del propio usuario (no doctrina general).
_FIRST_PERSON = re.compile(r"\b(me|mi|mis|conmigo|yo|nuestr[oa]s?|mio|mia)\b")


@dataclass(frozen=True)
class AdviceSignal:
    """Resultado de la detección.

    ``triggered`` indica si hay petición de asesoramiento aplicado. ``category``
    y ``match`` sirven para tests y para explicar *por qué* se recalibró.
    """

    triggered: bool
    category: str | None = None
    match: str | None = None


def detect_applied_advice(text: str) -> AdviceSignal:
    """Detecta si ``text`` pide una decisión sobre el caso personal del usuario.

    No es un clasificador perfecto ni pretende serlo: prefiere recalibrar de más
    (dar info + factores + orientación) antes que arriesgar un veredicto. El coste
    de un falso positivo es bajo; el de un falso negativo —dar un sí/no a alguien
    vulnerable— es alto.
    """
    if not text or not text.strip():
        return AdviceSignal(triggered=False)
    norm = _normalize(text)
    for pattern, category in _DECISION_PATTERNS:
        m = re.search(pattern, norm)
        if m:
            return AdviceSignal(triggered=True, category=category, match=m.group(0))
    return AdviceSignal(triggered=False)


_DIRECTIVE = """\
[MODO ORIENTACIÓN — activado por el guardarraíl anti-asesoramiento]

La última consulta del usuario pide una DECISIÓN sobre su caso personal
(señal detectada: «{match}», tipo: {category}). NO emitas un veredicto
("sí tienes que pagar", "no pueden despedirte"). En su lugar, estructura la
respuesta en tres partes claras y en lenguaje llano:

1. QUÉ DICE LA NORMA: la información normativa relevante explicada, citando el
   identificador BOE-A-... de la fuente. La certeza solo para lo que el BOE dice
   literalmente.
2. DE QUÉ DEPENDE SU CASO: enumera los factores concretos que cambian la
   respuesta (fechas exactas, si hubo notificación, plazos, importes, situación
   contractual…). Deja explícito que no puedes evaluarlos por él.
3. A DÓNDE ACUDIR: orienta al tipo de recurso —priorizando los gratuitos— que sí
   puede resolver su caso concreto, y cómo se accede en términos generales. No
   inventes teléfonos ni direcciones; invita a verificar el punto local.

Tono calibrado: "las normas de este tipo establecen X; si tu caso encaja depende
de Y". Esto da más poder real que un sí/no, porque da comprensión y un camino seguro.
"""


def recalibration_directive(signal: AdviceSignal) -> str:
    """Texto a inyectar en el system prompt cuando el guardarraíl se dispara."""
    return _DIRECTIVE.format(
        match=signal.match or "consulta de caso personal",
        category=signal.category or "decision-personal",
    )
