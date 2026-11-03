# 0011. Alcance: flota extranjera, incursiones y Malvinas

**Estado:** Propuesta · 3 de noviembre de 2026

## Contexto

Hasta ahora openMar cubre sólo la flota potera con bandera argentina. Una prueba
contra la API de Global Fishing Watch para 2025 mostró:

- 35.473 eventos de pesca de buques con bandera china en el área del talud, fuera
  de la ZEE, y 157 apagones de AIS.
- 11 eventos de pesca de buques extranjeros que GFW ubica dentro de la ZEE
  argentina: 9 de dos buques españoles y 1 de un buque coreano, todos a unos
  380–400 km de la costa, pegados a la línea; y 1 de un buque chino a 76 km de la
  costa de Santa Cruz.

La flota extranjera en la milla 201 ya está muy cubierta por otros (ver
`docs/propuesta-de-valor.md`). Los eventos dentro de la ZEE son ambiguos: la
posición de un evento es un punto medio, la línea de la ZEE de Marine Regions
puede incluir la zona en disputa alrededor de Malvinas, y un buque con licencia
británica estaría pescando ahí de forma legal según ese régimen.

## Decisión propuesta

1. **Flota extranjera fuera de la ZEE:** se incorpora sólo como **relación**. Se
   muestra cuando se vincula con buques de bandera argentina del mismo grupo
   empresario (ADR 0010), no como capa propia de "barcos chinos".
2. **Incursiones:** se calculan contra la línea real de la ZEE usando cada punto
   del recorrido, no la posición media del evento. Cada caso pasa por revisión
   manual antes de publicarse. Se publican como señal, con el lenguaje del ADR 0008.
3. **Malvinas:** los eventos dentro de la zona en disputa se separan en una
   categoría propia, "Zona en disputa (Malvinas)", y no se cuentan como incursión.
   El mapa explica por qué. Se mantiene la toponimia en español (ADR 0009).

## Consecuencias

- Hace falta descargar recorridos, no sólo eventos, y un cálculo geométrico contra
  la línea de la ZEE.
- Hace falta una geometría de la zona en disputa con fuente citada.
- La decisión sobre Malvinas es política además de técnica. Queda en "Propuesta"
  hasta que el responsable del proyecto la acepte.
