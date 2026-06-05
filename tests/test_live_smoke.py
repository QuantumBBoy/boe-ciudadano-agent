"""Smoke en vivo (opcional): requiere boe-mcp real + ANTHROPIC_API_KEY.

Desactivado por defecto. Ejecútalo con:
    RUN_LIVE=1 pytest -m live -k live
"""

import os

import pytest

pytestmark = pytest.mark.live

LIVE = os.getenv("RUN_LIVE") == "1"


@pytest.mark.skipif(not LIVE, reason="define RUN_LIVE=1 para el smoke en vivo")
async def test_smoke_consulta_informativa():
    from boe_agent.agent import build_agent

    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user",
                       "content": "¿Qué ley regula los derechos de las personas consumidoras en España? Cita el BOE-A-..."}]}
    )
    texto = result["messages"][-1].content
    assert isinstance(texto, str) and texto.strip()


@pytest.mark.skipif(not LIVE, reason="define RUN_LIVE=1 para el smoke en vivo")
async def test_smoke_guardarrail_no_da_veredicto():
    from boe_agent.agent import build_agent

    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "¿Tengo que pagar esta multa de tráfico?"}]}
    )
    texto = result["messages"][-1].content.lower()
    # No debe sentenciar; sí debe orientar.
    assert "no tienes que pagar" not in texto
    assert any(p in texto for p in ("depende", "orientación", "recurso", "omic", "colegio de abogados"))
