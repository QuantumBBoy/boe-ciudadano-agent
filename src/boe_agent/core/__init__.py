"""Núcleo determinista de las cuatro capacidades + guardarraíl.

Python puro, sin dependencias del LLM ni de la red. Estos módulos:
  - implementan la lógica auditable de cada capacidad,
  - se exponen como tools al agente (ver ``boe_agent.tools``), y
  - son lo que prueban los tests sin necesidad de un modelo en vivo.
"""

from boe_agent.core import divulgacion, guardrails, orientacion, verificacion, vigilancia

__all__ = ["divulgacion", "guardrails", "orientacion", "verificacion", "vigilancia"]
