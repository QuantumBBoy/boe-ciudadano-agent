"""Vigilancia de vigencia: ¿esto sigue en vigor?

Cruza dos fuentes del BOE:
  - metadatos / estado de consolidación  (``get_law_metadata``)
  - análisis de referencias posteriores   (``get_law_analysis``)

…y produce un veredicto de vigencia explicable: vigente, derogada (total o
parcial) o modificada, con la lista de normas que la afectan y los artículos
tocados cuando constan.

Diseñado para ser tolerante a la forma del JSON del BOE (claves en español, a
veces anidadas, a veces ausentes): nunca afirma lo que no encuentra. Si un dato
no está, lo deja como desconocido en vez de inventarlo.

Python puro: lo prueban los tests (con metadatos/análisis simulados) y lo expone
la tool ``evaluar_vigencia`` que usa el subagente `rastreador`.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Afectacion", "VeredictoVigencia", "evaluar_vigencia"]


@dataclass(frozen=True)
class Afectacion:
    """Una norma posterior que afecta a la consultada."""

    tipo: str  # "derogacion", "modificacion", "otra"
    norma: str | None  # identificador/título de la norma que afecta
    texto: str  # descripción tal cual la da el BOE
    alcance: str  # "total", "parcial", "desconocido"
    preceptos: list[str] = field(default_factory=list)  # artículos afectados, si constan


@dataclass(frozen=True)
class VeredictoVigencia:
    law_id: str
    estado: str  # "vigente", "derogada", "parcialmente_derogada", "modificada", "desconocido"
    vigente: bool | None  # None = no se puede afirmar con los datos disponibles
    afectaciones: list[Afectacion] = field(default_factory=list)
    estado_consolidacion: str | None = None
    advertencia_fuente: str = (
        "El texto consolidado es una elaboración con valor informativo: NO es la "
        "fuente oficial. La versión auténtica es la publicada en el BOE original "
        "({law_id}). Consúltalo en https://www.boe.es para usos con efectos jurídicos."
    )

    def fuente_oficial(self) -> str:
        return self.advertencia_fuente.format(law_id=self.law_id)


def _norm(text: Any) -> str:
    text = str(text or "").lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _dig(data: Any, *keys: str) -> Any:
    """Busca la primera clave presente (case-insensitive) en un dict, recursivo poco profundo."""
    if not isinstance(data, dict):
        return None
    lowered = {str(k).lower(): v for k, v in data.items()}
    for key in keys:
        if key.lower() in lowered:
            return lowered[key.lower()]
    return None


def _collect_text(item: Any) -> str:
    """Extrae un texto legible de una entrada de análisis con forma variable."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for k in ("texto", "text", "titulo", "title", "descripcion", "descripción", "valor"):
            v = _dig(item, k)
            if isinstance(v, str) and v.strip():
                return v
        # último recurso: aplanar valores string
        parts = [str(v) for v in item.values() if isinstance(v, (str, int))]
        return " ".join(parts)
    return str(item)


def _norma_id(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    for k in ("referencia", "id", "identificador", "norma", "boe", "codigo"):
        v = _dig(item, k)
        if isinstance(v, str) and v.strip():
            return v
    return None


def _preceptos(item: Any) -> list[str]:
    if not isinstance(item, dict):
        return []
    out: list[str] = []
    for k in ("preceptos", "articulos", "artículos", "precepto", "articulo", "artículo"):
        v = _dig(item, k)
        for entry in _as_list(v):
            if isinstance(entry, str) and entry.strip():
                out.append(entry.strip())
            elif isinstance(entry, dict):
                t = _collect_text(entry)
                if t:
                    out.append(t)
    return out


# Palabras que marcan tipo y alcance en el texto de una afectación.
_DEROGA = ("deroga", "derogacion", "derogad")
_MODIFICA = ("modifica", "modificacion", "modificad", "añade", "anade", "suprime", "redaccion", "nueva redaccion")
_TOTAL = ("totalmente", "total", "integra", "en su totalidad", "completa")
_PARCIAL = ("parcial", "parcialmente", "el articulo", "los articulos", "apartado", "disposicion")


def _clasificar(texto_norm: str, preceptos: list[str]) -> tuple[str, str]:
    """Devuelve (tipo, alcance) a partir del texto normalizado."""
    if any(w in texto_norm for w in _DEROGA):
        tipo = "derogacion"
    elif any(w in texto_norm for w in _MODIFICA):
        tipo = "modificacion"
    else:
        tipo = "otra"

    if any(w in texto_norm for w in _TOTAL) and "parcial" not in texto_norm:
        alcance = "total"
    elif preceptos or any(w in texto_norm for w in _PARCIAL):
        alcance = "parcial"
    else:
        # Una derogación sin marca de parcialidad suele ser total; una modificación, parcial.
        alcance = "total" if tipo == "derogacion" else ("parcial" if tipo == "modificacion" else "desconocido")
    return tipo, alcance


def _iter_afecciones(analysis: Any) -> list[Any]:
    """Reúne las entradas de 'afectada por' allá donde el BOE las coloque."""
    candidates: list[Any] = []
    if isinstance(analysis, dict):
        # El análisis del BOE suele exponer "referencias" -> "anteriores"/"posteriores",
        # o bloques tipo "materias"/"notas"/"analisis". Recogemos las posteriores.
        refs = _dig(analysis, "referencias", "references", "analisis", "análisis")
        if isinstance(refs, dict):
            for key in ("posteriores", "posterior", "afectada_por", "afecta_a_esta"):
                candidates.extend(_as_list(_dig(refs, key)))
        # Forma plana
        for key in ("posteriores", "afectada_por", "modificaciones", "derogaciones"):
            candidates.extend(_as_list(_dig(analysis, key)))
    elif isinstance(analysis, list):
        candidates.extend(analysis)
    return candidates


def evaluar_vigencia(law_id: str, metadata: Any, analysis: Any) -> VeredictoVigencia:
    """Construye el veredicto de vigencia cruzando metadatos y análisis.

    Reglas:
      - Si los metadatos marcan vigencia/derogación explícita, manda esa señal.
      - Las afectaciones posteriores del análisis añaden detalle (qué norma, qué
        artículos, total o parcial).
      - Ante ausencia de datos, ``estado='desconocido'`` y ``vigente=None``: no
        afirmamos vigencia que no podemos comprobar.
    """
    estado_consol = None
    estado = "desconocido"
    vigente: bool | None = None

    if isinstance(metadata, dict):
        estado_consol = _dig(metadata, "estado_consolidacion", "estado", "vigencia", "status")
        ec = _norm(estado_consol)
        derog_meta = _dig(metadata, "derogada", "derogado", "fecha_derogacion", "fecha_vigencia_hasta")
        vig_meta = _dig(metadata, "vigente", "en_vigor")
        if "deroga" in ec or (isinstance(derog_meta, str) and derog_meta.strip()) or derog_meta is True:
            estado, vigente = "derogada", False
        elif "vigor" in ec or "vigente" in ec or vig_meta is True:
            estado, vigente = "vigente", True

    afectaciones: list[Afectacion] = []
    for item in _iter_afecciones(analysis):
        texto = _collect_text(item)
        if not texto.strip():
            continue
        preceptos = _preceptos(item)
        tipo, alcance = _clasificar(_norm(texto), preceptos)
        if tipo == "otra" and not preceptos:
            # Referencia que no es claramente derogación ni modificación: la omitimos
            # para no generar ruido (no es una afectación de vigencia).
            continue
        afectaciones.append(
            Afectacion(
                tipo=tipo,
                norma=_norma_id(item),
                texto=texto.strip(),
                alcance=alcance,
                preceptos=preceptos,
            )
        )

    # Derivar estado a partir de afectaciones si los metadatos no fueron concluyentes.
    hay_derog_total = any(a.tipo == "derogacion" and a.alcance == "total" for a in afectaciones)
    hay_derog_parcial = any(a.tipo == "derogacion" and a.alcance == "parcial" for a in afectaciones)
    hay_modif = any(a.tipo == "modificacion" for a in afectaciones)

    if estado != "derogada":
        if hay_derog_total:
            estado, vigente = "derogada", False
        elif hay_derog_parcial and estado != "vigente":
            estado = "parcialmente_derogada"
            vigente = True if vigente is None else vigente
        elif hay_modif and estado == "vigente":
            estado = "modificada"
        elif hay_modif and estado == "desconocido":
            estado = "modificada"

    return VeredictoVigencia(
        law_id=law_id,
        estado=estado,
        vigente=vigente,
        afectaciones=afectaciones,
        estado_consolidacion=str(estado_consol) if estado_consol is not None else None,
    )
