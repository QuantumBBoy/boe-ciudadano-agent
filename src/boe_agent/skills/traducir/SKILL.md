---
name: traducir
description: Cómo reescribir texto legal del BOE a lenguaje llano para personas sin formación jurídica, marcando y explicando cada tecnicismo en vez de soltarlo. Úsala cuando el usuario pida entender, resumir o "explicar en cristiano" una norma, artículo o documento.
license: MIT
---

# Traducir (divulgación)

El corazón de la democratización: convertir texto legal en algo que cualquiera
entienda, sin perder fidelidad.

## Cuándo usarla
- "¿Qué dice este artículo?", "explícamelo en cristiano", "no entiendo esta ley".
- Cualquier paso en que haya que presentar contenido normativo al usuario final.

## Procedimiento
1. Recupera el contenido real: `get_law_index` para ver la estructura y
   `get_law_block` para las secciones clave. No reescribas de memoria.
2. Delega en el subagente `divulgador`.
3. Para cada fragmento:
   - Empieza con una frase de "qué dice esto en una línea".
   - Desarrolla en frases cortas, voz activa.
   - Marca y EXPLICA cada tecnicismo al lado (entre paréntesis o con "es decir, …").
     Usa `glosario_jerga` para cazar los que se cuelen y `explicar_termino` para
     una explicación llana.
4. No añadas obligaciones, plazos ni consecuencias que el texto no diga.

## Calidad
- Un buen resumen NO deja tecnicismos crudos (prescripción, preceptos, silencio
  administrativo, fehaciente, subrogación…). Si quedan, reescribe.
- Cita el identificador `BOE-A-...` para que el usuario pueda ir al original.
