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

## Publicarlo en Vercel

**Hoy:** el sitio está en <https://openmar.vercel.app> (proyecto `openmar` de Vercel,
sin conexión a GitHub). Como el repositorio no versiona `site/data/`, se publica
desde la máquina que generó los datos. Vercel bloquea los despliegues hechos desde
una carpeta con git si no reconoce al autor del último commit, así que se sube una
copia de `site/` sin git:

```bash
rm -rf /tmp/sitio && cp -r site /tmp/sitio && cd /tmp/sitio && npx vercel deploy --prod --yes
```

`site/.vercel/project.json` (no versionado) liga la carpeta al proyecto.


Hay dos caminos. Cualquiera de los dos deja el despliegue **protegido**: sólo lo
ven las cuentas de tu equipo de Vercel hasta que decidas abrirlo.

### Opción A: desde GitHub (recomendada)

Cada `git push` a `main` actualiza el sitio solo.

1. En GitHub: **Settings → Applications → Vercel → Configure**.
2. En *Repository access*, agregá `openMar` y guardá.
3. En Vercel: **Add New → Project**, elegí `openMar` y en *Root Directory* poné
   `site`. Framework: *Other*. Sin comando de build.
4. En el proyecto: **Settings → Deployment Protection → Vercel Authentication**,
   elegí **All Deployments** para que también la URL de producción quede
   protegida.

### Opción B: desde la terminal

```bash
npx vercel login          # una sola vez
cd site && npx vercel deploy
```

`vercel deploy` sin `--prod` crea un despliegue de vista previa, protegido por
defecto.

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

Hoy el sitio está cerrado a buscadores en cuatro lugares. Todos estos cambios van
juntos, en un mismo commit, y **no se aplican mientras siga el borrador**.

- [ ] **`noindex` en las 4 páginas.** Borrar la línea
      `<meta name="robots" content="noindex, nofollow">` del `<head>` de
      `site/index.html`, `site/tablero.html`, `site/buque.html` y
      `site/mapa.html`.
- [ ] **`X-Robots-Tag` en `site/vercel.json`.** Borrar la línea
      `{ "key": "X-Robots-Tag", "value": "noindex, nofollow" },`.
- [ ] **`site/robots.txt`.** Reemplazar el contenido por:

      User-agent: *
      Allow: /
      Sitemap: https://DOMINIO/sitemap.xml

- [ ] **Badge de borrador en las 4 páginas.** Borrar
      `<p class="top__draft">Borrador · en revisión</p>` de la cabecera de
      `site/index.html`, `site/tablero.html`, `site/buque.html` y
      `site/mapa.html` (la regla `.top__draft` de `site/cabecera.css` puede
      quedar o borrarse).
- [ ] **HSTS, sólo si hay dominio propio con HTTPS ya funcionando.** Agregar en
      `site/vercel.json`, en los headers de `"/(.*)"`:

      { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" },

      Empezar sin `preload`: sólo sumarlo (y anotar el dominio en
      <https://hstspreload.org>) cuando todos los subdominios sirvan HTTPS,
      porque es difícil de deshacer.
- [ ] **Dominio.** Reemplazar `https://openmar.example` en todo el repo (ver
      `pendientes-lanzamiento.md`) y regenerar el CSV con `uv run openmar exportar`.
- [ ] **Protección de Vercel.** En **Settings → Deployment Protection**, sacar la
      protección de la URL de producción (dejarla en las vistas previas).
- [ ] **Comprobar** con `curl -sI https://DOMINIO/ | grep -i robots` (no debe
      aparecer `X-Robots-Tag`), `curl -s https://DOMINIO/robots.txt` y la vista
      previa de un link en <https://www.opengraph.xyz> o en el depurador de
      tarjetas de cada red.
