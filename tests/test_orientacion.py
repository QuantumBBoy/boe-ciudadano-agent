"""Orientación: cada tipo de problema lleva al recurso adecuado, sin inventar contactos."""

from boe_agent.core.orientacion import clasificar_problema, orientar


def test_consumo_orienta_a_omic():
    o = orientar("Compré un móvil online y no me devuelven el dinero pese a la garantía")
    assert o.materia == "consumo"
    nombres = " ".join(r.nombre for r in o.recursos)
    assert "OMIC" in nombres


def test_laboral_orienta_a_turno_de_oficio_o_inspeccion():
    o = orientar("Mi empresa no me paga la nómina y me quieren hacer un despido")
    assert o.materia == "laboral"
    nombres = " ".join(r.nombre for r in o.recursos).lower()
    assert "oficio" in nombres or "inspección" in nombres or "conciliación" in nombres


def test_violencia_genero_prioriza_016():
    o = orientar("Sufro malos tratos de mi pareja y necesito ayuda")
    assert o.materia == "violencia_genero"
    assert "016" in o.recursos[0].nombre


def test_materia_desconocida_cae_en_general():
    o = orientar("Tengo una duda rara que no encaja en nada concreto")
    assert o.materia == "general"
    assert o.recursos  # siempre ofrece algo (SOJ / justicia gratuita)


def test_no_inventa_contactos_concretos():
    o = orientar("Problema con el alquiler y la fianza que no me devuelven")
    blob = " ".join(r.como_acceder for r in o.recursos)
    # No deben aparecer teléfonos concretos ni números largos inventados.
    import re

    assert not re.search(r"\b\d{6,}\b", blob), "no debe inventar teléfonos/números concretos"
    assert "verifica" in o.nota.lower()


def test_clasificador_es_determinista():
    txt = "Me han puesto una multa de tráfico injusta"
    assert clasificar_problema(txt) == clasificar_problema(txt) == "administrativo"
