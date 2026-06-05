# boe-ciudadano-agent

[![CI](https://github.com/QuantumBBoy/boe-ciudadano-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/QuantumBBoy/boe-ciudadano-agent/actions/workflows/ci.yml)

**Asistente que hace accesible la legislación española a la ciudadanía** — traduce
a lenguaje llano, localiza la norma aplicable, avisa de cambios y derogaciones, y
orienta hacia recursos de ayuda (incluidos los gratuitos). **Herramienta de
comprensión y orientación, no de asesoramiento jurídico aplicado.**

Es un *deep agent* (LangChain [deepagents](https://docs.langchain.com/oss/python/deepagents/overview)
sobre LangGraph) que reaprovecha el servidor MCP [boe-mcp](https://github.com/QuantumBBoy/boe-mcp)
para hablar con la API de datos abiertos del BOE.

## La misión

Derribar la barrera de acceso a la ley para gente sin formación jurídica, atacando
las cuatro cosas que la hacen opaca: **el lenguaje incomprensible**, **no saber qué
norma te aplica**, **no saber si sigue vigente**, y **no saber a dónde acudir**.

## Las cuatro capacidades (un solo agente)

El usuario no elige capacidad: el agente decide cuáles activar. Un *"me ha llegado
esto, ¿qué hago?"* combina las cuatro.

| | Capacidad | Subagente | Núcleo determinista |
|---|---|---|---|
| 1 | **Traducir** — reescribe la ley en lenguaje llano, explicando los tecnicismos | `divulgador` | [`core/divulgacion.py`](src/boe_agent/core/divulgacion.py) |
| 2 | **Encontrar** — "¿qué ley me aplica?": búsqueda multi-paso y dossier | `investigador` | — (orquestación + tools BOE) |
| 3 | **Vigilar** — "¿sigue vigente?": cruza consolidación + referencias posteriores | `rastreador` | [`core/vigilancia.py`](src/boe_agent/core/vigilancia.py) |
| 4 | **Orientar** — mapea el problema a recursos de ayuda gratuitos | `orientador` | [`core/orientacion.py`](src/boe_agent/core/orientacion.py) |

Más un quinto subagente transversal, **`verificador`**, que comprueba que cada
afirmación legal esté respaldada por un dato recuperado del BOE
([`core/verificacion.py`](src/boe_agent/core/verificacion.py)); lo no respaldado se
marca como no confirmado.

## El límite, construido (no pegado)

El que el agente **no decida por ti en tu caso concreto** es una característica de
diseño deliberada para no perjudicar a los usuarios más vulnerables, que son los que
actuarían sobre una respuesta errónea sin red de seguridad. Es ingeniería, no un
disclaimer al final:

- **Detección de asesoramiento aplicado** ([`core/guardrails.py`](src/boe_agent/core/guardrails.py),
  aplicada por [`guardrail_middleware.py`](src/boe_agent/guardrail_middleware.py)):
  cuando la consulta pide una decisión sobre el caso personal ("¿tengo que pagar?",
  "¿me conviene firmar?"), el agente cambia de modo y responde con **(a)** la
  información normativa explicada, **(b)** los factores concretos de los que depende
  la respuesta, y **(c)** la orientación al recurso que sí puede resolverlo. Da más
  poder real que un sí/no.
- **Tono calibrado**: la certeza se reserva para lo que el BOE dice literalmente; la
  incertidumbre se hace explícita para todo lo demás.
- **Verificador de respaldo**: subagente que evita afirmar lo que el modelo no
  recuperó del BOE.

## Arquitectura

```
Orquestador (create_deep_agent)
├── middleware: AntiAsesoramientoMiddleware  ← guardarraíl construido
├── skills (SKILL.md, carga progresiva): traducir · encontrar · vigilancia · orientar
├── tools del BOE  ── por MCP (stdio) ──▶  boe-mcp ──▶ API datos abiertos del BOE
├── tools locales: orientar_recursos · evaluar_vigencia · verificar_respaldo · glosario_jerga · explicar_termino
└── subagentes (contexto aislado): divulgador · investigador · rastreador · orientador · verificador
```

El **núcleo determinista** de cada capacidad vive en [`src/boe_agent/core/`](src/boe_agent/core):
Python puro, sin LLM ni red. Esa lógica auditable es la que (a) se expone como tools,
(b) alimenta a los subagentes y al guardarraíl, y (c) prueban los tests sin necesidad
de un modelo en vivo.

## Instalación

```bash
python -m venv .venv && source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env   # añade tu ANTHROPIC_API_KEY y configura boe-mcp
```

> Para desarrollo iterativo puedes usar `pip install -e ".[dev]"`. La batería de
> tests se ejecuta contra el árbol de fuentes (`pythonpath = ["src"]` en
> `pyproject.toml`), así que `pytest` funciona con o sin instalación editable.

Necesitas el servidor **boe-mcp** accesible. Por defecto el agente lo lanza con el
console-script `boe-mcp`; si prefieres ejecutarlo desde su repo, configura en `.env`:

```dotenv
BOE_MCP_COMMAND=python
BOE_MCP_ARGS=-m boe_mcp.server
BOE_MCP_CWD=/ruta/a/BoeMCP
```

## Uso

```bash
# Pregunta directa
boe-ciudadano "¿Qué ley regula los plazos de devolución de una compra online?"

# Modo interactivo
boe-ciudadano
```

Desde Python:

```python
from boe_agent.agent import build_agent

agent = await build_agent()
result = await agent.ainvoke({"messages": [{"role": "user", "content": "¿Sigue vigente la LAU de 1994?"}]})
print(result["messages"][-1].content)
```

Ver [`examples/`](examples/) para consultas de demostración, incluida una
(`06_asesoramiento_guardarrail.txt`) que dispara el guardarraíl.

## Tests

Los tests cubren el núcleo determinista sin necesidad de red ni LLM:

```bash
pytest                 # núcleo: guardarraíl, vigilancia, verificación, orientación, divulgación, ensamblado
RUN_LIVE=1 pytest -m live   # smoke opcional contra boe-mcp real + ANTHROPIC_API_KEY
```

| Test | Qué garantiza |
|---|---|
| `test_guardrails.py` / `test_guardrail_middleware.py` | Una consulta de decisión personal recalibra a info+factores+orientación, nunca un veredicto. |
| `test_vigilancia.py` | Una norma con modificación/derogación posterior (simulada) se detecta y se avisa. |
| `test_verificacion.py` | Un dato ausente en el resultado de tool no se afirma (se marca no confirmado). |
| `test_divulgacion.py` | El resumen explica los tecnicismos en vez de soltarlos. |
| `test_orientacion.py` | Consumo → OMIC; laboral → turno de oficio/inspección; sin inventar contactos. |
| `test_assembly.py` | El grafo deepagents (orquestador + 5 subagentes + guardarraíl) se ensambla. |

## Nota sobre la fuente

El texto consolidado del BOE tiene **valor informativo**; la versión auténtica es la
del BOE original. El agente cita siempre el identificador `BOE-A-...` para acceder a
la fuente oficial en <https://www.boe.es>.

## Licencia

MIT. Datos: [BOE — Datos Abiertos](https://www.boe.es/datosabiertos/).
