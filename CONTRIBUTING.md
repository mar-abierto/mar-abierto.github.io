# Cómo sumarse a openMar

Gracias por querer mirar el mar con datos. Toda ayuda suma: código, revisar
resultados, sumar fuentes o corregir errores.

## Antes de empezar

```bash
uv sync
uv run pytest
```

Los tests no usan la red: cada lector se prueba con fragmentos de texto o
respuestas falsas.

## Reglas del proyecto

1. **Cada dato con su fuente.** Todo lo que se descarga se guarda con `save_raw`,
   que deja al lado un `.meta.json` con la URL y la fecha.
2. **No subir datos de terceros al repositorio.** `data/` está en `.gitignore`.
   Se sube el código que los descarga, no los datos.
3. **No exponer secretos.** El token de GFW va en `.env`, nunca en el código, en
   issues ni en logs.
4. **No extraer datos personales.** Los informes oficiales a veces traen nombres de
   personas (por ejemplo, observadores). No se cargan ni se publican.
5. **Señales, no acusaciones.** Los resultados describen datos ("apagón de AIS de
   18 horas en marea sin observador"), no conclusiones ("pesca ilegal").
6. **Primero el test.** Para un lector o un cruce nuevo, escribí el test con un
   fragmento real de la fuente y después el código.

## Ideas para empezar

- Calcular los apagones contra la línea real de la ZEE (en lugar de la distancia a
  la costa).
- Un lector para las actas del Consejo Federal Pesquero.
- Sumar otras pesquerías: merluza, langostino.
- Una ficha por buque en HTML y un mapa.

## Encontraste un error en los datos

Abrí un issue con el buque, la fuente y el dato que no coincide. Si el error está
en una fuente externa, avisamos a quien la publica.
