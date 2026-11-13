# 0003. MIT para el código, CC BY 4.0 para los resultados

**Estado:** Reemplazada en parte por la revisión 2026-11 (resultados en CC BY-NC 4.0)

## Contexto

Se evaluaron MIT, Apache-2.0 y AGPL-3.0. AGPL obliga a publicar los cambios de
quien use el código en un sitio web; protege que siga abierto, pero espanta a
medios y organismos que podrían usarlo.

## Decisión

- **Código:** MIT. Es la licencia más simple y la que menos fricción genera.
- **Resultados publicados por el proyecto** (informes, mapas, CSV derivados):
  CC BY 4.0, que exige citar a openMar y a las fuentes originales.

## Consecuencias

- Cualquiera puede usar, modificar y redistribuir el código, incluso en productos
  cerrados.
- Los datos de terceros conservan su propia licencia y no se relicencian (ver ADR
  0004).

## Revisión 2026-11 — resultados en CC BY-NC 4.0

**Estado de la revisión:** Aceptada · 13 de noviembre de 2026 (propuesta el 7 de
noviembre, aprobada por el dueño del proyecto).

### Contexto

La API de Global Fishing Watch se ofrece sólo para uso no comercial, bajo CC
BY-NC 4.0, y pide atribuir con el texto "Powered by Global Fishing Watch."
enlazado a su sitio ([términos](https://globalfishingwatch.org/our-apis/documentation/docs/license-rate-limits)).
Los cortes de señal, las escalas y la identidad de los barcos salen de esa API.
Publicar esos resultados bajo CC BY 4.0, que permite el uso comercial, daría más
permisos de los que da la fuente.

### Decisión

- **Código:** sigue en MIT.
- **Resultados:** pasan de CC BY 4.0 a **CC BY-NC 4.0**, con las condiciones y
  el formato de atribución de cada fuente en [`LICENSE-DATOS.md`](../../LICENSE-DATOS.md).
- El pie de las cuatro páginas dice "Resultados CC BY-NC 4.0", enlaza a
  `LICENSE-DATOS.md` y muestra "Powered by Global Fishing Watch.".

### Consecuencias

- Los medios pueden usar y citar los resultados en sus notas; lo que queda
  afuera es revender o empaquetar los datos como producto comercial.
- Si más adelante GFW da un permiso distinto, o los resultados dejan de depender
  de su API, se puede volver a CC BY 4.0.
