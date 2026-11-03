# 0009. Mapa estático con MapLibre, publicado en Vercel

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

Además del repositorio, hace falta algo para mostrar a la comunidad: un mapa del
Mar Argentino con cada potero, su semáforo (ADR 0008) y la explicación de su
situación. Los datos cambian poco (una vez por temporada o por semana), y el
proyecto no tiene presupuesto de infraestructura.

## Decisión

- **Sitio estático** en `site/`: HTML, CSS y JavaScript sin paso de build.
- **MapLibre GL JS** desde CDN, con fondo de mapa oscuro de CARTO (con su
  atribución). Un fondo oscuro hace que el semáforo se lea como luces en el mar.
- El sitio sólo lee GeoJSON generados por el caso de uso de publicación en
  `gold/mapa/` y copiados a `site/data/` (ADR 0006).
- **Capas:** buques por color, apagones de AIS, zonas de pesca, límite de la ZEE
  argentina (Marine Regions, MRGID 8466). Un panel lateral las prende y apaga y
  permite buscar por nombre o armador.
- **Publicación en Vercel** como sitio estático. Mientras el contenido no esté
  revisado, el despliegue queda **protegido** (sólo la cuenta del autor lo ve).

## Consecuencias

- Costo cero y nada que mantener del lado del servidor.
- Actualizar el mapa es regenerar los GeoJSON y volver a desplegar.
- Si más adelante hace falta interactividad pesada o datos en vivo, se puede
  migrar a un framework sin cambiar la capa gold.
