"""Divulgación: un buen resumen explica los tecnicismos en vez de soltarlos."""

from boe_agent.core.divulgacion import explicar, jerga_sin_explicar


def test_detecta_tecnicismo_crudo():
    crudo = "La acción ha sufrido prescripción y no cabe recurso de alzada."
    sueltos = jerga_sin_explicar(crudo)
    assert "prescripcion" in sueltos
    assert "recurso de alzada" in sueltos


def test_no_marca_termino_ya_explicado():
    explicado = (
        "La acción ha sufrido prescripción (es decir, ha pasado el plazo en el que "
        "te podían reclamar) y por eso no procede."
    )
    sueltos = jerga_sin_explicar(explicado)
    assert "prescripcion" not in sueltos


def test_explicar_devuelve_lenguaje_llano():
    exp = explicar("silencio administrativo")
    assert exp and "Administración" in exp


def test_termino_fuera_de_glosario_devuelve_none():
    assert explicar("bicicleta") is None
