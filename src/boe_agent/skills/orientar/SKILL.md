---
name: orientar
description: Cómo mapear el tipo de problema del usuario a recursos de ayuda reales, priorizando los gratuitos (justicia gratuita/turno de oficio, OMIC, mediación, defensor del pueblo), describiendo cómo se accede en general sin inventar contactos. Úsala cuando el usuario no sepa a dónde acudir o pida ayuda para resolver su situación.
license: MIT
---

# Orientar (recursos de ayuda)

La cuarta pata, la que de verdad empodera: a dónde acudir, priorizando lo gratuito.

## Cuándo usarla
- "¿A dónde voy?", "¿quién me ayuda con esto?", "¿hay algo gratuito?".
- Siempre que recalibres una consulta de asesoramiento aplicado (parte (c)).

## Procedimiento
1. Delega en el subagente `orientador`.
2. Llama a `orientar_recursos` con la descripción del problema. Devuelve el tipo de
   recurso por materia (consumo→OMIC; laboral→turno de oficio/inspección; vivienda,
   familia, administrativo, seguridad social, extranjería, violencia de género…).
3. Para cada recurso explica: qué es, si es gratuito y cómo se accede en general.

## Reglas innegociables
- NUNCA inventes teléfonos, direcciones, nombres de oficinas ni horarios. Eso se
  alucina y hace daño.
- Invita a verificar el punto local (ayuntamiento, colegio de abogados, comunidad
  autónoma).
- Si la situación puede ser urgente o sensible (violencia, plazos que caducan),
  dilo con claridad y prioriza el recurso adecuado.
