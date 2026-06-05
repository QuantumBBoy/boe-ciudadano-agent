"""CLI mínima para conversar con el agente desde la terminal.

  boe-ciudadano "¿qué ley regula los plazos de devolución de una compra online?"
  boe-ciudadano            # modo interactivo

Carga variables de .env, ensambla el agente y muestra la respuesta final.
"""

from __future__ import annotations

import asyncio
import sys

from boe_agent.mcp import MCP_SETUP_HELP


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:  # noqa: BLE001 — dotenv es opcional
        pass


def _final_text(result) -> str:
    """Extrae el texto del último mensaje del resultado de invoke()."""
    messages = result.get("messages", []) if isinstance(result, dict) else []
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if getattr(msg, "type", None) == "ai" and content:
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    b.get("text", "") if isinstance(b, dict) else str(b) for b in content
                )
    return "(sin respuesta)"


async def _ask(agent, pregunta: str) -> str:
    result = await agent.ainvoke({"messages": [{"role": "user", "content": pregunta}]})
    return _final_text(result)


async def _run(pregunta: str | None) -> int:
    from boe_agent.agent import build_agent

    try:
        agent = await build_agent()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if pregunta:
        print(await _ask(agent, pregunta))
        return 0

    print("Agente del BOE para la ciudadanía. Escribe tu consulta (Ctrl-D para salir).\n")
    try:
        while True:
            try:
                pregunta = input("> ").strip()
            except EOFError:
                print()
                break
            if not pregunta:
                continue
            print("\n" + await _ask(agent, pregunta) + "\n")
    except KeyboardInterrupt:
        print()
    return 0


def main() -> int:
    _load_env()
    pregunta = " ".join(sys.argv[1:]).strip() or None
    try:
        return asyncio.run(_run(pregunta))
    except RuntimeError as exc:
        print(MCP_SETUP_HELP if "boe-mcp" not in str(exc) else str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
