# data/

Datos descargados y procesados. **No se versionan** ([ADR 0004](../docs/adr/0004-no-redistribuir-datos-de-terceros.md)).
Se generan con los comandos de `openmar`.

| Carpeta | Qué va | Se genera con |
|---|---|---|
| `bronze/` | Lo que llega de cada fuente, sin tocar. Cada archivo tiene al lado un `.meta.json` con la URL y la fecha de descarga. | `openmar descargar todo` |
| `silver/` | Una tabla limpia por concepto, con nombres de buques unificados. | `openmar silver` |
| `gold/` | Cruces listos para usar y las capas del mapa (`gold/mapa/`). | `openmar gold` |

Ver [ADR 0006](../docs/adr/0006-capas-de-datos.md).
