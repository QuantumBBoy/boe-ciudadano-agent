"""Apoyo a la divulgación: glosario y detección de jerga sin explicar.

El subagente `divulgador` reescribe en lenguaje llano y, sobre todo, **marca y
explica** los tecnicismos en vez de soltarlos. Este módulo da:

  - un glosario base de términos jurídicos frecuentes con su explicación llana, y
  - ``jerga_sin_explicar(texto)``: detecta tecnicismos presentes en un texto que
    NO van acompañados de una explicación cercana.

Lo usa la tool ``glosario_jerga`` (ayuda al divulgador) y el chequeo de
divulgación de los ejemplos/tests: un buen resumen no debe dejar tecnicismos
crudos.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["GLOSARIO", "explicar", "jerga_sin_explicar"]


# Término técnico -> explicación en lenguaje llano (sin volver a usar jerga).
GLOSARIO: dict[str, str] = {
    "prescripcion": "el plazo pasado el cual ya no te pueden reclamar algo legalmente",
    "prescribir": "perder validez por haber pasado demasiado tiempo",
    "caducidad": "el plazo límite tras el cual pierdes el derecho a hacer un trámite",
    "derogacion": "cuando una ley deja de estar en vigor porque otra la anula",
    "derogar": "anular una ley para que deje de aplicarse",
    "preceptos": "los artículos o normas concretas de una ley",
    "precepto": "un artículo o regla concreta de una ley",
    "disposicion adicional": "una regla extra al final de la ley que añade algo al texto principal",
    "disposicion transitoria": "una regla que dice qué pasa con las situaciones que venían de antes de la nueva ley",
    "disposicion derogatoria": "la parte de la ley que dice qué normas anteriores quedan anuladas",
    "subrogacion": "cuando alguien ocupa el lugar de otra persona en un contrato o deuda",
    "litisconsorcio": "cuando varias personas actúan juntas como parte en un mismo juicio",
    "fehaciente": "que deja constancia segura y demostrable (por ejemplo, un burofax)",
    "notificacion fehaciente": "un aviso enviado de forma que quede prueba de que lo recibiste",
    "silencio administrativo": "qué se entiende que decide la Administración cuando no te contesta a tiempo",
    "recurso de alzada": "una reclamación ante el órgano superior al que tomó la decisión",
    "via ejecutiva": "la fase en la que la Administración puede cobrarte por la fuerza (embargos)",
    "apremio": "el recargo y procedimiento para cobrarte una deuda que no pagaste a tiempo",
    "usufructo": "el derecho a usar y disfrutar algo que es propiedad de otra persona",
    "nuda propiedad": "ser dueño de algo pero sin poder usarlo mientras otro tiene el usufructo",
    "potestativo": "que es opcional, no obligatorio",
    "preceptivo": "que es obligatorio por ley",
    "ex officio": "que se hace de oficio, por iniciativa del propio organismo, sin que tú lo pidas",
    "de oficio": "que lo hace el organismo por su cuenta, sin que tengas que solicitarlo",
    "ad cautelam": "por precaución, por si acaso",
    "estimar": "dar la razón a una reclamación o recurso",
    "desestimar": "rechazar una reclamación o recurso",
    "allanarse": "aceptar las pretensiones de la otra parte en un juicio",
    "litisexpensas": "los gastos de un pleito",
    "emolumentos": "lo que se cobra por un trabajo o cargo (sueldo, honorarios)",
    "devengar": "generar el derecho a cobrar algo (por ejemplo, intereses que se van acumulando)",
    "sine die": "sin fecha fijada, indefinidamente",
    "in fine": "al final (de un artículo o apartado)",
    "ipso iure": "de forma automática, por la propia ley, sin necesidad de trámite",
}


def _norm(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def explicar(termino: str) -> str | None:
    """Explicación llana de un término, o None si no está en el glosario."""
    return GLOSARIO.get(_norm(termino).strip())


# Señales de que un término YA se está explicando cerca (no cuenta como jerga cruda).
_MARCAS_EXPLICACION = (
    "es decir", "esto es", "o sea", "significa", "quiere decir", "es cuando",
    "es el", "es la", "es lo que", "(", "—", "se refiere a", "consiste en",
)


def jerga_sin_explicar(texto: str, *, ventana: int = 90) -> list[str]:
    """Lista los tecnicismos del glosario presentes en ``texto`` sin explicación cercana.

    Heurística: si un término aparece y dentro de una ventana de caracteres a su
    derecha hay una marca de explicación (paréntesis, "es decir", "significa"…),
    se considera explicado. Si no, es jerga cruda.
    """
    norm = _norm(texto)
    sueltos: list[str] = []
    for termino in GLOSARIO:
        idx = norm.find(termino)
        if idx == -1:
            continue
        cola = norm[idx : idx + len(termino) + ventana]
        if any(marca in cola for marca in _MARCAS_EXPLICACION):
            continue
        sueltos.append(termino)
    return sueltos
