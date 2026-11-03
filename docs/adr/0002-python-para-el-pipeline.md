# 0002. Python para el pipeline de datos

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

El primer diseño proponía Java 21 con Quarkus, el stack habitual del autor. Pero
quienes van a usar y mejorar openMar son periodistas de datos, investigadores y
organizaciones, que trabajan casi siempre en Python. Las herramientas geográficas
(GeoPandas, Shapely) y de lectura de PDF también están ahí.

## Decisión

- El pipeline (recolectores, cruces, salidas) se escribe en Python 3.12.
- Se gestiona con [uv](https://docs.astral.sh/uv/): un comando (`uv sync`) deja
  todo listo.
- Los PDF se convierten con `pdftotext -layout` (poppler), que conserva las
  columnas de las tablas.
- Dependencias mínimas: hoy sólo `requests`.

## Consecuencias

- Más gente puede contribuir.
- Hay una dependencia del sistema (`poppler-utils`) que se documenta en el README.
- Si en el futuro hace falta una API de alto tráfico, puede escribirse en otro
  lenguaje como un adaptador más (ver ADR 0005), consumiendo la capa silver.
