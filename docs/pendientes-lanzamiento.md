# Pendientes de lanzamiento

Lo que el dueño del proyecto todavía no decidió y quedó con un valor provisorio.
Cada valor es un texto único, fácil de buscar y reemplazar. Cuando se decida,
reemplazarlo, correr las comprobaciones del final y borrar la fila de esta lista.

## 1. Dominio propio

**Valor provisorio:** `https://openmar.example` (el TLD `.example` está reservado y
no resuelve: nunca va a apuntar a un sitio de otro).

| Dónde | Qué es |
|---|---|
| `site/index.html`, `site/tablero.html`, `site/buque.html`, `site/mapa.html` (`<head>`) | `canonical`, `og:url`, `og:image`, `twitter:image` (4 por página) |
| `site/enlaces.js` (`ENLACES.sitio`) | URL que aparece en la cita sugerida de la portada |
| `src/openmar/application/exportar.py` (`SITE_URL`) | Columna `ficha` de `buques.csv` |
| `site/sitemap.xml` | Las 4 URL |
| `site/robots.txt` | Línea `Sitemap:` (comentada mientras siga el borrador) |
| `site/data/buques.csv` | Se regenera, no se edita a mano |

Reemplazo (cambiar `DOMINIO` por el dominio real, sin barra final):

```bash
grep -rl 'https://openmar.example' site src \
  | xargs sed -i 's#https://openmar.example#https://DOMINIO#g'
uv run openmar exportar     # regenera buques.csv con el dominio nuevo
```

Las tarjetas para compartir (Open Graph) necesitan URL absolutas: hasta que haya
dominio, la vista previa de un link no muestra la imagen.

## 2. Correo público

**Valor provisorio:** vacío (`""`, el enlace no se muestra), en un solo lugar:
`site/enlaces.js`, `ENLACES.correo` (sin `mailto:`).

Lo usan el pie de las 4 páginas ("o escribinos") y el bloque de corrección y
réplica de cada ficha. Si se deja `correo: ""`, el "o escribinos" desaparece y
queda sólo el link a GitHub.

## 3. Link de Cafecito

**Valor provisorio:** vacío (`""`, el enlace no se muestra), en un solo lugar:
`site/enlaces.js`, `ENLACES.cafecito`.

Lo usan el "Apoyá openMar" del pie de las 4 páginas y el párrafo de apoyo al final
de la portada. Es un link común (la CSP bloquea los widgets externos). Si se deja
`cafecito: ""`, los dos desaparecen.

## 4. Licencia de los resultados

**Propuesta:** CC BY-NC 4.0, por la condición no comercial de la API de Global
Fishing Watch. Detalle en `LICENSE-DATOS.md` y en la "Revisión 2026-11" de
`docs/adr/0003-licencias.md`.

- **Si se aprueba:** cambiar en el ADR 0003 el estado de la revisión a
  "Aceptada", sacar el aviso de "Propuesta" del principio de `LICENSE-DATOS.md`
  y el "(propuesta pendiente de aprobación…)" de `README.md`.
- **Si no se aprueba:** volver "CC BY-NC 4.0" a "CC BY 4.0" en el `.foot` de las 4
  páginas (`grep -rn 'CC BY-NC' site README.md`), ajustar `LICENSE-DATOS.md` y
  resolver de otra forma la condición no comercial de GFW.

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

- Crear las etiquetas `correccion` y `replica` en el repositorio: los formularios
  de `.github/ISSUE_TEMPLATE/` las asignan, y GitHub las ignora si no existen.
- Los links de corrección, réplica y licencia apuntan a
  `https://github.com/eroveda/openMar`: funcionan cuando el repositorio sea
  público.

## 7. Salida del borrador

No es un valor pendiente sino una decisión: la checklist exacta está en
`docs/despliegue.md`, "Al abrir el sitio".

## Comprobaciones después de reemplazar

```bash
./scripts/verificar_lanzamiento.sh   # lista todo lo que falta para abrir; sale 0 cuando está listo
uv run pytest
python3 -m http.server -d site 8766    # y revisar el pie y la cita en el navegador
```
