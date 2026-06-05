"""Vigilancia de vigencia: cruce de metadatos y análisis (con datos simulados)."""

from boe_agent.core.vigilancia import evaluar_vigencia


def test_detecta_modificacion_posterior():
    metadata = {"estado_consolidacion": "Vigente", "vigente": True}
    analysis = {
        "referencias": {
            "posteriores": [
                {
                    "referencia": "BOE-A-2023-0001",
                    "texto": "Modifica el artículo 7 y añade una disposición adicional",
                    "preceptos": ["art. 7"],
                }
            ]
        }
    }
    v = evaluar_vigencia("BOE-A-1994-26003", metadata, analysis)
    assert v.estado == "modificada"
    assert v.vigente is True
    assert len(v.afectaciones) == 1
    af = v.afectaciones[0]
    assert af.tipo == "modificacion"
    assert af.norma == "BOE-A-2023-0001"
    assert "art. 7" in af.preceptos
    # Siempre avisa de que el consolidado no es la fuente oficial.
    assert "BOE-A-1994-26003" in v.fuente_oficial()


def test_detecta_derogacion_total():
    metadata = {"estado_consolidacion": "Derogada", "fecha_derogacion": "2015-10-02"}
    analysis = {
        "posteriores": [
            {"referencia": "BOE-A-2015-10565", "texto": "Deroga totalmente la presente Ley"}
        ]
    }
    v = evaluar_vigencia("BOE-A-1992-26318", metadata, analysis)
    assert v.estado == "derogada"
    assert v.vigente is False
    assert any(a.tipo == "derogacion" and a.alcance == "total" for a in v.afectaciones)


def test_derogacion_parcial_marca_estado():
    metadata = {"estado_consolidacion": "Vigente"}
    analysis = {
        "posteriores": [
            {
                "referencia": "BOE-A-2020-1",
                "texto": "Deroga el artículo 12 y el apartado 3 del artículo 15",
                "articulos": ["art. 12", "art. 15.3"],
            }
        ]
    }
    v = evaluar_vigencia("BOE-A-2000-1", metadata, analysis)
    assert v.estado in ("parcialmente_derogada", "vigente")
    af = v.afectaciones[0]
    assert af.tipo == "derogacion"
    assert af.alcance == "parcial"
    assert "art. 12" in af.preceptos


def test_sin_datos_no_afirma_vigencia():
    # Ni metadatos concluyentes ni análisis: no se puede confirmar.
    v = evaluar_vigencia("BOE-A-1999-9", {}, {})
    assert v.estado == "desconocido"
    assert v.vigente is None
    assert v.afectaciones == []


def test_tolera_formas_no_json_o_planas():
    # El BOE a veces devuelve listas planas; no debe romper.
    analysis = [
        {"id": "BOE-A-2021-5", "titulo": "Modifica el artículo 1"},
        {"texto": "Mera referencia sin efecto de vigencia"},  # se ignora (tipo 'otra' sin preceptos)
    ]
    v = evaluar_vigencia("BOE-A-2010-3", None, analysis)
    assert len(v.afectaciones) == 1
    assert v.afectaciones[0].tipo == "modificacion"
