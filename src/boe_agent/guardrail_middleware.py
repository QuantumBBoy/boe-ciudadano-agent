"""Middleware que aplica el guardarraíl anti-asesoramiento al agente.

Intercepta la llamada al modelo (``wrap_model_call``): si el último mensaje del
usuario pide una decisión sobre su caso personal, inyecta en el system prompt la
directiva [MODO ORIENTACIÓN] que recalibra la respuesta a info + factores +
orientación (nunca un veredicto).

La *detección* vive en ``boe_agent.core.guardrails`` (Python puro, testeado). Aquí
solo la conectamos al ciclo del agente.
"""

from __future__ import annotations

from langchain.agents.middleware import AgentMiddleware

from boe_agent.core.guardrails import detect_applied_advice, recalibration_directive

__all__ = ["AntiAsesoramientoMiddleware"]


def _last_human_text(messages) -> str | None:
    """Texto del último mensaje humano (soporta content str o lista de bloques)."""
    for msg in reversed(messages or []):
        if getattr(msg, "type", None) == "human" or msg.__class__.__name__ == "HumanMessage":
            content = getattr(msg, "content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = [
                    b.get("text", "") if isinstance(b, dict) else str(b)
                    for b in content
                ]
                return " ".join(parts)
            return str(content)
    return None


class AntiAsesoramientoMiddleware(AgentMiddleware):
    """Recalibra la respuesta cuando se pide asesoramiento aplicado."""

    name = "anti_asesoramiento"

    def wrap_model_call(self, request, handler):
        text = _last_human_text(request.messages)
        signal = detect_applied_advice(text or "")
        if signal.triggered:
            base = request.system_prompt or ""
            nuevo = base + "\n\n" + recalibration_directive(signal)
            request = request.override(system_prompt=nuevo)
        return handler(request)

    async def awrap_model_call(self, request, handler):
        text = _last_human_text(request.messages)
        signal = detect_applied_advice(text or "")
        if signal.triggered:
            base = request.system_prompt or ""
            nuevo = base + "\n\n" + recalibration_directive(signal)
            request = request.override(system_prompt=nuevo)
        return await handler(request)
