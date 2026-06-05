"""Guardarraíl anti-asesoramiento: detección y recalibrado."""

import pytest

from boe_agent.core.guardrails import detect_applied_advice, recalibration_directive

# Consultas que SÍ piden una decisión sobre el caso personal (deben disparar).
ASESORAMIENTO = [
    "¿Tengo que pagar esta multa de tráfico?",
    "¿Puedo despedir a un trabajador que está de baja?",
    "¿Me conviene firmar el finiquito que me ofrecen?",
    "Me ha llegado una carta del banco, ¿qué hago?",
    "¿Me pueden desahuciar si me retraso un mes en el alquiler?",
    "¿Cuánto me corresponde de indemnización por mi despido?",
    "¿Debo aceptar la herencia o la rechazo?",
    "¿Tengo derecho a la pensión de viudedad?",
]

# Consultas informativas / de comprensión (NO deben disparar el guardarraíl).
INFORMATIVAS = [
    "¿Qué dice el artículo 56 del Estatuto de los Trabajadores?",
    "¿Qué ley regula los plazos de devolución en compras online?",
    "Explícame en lenguaje llano qué es la prescripción.",
    "¿Sigue vigente la Ley de Arrendamientos Urbanos de 1994?",
    "¿Qué es una disposición transitoria?",
]


@pytest.mark.parametrize("texto", ASESORAMIENTO)
def test_detecta_asesoramiento_aplicado(texto):
    signal = detect_applied_advice(texto)
    assert signal.triggered, f"debería disparar: {texto!r}"
    assert signal.category and signal.match


@pytest.mark.parametrize("texto", INFORMATIVAS)
def test_no_dispara_en_consultas_informativas(texto):
    signal = detect_applied_advice(texto)
    assert not signal.triggered, f"no debería disparar: {texto!r}"


def test_directiva_de_recalibrado_estructura_la_respuesta():
    signal = detect_applied_advice("¿Tengo que pagar esta deuda?")
    directiva = recalibration_directive(signal)
    # La directiva impone los tres bloques y prohíbe el veredicto.
    assert "MODO ORIENTACIÓN" in directiva
    assert "QUÉ DICE LA NORMA" in directiva
    assert "DE QUÉ DEPENDE SU CASO" in directiva
    assert "A DÓNDE ACUDIR" in directiva
    assert "NO emitas un veredicto" in directiva


def test_texto_vacio_no_dispara():
    assert not detect_applied_advice("").triggered
    assert not detect_applied_advice("   ").triggered
