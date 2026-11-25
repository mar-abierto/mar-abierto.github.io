# Despliegue del mapa

El mapa es un sitio estático en `site/` (ADR 0009). Los datos del mapa están en
`site/data/` y se regeneran con:

```bash
uv run openmar descargar todo --desde 2025-01-01 --hasta 2025-12-31
uv run openmar silver && uv run openmar gold && uv run openmar publicar
```

## Ver el mapa en tu máquina

```bash
python3 -m http.server -d site 8765
```

y abrí <http://localhost:8765>.

## Publicarlo en GitHub Pages

El sitio está en <https://mar-abierto.github.io> (ADR 0013). Lo publica el robot
`.github/workflows/publicar.yml`, sin pasar por ninguna PC:

- **Cuándo:** todos los días a las 06:17 (hora argentina), con cada push a `main`
  que toque `site/`, `src/` o el workflow, y a mano desde **Actions → publicar →
  Run workflow**.
- **Qué hace:** corre las pruebas, baja las fuentes, arma silver y gold, y sube
  `site/` a Pages. Si algo falla, queda publicada la versión anterior.
- **Qué necesita:** el secreto `GFW_API_TOKEN` en **Settings → Secrets and
  variables → Actions**, y en **Settings → Pages** la fuente *GitHub Actions*.

`site/vercel.json` y `npx vercel deploy --prod` siguen andando mientras Vercel
quede como respaldo en <https://openmar.vercel.app>.

## Antes de hacerlo público

- [ ] Revisar a mano los buques en rojo contra sus fuentes.
- [ ] Confirmar los términos de uso de Global Fishing Watch para publicar datos
      derivados.
- [ ] Avisar al Círculo de Políticas Ambientales que el mapa muestra datos de su
      registro.
- [ ] Resolver los valores pendientes de
      [`pendientes-lanzamiento.md`](pendientes-lanzamiento.md) (dominio, correo,
      Cafecito, licencia).

## Al abrir el sitio (salida del borrador)

Hoy el sitio está cerrado a buscadores en tres lugares. Todos estos cambios van
juntos, en un mismo commit, y **no se aplican mientras siga el borrador**.

- [ ] **`noindex` en las 4 páginas.** Borrar la línea
      `<meta name="robots" content="noindex, nofollow">` del `<head>` de
      `site/index.html`, `site/tablero.html`, `site/buque.html` y
      `site/mapa.html`.
- [ ] **`site/robots.txt`.** Reemplazar el contenido por:

      User-agent: *
      Allow: /
      Sitemap: https://mar-abierto.github.io/sitemap.xml

- [ ] **Badge de borrador en las 4 páginas.** Borrar
      `<p class="top__draft">Borrador · en revisión</p>` de la cabecera de
      `site/index.html`, `site/tablero.html`, `site/buque.html` y
      `site/mapa.html` (la regla `.top__draft` de `site/cabecera.css` puede
      quedar o borrarse).
- [ ] **Comprobar** con `curl -s https://mar-abierto.github.io/robots.txt` y la vista
      previa de un link en <https://www.opengraph.xyz> o en el depurador de
      tarjetas de cada red.
