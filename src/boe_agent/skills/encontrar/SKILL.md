---
name: encontrar
description: Cómo localizar la norma aplicable a un problema descrito en lenguaje natural mediante una búsqueda multi-paso en el BOE y escribir un dossier. Úsala cuando el usuario diga "tengo un problema con X, ¿qué ley me aplica?" o pregunte qué norma regula algo.
license: MIT
---

# Encontrar (investigación)

"Tengo un problema con X, ¿qué ley me aplica?" — planifica y ejecuta una búsqueda
multi-paso.

## Cuándo usarla
- El usuario describe una situación y no sabe qué norma la regula.
- Hay que identificar la(s) norma(s) aplicable(s) antes de traducir o vigilar.

## Procedimiento
1. Planifica con `write_todos` si hay varios pasos.
2. Delega en el subagente `investigador`.
3. Traduce el problema a materia(s) y términos; busca con `search_legislation`.
   Apóyate en `lookup_matters` y `lookup_legal_ranges` para acotar.
4. Recupera las candidatas (`get_law_metadata`, `get_law_index`) y razona por qué
   encajan o no.
5. Usa `get_law_analysis` para tejer relaciones (qué desarrolla, qué la modifica).
6. Escribe un DOSSIER: norma(s) con su `BOE-A-...`, por qué aplican, artículos
   relevantes y dudas abiertas. Guarda hallazgos largos en ficheros si es multi-norma.

## Salvaguardas
- Respeta el tope de pasos: no entres en bucle.
- Si no hay una norma clara, dilo. No inventes una ley ni un identificador.
