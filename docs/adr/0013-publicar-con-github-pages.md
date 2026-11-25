# 0013. Publicar con GitHub Pages desde un robot diario

**Estado:** Aceptada · 25 de noviembre de 2026

## Contexto

El sitio se publicaba en Vercel (ADR 0009) desde la máquina que generaba los datos,
porque `site/data/` no se versiona (ADR 0004). Cada actualización dependía de esa
máquina. El proyecto hermano alertaCuencas vive en una organización propia y
publica en GitHub Pages con un robot de GitHub Actions que baja las fuentes y arma
el sitio solo.

## Decisión

- El repositorio pasa a la organización **mar-abierto** con el nombre
  `mar-abierto.github.io`, y el sitio se sirve en <https://mar-abierto.github.io>.
- `.github/workflows/publicar.yml` corre todos los días, a mano y con cada push que
  toca el sitio o el pipeline: corre las pruebas, baja todas las fuentes, arma
  silver y gold, y sube `site/` a Pages.
- Los datos **siguen sin versionarse**: sólo viajan dentro del sitio publicado,
  igual que antes en Vercel.
- El token de Global Fishing Watch va como secreto del repositorio
  (`GFW_API_TOKEN`).
- Si una fuente falla, el job se corta y queda publicada la versión anterior.
- GitHub Pages no acepta cabeceras propias: la política de seguridad (CSP) y la de
  referer pasan a etiquetas `<meta>` en cada página. `X-Frame-Options` y
  `frame-ancestors` no tienen equivalente en `<meta>` y se pierden. `/mapa`
  redirige a la portada con `site/mapa.html`.

## Consecuencias

- El sitio se actualiza sin depender de una PC.
- Sin cabeceras, otro sitio podría mostrar openMar dentro de un `iframe`. Para un
  sitio sin cuentas ni formularios el riesgo es bajo.
- `site/vercel.json` queda mientras Vercel siga como respaldo; se borra al apagarlo.
- Paso siguiente: seguir la temporada en curso (2026) además de 2025.
