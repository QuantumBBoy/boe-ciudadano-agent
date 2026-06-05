# Ejemplos de consultas

Cada archivo `.txt` es una consulta de demostración. Con el agente configurado
(`.env` con `ANTHROPIC_API_KEY` y `boe-mcp` accesible):

```bash
boe-ciudadano "$(cat examples/01_traducir.txt)"
```

| Ejemplo | Capacidad que activa | Qué demuestra |
|---|---|---|
| `01_traducir.txt` | Traducir | Reescribe un artículo en lenguaje llano, explicando los tecnicismos. |
| `02_encontrar.txt` | Encontrar | Localiza la norma aplicable a un problema descrito en lenguaje natural. |
| `03_vigilancia.txt` | Vigilar | Comprueba si una norma sigue vigente y avisa de cambios. |
| `04_orientar.txt` | Orientar | Mapea un problema de consumo a recursos de ayuda gratuitos. |
| `05_combinada.txt` | Las cuatro | "Me ha llegado esto, ¿qué hago?": traduce, localiza, vigila y orienta. |
| `06_asesoramiento_guardarrail.txt` | Guardarraíl | Consulta de decisión personal: dispara el modo orientación (info + factores + recurso), **nunca un veredicto**. |
