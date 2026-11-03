# 0007. Fechas en hora argentina para cruzar fuentes

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

GFW entrega los eventos en UTC. El INIDEP informa las mareas con fechas locales.
Un apagón a las 22 h de Argentina figura en GFW como el día siguiente.

## Decisión

- Para comparar un evento con una marea se usa la fecha del evento en
  `America/Argentina/Buenos_Aires`.
- Un evento se asigna a la marea que contiene ese día. Si ninguna lo contiene, a la
  más cercana dentro de una tolerancia (3 días por defecto). Si dos quedan a la
  misma distancia, gana la que tenía observador.
- Las horas se guardan en UTC en silver; la fecha local se calcula al cruzar.

## Consecuencias

- Los cruces son estables en los bordes de las mareas.
- La tolerancia es un parámetro explícito, documentado en cada salida.
