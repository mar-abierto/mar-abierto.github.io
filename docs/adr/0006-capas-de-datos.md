# 0006. Capas de datos bronze, silver y gold

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

La primera versión tenía `raw/` y `processed/`. No había una etapa intermedia
limpia y validada sobre la que otros pudieran construir sus propios cruces sin
pelearse con PDFs y APIs.

## Decisión

Los datos se organizan en tres capas (patrón "medallion"):

```
data/
├── bronze/<fuente>/   tal cual vino de la fuente, con su .meta.json
├── silver/            limpio, validado y con el modelo del dominio
│   ├── buques.csv         identidad unificada (nombre normalizado, MMSI, matrícula, armador)
│   ├── mareas.csv         una fila por marea (INIDEP)
│   ├── cobertura.csv      viajes con y sin observador 2021-2024 (INIDEP)
│   ├── apagones.csv       un apagón de AIS por fila (GFW)
│   └── pesca.csv          eventos de pesca (GFW)
└── gold/              cruces listos para usar
    ├── apagones-por-buque.csv
    ├── apagones-detalle.csv
    └── mapa/*.geojson     lo que consume la capa de presentación
```

- Bronze nunca se modifica.
- Silver tiene una sola forma por concepto, sin importar de qué fuente vino.
- Gold se puede regenerar siempre desde silver.

## Consecuencias

- Un periodista que quiere su propio cruce parte de `silver/`.
- La capa de presentación sólo lee `gold/mapa/`: no sabe nada de las fuentes.
- `data/raw` y `data/processed` de la versión anterior pasan a `bronze` y `gold`.
