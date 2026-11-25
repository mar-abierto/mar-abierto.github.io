# Pendientes de lanzamiento

Lo que el dueño del proyecto todavía no decidió y quedó con un valor provisorio.
Cada valor es un texto único, fácil de buscar y reemplazar. Cuando se decida,
reemplazarlo, correr las comprobaciones del final y borrar la fila de esta lista.

## 1. Dominio

**Resuelto (25/11/2026):** `https://mar-abierto.github.io`, en GitHub Pages (ADR 0013).
No se compra dominio propio: openMar se publica como proyecto demostrativo.

## 2. Correo público

**Valor provisorio:** vacío (`""`, el enlace no se muestra), en un solo lugar:
`site/enlaces.js`, `ENLACES.correo` (sin `mailto:`).

Lo usan el pie de las 4 páginas ("o escribinos") y el bloque de corrección y
réplica de cada ficha. Si se deja `correo: ""`, el "o escribinos" desaparece y
queda sólo el link a GitHub.

## 3. Link de Cafecito

**Resuelto (13/11/2026):** `https://cafecito.app/openmar`, en `site/enlaces.js`.
Recibe aportes cuando la cuenta tenga un método de pago conectado.

## 4. Licencia de los resultados

**Resuelto (13/11/2026):** CC BY-NC 4.0, aprobada. Queda registrada en la
"Revisión 2026-11" de `docs/adr/0003-licencias.md` y en `LICENSE-DATOS.md`.

## 5. Imagen para compartir: regenerar si cambian los datos

`site/img/compartir.png` es la **única** pieza con cifras fijas: "1 de cada 15",
la cantidad de viajes (354) y con observador (23), la fecha de corte del INIDEP
(5 de junio de 2025) y la fecha de los datos (03/11/2026). Las calcula el script
desde `site/data/resumen.json` y `site/data/fichas.json`. Después de cada
`openmar publicar`, regenerarla:

```bash
uv run --with playwright python scripts/imagen_compartir.py
# la primera vez: uv run --with playwright playwright install chromium
```

El texto alternativo de la imagen (`og:image:alt` y `twitter:image:alt` en el
`<head>` de las 4 páginas) también dice "1 de cada 15": actualizarlo a mano si la
cifra cambia.

## 6. GitHub

**Resuelto (25/11/2026):** el repositorio es público, en
<https://github.com/mar-abierto/mar-abierto.github.io>, y tiene las etiquetas
`correccion` y `replica` que asignan los formularios de `.github/ISSUE_TEMPLATE/`.

## 7. Salida del borrador

**Parcial (13/11/2026):** el cartel dice "Proyecto demostrativo · datos 2025" y el
sitio está online, pero sigue con `noindex` y `robots.txt` cerrado a propósito: se
ve con el link y no aparece en buscadores.

No es un valor pendiente sino una decisión: la checklist exacta está en
`docs/despliegue.md`, "Al abrir el sitio".

## Comprobaciones después de reemplazar

```bash
./scripts/verificar_lanzamiento.sh   # lista todo lo que falta para abrir; sale 0 cuando está listo
uv run pytest
python3 -m http.server -d site 8766    # y revisar el pie y la cita en el navegador
```
