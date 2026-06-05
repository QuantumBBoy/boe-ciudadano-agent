"""Verificador de respaldo.

Comprueba que cada afirmación legal de una respuesta esté sostenida por un dato
*recuperado del BOE* (lo que devolvieron las tools), no generado por el modelo.
Lo no respaldado se marca como no confirmado.

No es un verificador semántico perfecto —eso requeriría un LLM—; es un colchón
determinista y conservador: extrae las afirmaciones "duras" (identificadores
BOE-A-..., números de artículo, cifras, fechas, porcentajes) y verifica que esos
tokens aparezcan en la evidencia recuperada. Si un identificador o un artículo
citado no está en ninguna respuesta de tool, es una alucinación candidata.

Lo usa el subagente `verificador` (vía la tool ``verificar_respaldo``) y los tests.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

__all__ = ["Claim", "ReporteVerificacion", "extraer_afirmaciones", "verificar_respaldo"]


_BOE_ID = re.compile(r"\bBOE-[A-Z]-\d{4}-\d+\b")
_ARTICULO = re.compile(r"\b(art[íi]culos?|art\.)\s*([0-9]+(?:\s*(?:bis|ter|qu[áa]ter))?)", re.IGNORECASE)
_PORCENTAJE = re.compile(r"\b\d{1,3}(?:[.,]\d+)?\s*%")
_EUROS = re.compile(r"\b\d[\d.\s]*\s*(?:€|euros?)\b", re.IGNORECASE)
_FECHA = re.compile(r"\b\d{1,2}\s+de\s+[a-záéíóú]+\s+de\s+\d{4}\b", re.IGNORECASE)
_PLAZO = re.compile(r"\b\d+\s+(?:d[íi]as?|meses?|años?)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Claim:
    """Una afirmación 'dura' detectada en el texto de la respuesta."""

    tipo: str  # "boe_id", "articulo", "porcentaje", "importe", "fecha", "plazo"
    valor: str  # token normalizado para comparar
    bruto: str  # texto tal cual aparece


@dataclass(frozen=True)
class ReporteVerificacion:
    respaldadas: list[Claim] = field(default_factory=list)
    no_confirmadas: list[Claim] = field(default_factory=list)

    @property
    def todo_respaldado(self) -> bool:
        return not self.no_confirmadas

    def resumen(self) -> str:
        if self.todo_respaldado:
            return "Todas las afirmaciones verificables están respaldadas por datos del BOE."
        items = ", ".join(f"{c.bruto}" for c in self.no_confirmadas)
        return (
            "Afirmaciones NO confirmadas con la evidencia recuperada (márcalas como "
            f"no confirmadas o recupéralas del BOE): {items}"
        )


def _norm(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text)


def _digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def extraer_afirmaciones(respuesta: str) -> list[Claim]:
    """Extrae las afirmaciones verificables del texto de la respuesta."""
    claims: list[Claim] = []
    seen: set[tuple[str, str]] = set()

    def add(tipo: str, valor: str, bruto: str) -> None:
        key = (tipo, valor)
        if valor and key not in seen:
            seen.add(key)
            claims.append(Claim(tipo=tipo, valor=valor, bruto=bruto.strip()))

    for m in _BOE_ID.finditer(respuesta):
        add("boe_id", m.group(0).upper(), m.group(0))
    for m in _ARTICULO.finditer(respuesta):
        add("articulo", _norm(m.group(2)), m.group(0))
    for m in _PORCENTAJE.finditer(respuesta):
        add("porcentaje", _digits(m.group(0)), m.group(0))
    for m in _EUROS.finditer(respuesta):
        add("importe", _digits(m.group(0)), m.group(0))
    for m in _FECHA.finditer(respuesta):
        add("fecha", _norm(m.group(0)), m.group(0))
    for m in _PLAZO.finditer(respuesta):
        add("plazo", _norm(m.group(0)), m.group(0))
    return claims


def _respaldada(claim: Claim, evidencia_norm: str, evidencia_digits: str) -> bool:
    if claim.tipo == "boe_id":
        return claim.valor.lower() in evidencia_norm
    if claim.tipo in ("porcentaje", "importe"):
        # Comparar la secuencia de dígitos para tolerar formatos (1.000 vs 1000).
        return bool(claim.valor) and claim.valor in evidencia_digits
    # articulo, fecha, plazo: comparar el token normalizado.
    return claim.valor in evidencia_norm


def verificar_respaldo(respuesta: str, evidencia: list[str] | str) -> ReporteVerificacion:
    """Verifica las afirmaciones de ``respuesta`` contra la ``evidencia`` recuperada.

    ``evidencia`` son las salidas de las tools del BOE (texto). Una afirmación se
    considera respaldada si su token aparece en la evidencia.
    """
    if isinstance(evidencia, str):
        evidencia = [evidencia]
    blob = "\n".join(evidencia)
    evidencia_norm = _norm(blob)
    evidencia_digits = _digits(blob)

    respaldadas: list[Claim] = []
    no_confirmadas: list[Claim] = []
    for claim in extraer_afirmaciones(respuesta):
        if _respaldada(claim, evidencia_norm, evidencia_digits):
            respaldadas.append(claim)
        else:
            no_confirmadas.append(claim)
    return ReporteVerificacion(respaldadas=respaldadas, no_confirmadas=no_confirmadas)
