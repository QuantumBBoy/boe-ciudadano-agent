"""Verificador de respaldo: lo no recuperado del BOE no se afirma."""

from boe_agent.core.verificacion import extraer_afirmaciones, verificar_respaldo


def test_afirmacion_no_presente_se_marca_no_confirmada():
    respuesta = "Según el BOE-A-2015-11430, el plazo es de 30 días y la multa de 200 euros."
    evidencia = ["Documento BOE-A-2015-11430: el plazo para recurrir es de 30 días."]
    reporte = verificar_respaldo(respuesta, evidencia)
    # El BOE-id y el plazo están respaldados; los 200 euros NO aparecen en la evidencia.
    no_conf = {c.tipo for c in reporte.no_confirmadas}
    assert "importe" in no_conf
    assert not reporte.todo_respaldado
    assert "200" in reporte.resumen()


def test_todo_respaldado_cuando_la_evidencia_cubre():
    respuesta = "El artículo 7 del BOE-A-1994-26003 fija un plazo de 3 meses."
    evidencia = [
        "BOE-A-1994-26003, artículo 7: el plazo será de 3 meses desde la notificación."
    ]
    reporte = verificar_respaldo(respuesta, evidencia)
    assert reporte.todo_respaldado, reporte.resumen()


def test_identificador_boe_inventado_se_detecta():
    respuesta = "La norma aplicable es la BOE-A-2099-99999."  # no existe en la evidencia
    evidencia = ["Resultado de búsqueda: BOE-A-1980-1234 sobre la materia."]
    reporte = verificar_respaldo(respuesta, evidencia)
    assert any(c.tipo == "boe_id" for c in reporte.no_confirmadas)


def test_tolera_formato_de_cifras():
    # "1.000 €" en la respuesta vs "1000 euros" en la evidencia: misma cifra.
    respuesta = "La cuantía máxima es de 1.000 €."
    evidencia = ["El importe máximo asciende a 1000 euros."]
    reporte = verificar_respaldo(respuesta, evidencia)
    assert reporte.todo_respaldado, reporte.resumen()


def test_extrae_tipos_de_afirmacion():
    tipos = {c.tipo for c in extraer_afirmaciones(
        "BOE-A-2020-1, artículo 5, 15 días, 21 %, 500 euros, 3 de mayo de 2020"
    )}
    assert {"boe_id", "articulo", "plazo", "porcentaje", "importe", "fecha"} <= tipos
