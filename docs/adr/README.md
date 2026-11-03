# Decisiones de arquitectura (ADR)

Cada decisión importante del proyecto queda escrita acá, con su contexto y sus
consecuencias. Si llegás al proyecto y algo te parece raro, la respuesta
probablemente esté en uno de estos archivos.

| N° | Decisión | Estado |
|---|---|---|
| [0001](0001-registrar-decisiones-con-adr.md) | Registrar las decisiones con ADR | Aceptada |
| [0002](0002-python-para-el-pipeline.md) | Python para el pipeline de datos | Aceptada |
| [0003](0003-licencias.md) | MIT para el código, CC BY 4.0 para los resultados | Aceptada |
| [0004](0004-no-redistribuir-datos-de-terceros.md) | No redistribuir datos de terceros | Aceptada |
| [0005](0005-arquitectura-hexagonal.md) | Arquitectura hexagonal (puertos y adaptadores) | Aceptada |
| [0006](0006-capas-de-datos.md) | Capas de datos bronze, silver y gold | Aceptada |
| [0007](0007-fechas-locales-en-los-cruces.md) | Fechas en hora argentina para cruzar fuentes | Aceptada |
| [0008](0008-senales-no-acusaciones.md) | Señales, no acusaciones: el semáforo | Aceptada |
| [0009](0009-capa-de-presentacion.md) | Mapa estático con MapLibre, publicado en Vercel | Aceptada |

## Cómo escribir uno nuevo

Copiá el formato de cualquiera: **Estado**, **Contexto**, **Decisión**,
**Consecuencias**. Numeralo con el siguiente número libre. Una decisión que cambia
otra no la borra: la marca como "Reemplazada por 00XX".
