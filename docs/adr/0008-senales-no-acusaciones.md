# 0008. Señales, no acusaciones: el semáforo

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

openMar nombra buques y empresas reales. Un apagón de AIS no es una infracción:
los buques argentinos reportan además por VMS, que no es público, y hay apagones
que ocurren con observador a bordo (18 de 76 en 2025). Presentar los datos como
acusaciones sería incorrecto y expondría al proyecto a reclamos.

## Decisión

El mapa clasifica a cada buque con un **semáforo de señales para revisar**, con
reglas simples y públicas, calculadas sobre la temporada:

| Color | Nombre | Regla |
|---|---|---|
| 🟢 Verde | Sin señales | Sin apagones de AIS registrados por GFW en la temporada |
| 🟡 Amarillo | Señales aisladas | 1 o 2 apagones en mareas sin observador o fuera de marea, o apagones sólo en mareas con observador |
| 🔴 Rojo | Señales repetidas | 3 o más apagones en mareas sin observador o fuera de marea |

Reglas de lenguaje para todo lo publicado:

- Se describen hechos medibles ("4 apagones de AIS de más de 12 horas en mareas
  sin observador"), nunca conclusiones ("pesca ilegal", "se esconden").
- Cada número muestra su fuente.
- El mapa explica en pantalla qué significa cada color y qué **no** significa.
- Los umbrales se cambian sólo con un ADR nuevo.

## Consecuencias

- El rojo indica dónde mirar primero, no culpables.
- Un buque sin AIS no aparece en los datos de apagones: verde no significa
  "cumple", significa "sin señales en estas fuentes". El mapa lo aclara.
- Ante un reclamo de una empresa, se revisa el dato contra la fuente y se corrige
  públicamente si corresponde (ver CONTRIBUTING).
