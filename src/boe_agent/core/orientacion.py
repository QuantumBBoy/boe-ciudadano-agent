"""Orientación a recursos de ayuda reales (la cuarta pata).

Mapea el *tipo* de problema a categorías de recursos —priorizando los gratuitos
que mucha gente no sabe que existen— y describe **cómo se accede en términos
generales**. Regla de oro: NO inventar teléfonos, direcciones ni nombres de
oficinas concretas (eso se alucina y hace daño). Solo el tipo de recurso y la vía
genérica de acceso, invitando a verificar el punto local.

Es Python puro: lo prueban los tests y lo expone una tool (`orientar_recursos`)
que usa el subagente `orientador`.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

__all__ = ["Recurso", "Orientacion", "clasificar_problema", "orientar"]


@dataclass(frozen=True)
class Recurso:
    nombre: str
    descripcion: str
    gratuito: bool
    como_acceder: str


@dataclass(frozen=True)
class Orientacion:
    materia: str
    recursos: list[Recurso] = field(default_factory=list)
    nota: str = (
        "Estos son tipos de recurso, no contactos concretos. Verifica el punto "
        "exacto (teléfono, dirección, horario) en la web oficial de tu ayuntamiento, "
        "comunidad autónoma o del organismo correspondiente."
    )


# --- Catálogo de recursos por categoría (genéricos, verificables, sin datos inventados) ---

_AJG = Recurso(
    nombre="Asistencia Jurídica Gratuita / Turno de Oficio",
    descripcion=(
        "Abogado y procurador de oficio sin coste para quien acredita ingresos por "
        "debajo del umbral legal. Cubre muchos procedimientos (civil, penal, laboral, "
        "extranjería, violencia de género, etc.)."
    ),
    gratuito=True,
    como_acceder=(
        "Se solicita en el Servicio de Orientación Jurídica (SOJ) del Colegio de "
        "Abogados de tu provincia o en los juzgados; también en las oficinas de "
        "justicia gratuita. Requiere rellenar un formulario y aportar documentación "
        "de ingresos."
    ),
)

_SOJ = Recurso(
    nombre="Servicio de Orientación Jurídica del Colegio de Abogados",
    descripcion=(
        "Orientación jurídica inicial y gratuita sobre cualquier materia: te dicen si "
        "tienes vía, qué plazos corren y si te corresponde justicia gratuita."
    ),
    gratuito=True,
    como_acceder=(
        "A través del Colegio de Abogados de tu provincia (suelen tener cita previa "
        "presencial o telefónica)."
    ),
)

_OMIC = Recurso(
    nombre="OMIC (Oficina Municipal de Información al Consumidor)",
    descripcion=(
        "Información, mediación y tramitación de reclamaciones de consumo entre "
        "particulares y empresas (telefonía, banca, suministros, compras, garantías…)."
    ),
    gratuito=True,
    como_acceder=(
        "En tu ayuntamiento o a través de la Dirección General de Consumo de tu "
        "comunidad autónoma. Muchas admiten reclamación online."
    ),
)

_ARBITRAJE_CONSUMO = Recurso(
    nombre="Junta Arbitral de Consumo",
    descripcion=(
        "Resuelve conflictos de consumo de forma extrajudicial, rápida y gratuita, si "
        "la empresa está adherida o acepta el arbitraje."
    ),
    gratuito=True,
    como_acceder="A través de la OMIC o de la Junta Arbitral autonómica/municipal.",
)

_MEDIACION = Recurso(
    nombre="Servicios de Mediación",
    descripcion=(
        "Vía extrajudicial para acuerdos en conflictos familiares, civiles, vecinales o "
        "mercantiles, con un mediador neutral. Suele ser más rápida y barata que el juicio."
    ),
    gratuito=False,
    como_acceder=(
        "Centros de mediación de las comunidades autónomas, colegios profesionales o "
        "los registros de mediadores del Ministerio de Justicia. Hay supuestos gratuitos."
    ),
)

_INSPECCION_TRABAJO = Recurso(
    nombre="Inspección de Trabajo y Seguridad Social",
    descripcion=(
        "Recibe denuncias sobre incumplimientos laborales (impagos, jornada, seguridad, "
        "no dar de alta…) e investiga a la empresa."
    ),
    gratuito=True,
    como_acceder="Denuncia online en la sede electrónica del Ministerio de Trabajo, o presencial.",
)

_SMAC = Recurso(
    nombre="Servicio de Mediación, Arbitraje y Conciliación (SMAC / acto de conciliación)",
    descripcion=(
        "Paso previo y obligatorio en muchos conflictos laborales (p. ej. despidos) antes "
        "de ir al juzgado de lo social; intenta un acuerdo."
    ),
    gratuito=True,
    como_acceder="Órgano de mediación laboral de tu comunidad autónoma. Ojo a los plazos (caducan rápido).",
)

_DEFENSOR_PUEBLO = Recurso(
    nombre="Defensor del Pueblo (o autonómico)",
    descripcion=(
        "Supervisa a las administraciones públicas. Útil cuando el conflicto es con un "
        "organismo público (sanidad, educación, prestaciones, trato administrativo)."
    ),
    gratuito=True,
    como_acceder="Queja gratuita por su web. Hay defensorías autonómicas equivalentes.",
)

_SS_INFO = Recurso(
    nombre="Información de la Seguridad Social / SEPE",
    descripcion=(
        "Información oficial sobre pensiones, prestaciones, paro, bajas e incapacidades."
    ),
    gratuito=True,
    como_acceder="Sede electrónica de la Seguridad Social o del SEPE, y oficinas con cita previa.",
)

_VIOLENCIA_016 = Recurso(
    nombre="Recursos de violencia de género (016)",
    descripcion=(
        "Información, asesoramiento jurídico y atención especializada y gratuita, "
        "confidencial y 24 h, para víctimas de violencia de género."
    ),
    gratuito=True,
    como_acceder="Servicio 016 (no deja rastro en la factura), su chat/web y los puntos de atención.",
)

_REGISTRO_CIVIL = Recurso(
    nombre="Registro Civil",
    descripcion="Trámites de estado civil: nacimientos, matrimonios, defunciones, nacionalidad.",
    gratuito=True,
    como_acceder="Registro Civil de tu localidad o sede electrónica del Ministerio de Justicia.",
)


# --- Clasificación de la materia a partir de palabras clave ---

_MATERIAS: dict[str, tuple[str, ...]] = {
    "consumo": (
        "consumidor", "compra", "comprado", "producto", "garantia", "devolucion",
        "reembolso", "factura", "telefonia", "internet", "compañia", "suministro",
        "luz", "gas", "agua", "banco", "comision", "tarjeta", "aerolinea", "vuelo",
        "tienda", "reclamacion", "estafa comercial", "publicidad",
    ),
    "laboral": (
        "despido", "despedir", "trabajo", "empresa", "jefe", "nomina", "salario",
        "sueldo", "horas extra", "jornada", "contrato laboral", "baja", "finiquito",
        "indemnizacion", "alta", "convenio", "sindicato", "eres", "erte",
    ),
    "vivienda": (
        "alquiler", "inquilino", "casero", "arrendador", "arrendatario", "fianza",
        "desahucio", "deshaucio", "hipoteca", "comunidad de vecinos", "okupa",
        "vivienda", "piso", "contrato de arrendamiento", "obras",
    ),
    "familia": (
        "divorcio", "separacion", "custodia", "pension de alimentos", "herencia",
        "testamento", "matrimonio", "pareja de hecho", "patria potestad", "tutela",
    ),
    "administrativo": (
        "multa", "sancion", "ayuntamiento", "administracion", "subvencion",
        "prestacion", "beca", "licencia", "recurso de alzada", "silencio administrativo",
        "expediente", "hacienda", "tributo", "impuesto", "trafico", "dgt",
    ),
    "seguridad_social": (
        "pension", "jubilacion", "paro", "desempleo", "sepe", "incapacidad",
        "seguridad social", "prestacion por desempleo", "baja medica", "ingreso minimo",
    ),
    "extranjeria": (
        "extranjeria", "residencia", "arraigo", "nie", "nacionalidad", "permiso de trabajo",
        "asilo", "reagrupacion",
    ),
    "violencia_genero": (
        "malos tratos", "maltrato", "violencia de genero", "orden de alejamiento",
        "agresion de mi pareja", "violencia machista",
    ),
    "penal": (
        "denuncia", "delito", "robo", "agresion", "amenaza", "estafa", "juicio penal",
        "detenido", "abogado penal",
    ),
}

# Recursos asociados a cada materia (orden = prioridad; gratuitos primero).
_RECURSOS_POR_MATERIA: dict[str, list[Recurso]] = {
    "consumo": [_OMIC, _ARBITRAJE_CONSUMO, _SOJ],
    "laboral": [_SMAC, _INSPECCION_TRABAJO, _AJG, _SOJ],
    "vivienda": [_SOJ, _OMIC, _MEDIACION, _AJG],
    "familia": [_SOJ, _MEDIACION, _AJG, _REGISTRO_CIVIL],
    "administrativo": [_SOJ, _DEFENSOR_PUEBLO, _AJG],
    "seguridad_social": [_SS_INFO, _SOJ, _AJG],
    "extranjeria": [_AJG, _SOJ, _DEFENSOR_PUEBLO],
    "violencia_genero": [_VIOLENCIA_016, _AJG, _SOJ],
    "penal": [_AJG, _SOJ],
    # Genérico cuando no se reconoce la materia.
    "general": [_SOJ, _AJG],
}


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def clasificar_problema(texto: str) -> str:
    """Devuelve la clave de materia más probable, o 'general' si no hay señal.

    Cuenta coincidencias de palabras clave por materia y elige la de mayor score.
    Determinista y explicable (útil para los tests).
    """
    norm = _normalize(texto)
    best, best_score = "general", 0
    for materia, claves in _MATERIAS.items():
        score = sum(1 for c in claves if c in norm)
        if score > best_score:
            best, best_score = materia, score
    return best


def orientar(texto: str) -> Orientacion:
    """Mapea un problema descrito en lenguaje natural a recursos de ayuda."""
    materia = clasificar_problema(texto)
    recursos = _RECURSOS_POR_MATERIA.get(materia, _RECURSOS_POR_MATERIA["general"])
    return Orientacion(materia=materia, recursos=list(recursos))
