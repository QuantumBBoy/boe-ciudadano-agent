"""Fixtures compartidas: tools del BOE simuladas y un modelo falso."""

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.tools import tool


@pytest.fixture
def fake_boe_tools():
    """Stubs con los mismos nombres que las tools reales del boe-mcp."""

    @tool
    def search_legislation(query: str) -> str:
        """Busca legislación por materia o texto."""
        return "[]"

    @tool
    def get_law_metadata(law_id: str) -> str:
        """Metadatos y estado de consolidación de una norma."""
        return "{}"

    @tool
    def get_law_analysis(law_id: str) -> str:
        """Análisis de referencias de una norma."""
        return "{}"

    @tool
    def get_law_index(law_id: str) -> str:
        """Índice (estructura) de una norma."""
        return "[]"

    @tool
    def get_law_block(law_id: str, block_id: str) -> str:
        """Bloque de texto de una norma."""
        return ""

    @tool
    def get_law(law_id: str) -> str:
        """Ficha de una norma."""
        return "{}"

    @tool
    def lookup_matters(name_filter: str = "") -> str:
        """Tabla de materias."""
        return "[]"

    @tool
    def lookup_legal_ranges(name_filter: str = "") -> str:
        """Tabla de rangos legales."""
        return "[]"

    return [
        search_legislation,
        get_law_metadata,
        get_law_analysis,
        get_law_index,
        get_law_block,
        get_law,
        lookup_matters,
        lookup_legal_ranges,
    ]


@pytest.fixture
def fake_model():
    """Modelo que responde un texto fijo sin tool calls (cierra el bucle del agente)."""
    from langchain_core.messages import AIMessage

    return GenericFakeChatModel(messages=iter([AIMessage(content="respuesta de prueba")]))
