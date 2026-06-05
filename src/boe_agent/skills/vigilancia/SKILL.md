---
name: vigilancia
description: Cómo comprobar si una norma sigue vigente cruzando su estado de consolidación con las referencias posteriores, y avisar de modificaciones y derogaciones totales o parciales. Úsala cuando el usuario pregunte "¿esto sigue vigente?", "¿está derogada?" o "¿esta ley sigue en vigor?".
license: MIT
---

# Vigilancia (vigencia y cambios)

"¿Esto sigue vigente?" — cruza metadatos y referencias posteriores.

## Cuándo usarla
- Dudas sobre vigencia, derogación o modificaciones de una norma.
- Antes de afirmar que algo "se aplica": comprueba que la norma siga viva.

## Procedimiento
1. Delega en el subagente `rastreador`.
2. Recupera `get_law_metadata` (estado de consolidación) y `get_law_analysis`
   (referencias posteriores) de la norma.
3. Llama a `evaluar_vigencia` con el `law_id` y ambos JSON. Reporta:
   - estado: vigente / derogada / parcialmente derogada / modificada / desconocido,
   - qué normas posteriores la afectan y con qué alcance (total o parcial),
   - los artículos afectados cuando consten.

## Reglas innegociables
- Avisa SIEMPRE de que el texto consolidado NO es la fuente oficial; da el
  `BOE-A-...` del original para acceder a la versión auténtica.
- Si no hay datos para afirmar la vigencia, dilo como "no se puede confirmar con los
  datos disponibles". No supongas vigencia por defecto.
