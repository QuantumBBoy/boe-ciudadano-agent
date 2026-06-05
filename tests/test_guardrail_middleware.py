"""El middleware inyecta la directiva [MODO ORIENTACIÓN] en el system prompt
cuando detecta asesoramiento aplicado, y la deja intacta si no.

Probamos el contrato del hook con un ModelRequest simulado (sin LLM ni grafo):
así garantizamos, de forma determinista, que una consulta de decisión personal
recalibra la respuesta en vez de permitir un veredicto.
"""

from langchain_core.messages import AIMessage, HumanMessage

from boe_agent.guardrail_middleware import AntiAsesoramientoMiddleware


class FakeRequest:
    """Sustituto de ModelRequest: expone messages, system_prompt y override()."""

    def __init__(self, messages, system_message_text=""):
        self.messages = messages
        self._sys = system_message_text

    @property
    def system_prompt(self):
        return self._sys

    def override(self, **overrides):
        if "system_prompt" in overrides:
            self._sys = overrides["system_prompt"]
        return self


def _run(req):
    mw = AntiAsesoramientoMiddleware()
    captured = {}

    def handler(r):
        captured["system_prompt"] = r.system_prompt
        return AIMessage(content="ok")

    mw.wrap_model_call(req, handler)
    return captured["system_prompt"]


def test_inyecta_directiva_en_consulta_de_asesoramiento():
    req = FakeRequest(
        messages=[HumanMessage(content="¿Tengo que pagar esta multa?")],
        system_message_text="PROMPT BASE",
    )
    sp = _run(req)
    assert "MODO ORIENTACIÓN" in sp
    assert "DE QUÉ DEPENDE SU CASO" in sp
    assert "A DÓNDE ACUDIR" in sp
    assert sp.startswith("PROMPT BASE")  # no pisa el prompt base, lo amplía


def test_no_inyecta_en_consulta_informativa():
    req = FakeRequest(
        messages=[HumanMessage(content="¿Qué dice el artículo 56 del Estatuto de los Trabajadores?")],
        system_message_text="PROMPT BASE",
    )
    sp = _run(req)
    assert "MODO ORIENTACIÓN" not in sp
    assert sp == "PROMPT BASE"


def test_usa_el_ultimo_mensaje_humano():
    req = FakeRequest(
        messages=[
            HumanMessage(content="Hola"),
            AIMessage(content="¿En qué puedo ayudarte?"),
            HumanMessage(content="¿Me conviene firmar este contrato?"),
        ],
        system_message_text="BASE",
    )
    assert "MODO ORIENTACIÓN" in _run(req)
