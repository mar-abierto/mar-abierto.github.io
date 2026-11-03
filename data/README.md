# data/

Datos descargados y procesados. No se versionan.

| Carpeta | Qué va |
|---|---|
| `raw/` | Lo que llega de cada fuente, sin tocar, con fecha de descarga en el nombre. |
| `processed/` | Datos limpios y cruzados, listos para las fichas. |

Cada archivo de `raw/` tiene que poder rastrearse hasta su fuente: guardar la URL y
la fecha de descarga en un `.meta.json` al lado.
