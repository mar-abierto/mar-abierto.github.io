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
- [ ] Quitar `noindex` de `site/index.html` y `X-Robots-Tag` de `site/vercel.json`.
- [ ] Quitar el cartel "Borrador · en revisión".
