"""El agente se ensambla (grafo deepagents) con tools y modelo simulados, sin red."""

from boe_agent.agent import assemble_agent
from boe_agent.subagents import build_subagents
from boe_agent.tools import LOCAL_TOOLS


def test_build_subagents_define_los_cinco(fake_boe_tools):
    subs = build_subagents(fake_boe_tools)
    nombres = {s["name"] for s in subs}
    assert nombres == {"divulgador", "investigador", "rastreador", "orientador", "verificador"}
    # El rastreador lleva la tool local de vigencia.
    rastreador = next(s for s in subs if s["name"] == "rastreador")
    assert any(getattr(t, "name", "") == "evaluar_vigencia" for t in rastreador["tools"])
    # El orientador solo orienta (no toca el BOE directamente).
    orientador = next(s for s in subs if s["name"] == "orientador")
    assert [getattr(t, "name", "") for t in orientador["tools"]] == ["orientar_recursos"]


def test_tools_locales_disponibles():
    nombres = {getattr(t, "name", "") for t in LOCAL_TOOLS}
    assert nombres == {
        "orientar_recursos",
        "evaluar_vigencia",
        "verificar_respaldo",
        "glosario_jerga",
        "explicar_termino",
    }


def test_assemble_agent_construye_grafo_invocable(fake_boe_tools, fake_model):
    agent = assemble_agent(fake_boe_tools, model=fake_model)
    # Es un grafo compilado de LangGraph: expone invoke/ainvoke.
    assert hasattr(agent, "invoke")
    assert hasattr(agent, "ainvoke")
