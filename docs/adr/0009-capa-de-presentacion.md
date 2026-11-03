# 0009. Mapa estático con MapLibre, publicado en Vercel

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

Además del repositorio, hace falta algo para mostrar a la comunidad: un mapa del
Mar Argentino con cada potero, su semáforo (ADR 0008) y la explicación de su
situación. Los datos cambian poco (una vez por temporada o por semana), y el
proyecto no tiene presupuesto de infraestructura.

## Decisión

- **Sitio estático** en `site/`: HTML, CSS y JavaScript sin paso de build.
- **MapLibre GL JS** desde CDN, con fondo de mapa oscuro de OpenFreeMap (con su
  atribución). Un fondo oscuro hace que el semáforo se lea como luces en el mar.
- El sitio sólo lee GeoJSON generados por el caso de uso de publicación en
  `gold/mapa/` y copiados a `site/data/` (ADR 0006).
- **Capas:** buques por color, apagones de AIS, zonas de pesca, límite de la ZEE
  argentina (Marine Regions, MRGID 8466). Un panel lateral las prende y apaga y
  permite buscar por nombre o armador.
- **Publicación en Vercel** como sitio estático. Mientras el contenido no esté
  revisado, el despliegue queda **protegido** (sólo la cuenta del autor lo ve).

**Malvinas.** El polígono de Marine Regions (MRGID 8466) excluye el área en
disputa alrededor de las Islas Malvinas. El mapa lo aclara en pantalla: no es una
posición sobre la soberanía. Las etiquetas del mapa base se muestran en castellano
(`name:es` de OpenStreetMap: "Islas Malvinas", "Puerto Argentino").

**Mapa base.** CARTO pasó a exigir clave de API; se usa OpenFreeMap (estilo
`dark`), abierto y sin clave.

## Consecuencias

- Costo cero y nada que mantener del lado del servidor.
- Actualizar el mapa es regenerar los GeoJSON y volver a desplegar.
- Si más adelante hace falta interactividad pesada o datos en vivo, se puede
  migrar a un framework sin cambiar la capa gold.

## Actualización (3 de noviembre de 2026): portada infográfica

El sitio pasa a tener dos páginas, según `docs/propuesta-de-valor.md`:

- `index.html`: portada que cuenta la historia en seis capítulos (mareas con
  observador, histórico 2021–2024, apagones, la lectura honesta de los apagones,
  buques con señales repetidas y lo que no sabemos).
- `mapa.html`: el mapa. Acepta `?buque=NOMBRE` para abrir la ficha de un buque.

Ninguna cifra de la portada se escribe a mano: salen del bloque `relato` de
`resumen.json`, que calcula `openmar gold` (`domain/story.py`). Las funciones y
la lista de límites compartidas viven en `site/comun.js`; los colores y fuentes, en
`site/tokens.css`. Sin librerías nuevas: los gráficos son HTML y CSS.

