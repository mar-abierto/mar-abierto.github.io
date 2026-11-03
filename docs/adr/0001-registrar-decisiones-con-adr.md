# 0001. Registrar las decisiones con ADR

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

openMar es un proyecto abierto. Quien se sume no estuvo en las charlas donde se
decidió por qué las cosas son como son. Sin ese contexto, cada decisión se vuelve
a discutir o, peor, se deshace sin saber qué problema resolvía.

## Decisión

Cada decisión de arquitectura, de datos o de criterio editorial se escribe como un
ADR (Architecture Decision Record) en `docs/adr/`, con cuatro partes: estado,
contexto, decisión y consecuencias.

## Consecuencias

- Una decisión nueva que cambia otra no la borra: la marca como reemplazada.
- Un cambio grande en un pull request debería traer su ADR.
- Cuesta diez minutos por decisión; ahorra horas de discusiones repetidas.
