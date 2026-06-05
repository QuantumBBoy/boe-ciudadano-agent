"""Configuración de la conexión a boe-mcp (función pura, sin lanzar el proceso)."""

from boe_agent.mcp import build_server_config


def test_valores_por_defecto():
    cfg = build_server_config({})
    assert cfg.command == "boe-mcp"
    assert cfg.args == []
    assert cfg.cwd is None
    d = cfg.to_adapter_dict()
    assert d["transport"] == "stdio"
    assert d["command"] == "boe-mcp"


def test_forma_modulo_python():
    cfg = build_server_config(
        {"BOE_MCP_COMMAND": "python", "BOE_MCP_ARGS": "-m boe_mcp.server", "BOE_MCP_CWD": "/repos/BoeMCP"}
    )
    assert cfg.command == "python"
    assert cfg.args == ["-m", "boe_mcp.server"]
    assert cfg.cwd == "/repos/BoeMCP"
    assert cfg.to_adapter_dict()["cwd"] == "/repos/BoeMCP"


def test_command_vacio_cae_en_defecto():
    cfg = build_server_config({"BOE_MCP_COMMAND": "   "})
    assert cfg.command == "boe-mcp"
