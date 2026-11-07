# openMar

**El Mar Argentino, a la vista de todos.**

Herramienta abierta para cruzar, barco por barco, datos públicos sobre la flota
pesquera argentina: qué hace cada buque en el mar (recorridos y apagones de AIS),
con quién a bordo (observadores del INIDEP) y quién es su armador (registro de la
flota). Cada resultado guarda de qué fuente salió.

Pensada para periodistas de datos, investigadores, organizaciones y cualquiera que
quiera mirar el mar con datos.

![Mapa de openMar: la flota potera argentina con su semáforo de señales](docs/img/mapa.png)

## Qué hace hoy

Para la flota potera (calamar) de 2025:

1. Baja de Global Fishing Watch los poteros con bandera argentina y sus apagones de AIS.
2. Baja del INIDEP el detalle de cada marea y la cobertura de observadores.
3. Baja del Registro de Flota Pesquera el armador, la matrícula y las sanciones.
4. Ubica cada apagón en la marea en la que ocurrió y dice si había observador a bordo.

El resultado es un resumen por buque con un semáforo de señales
([ADR 0008](docs/adr/0008-senales-no-acusaciones.md)), el detalle de cada apagón y
un mapa. Los hallazgos de la primera corrida están en
[`docs/hallazgos-2025.md`](docs/hallazgos-2025.md).

## Instalación

Requiere Python 3.12+, [uv](https://docs.astral.sh/uv/) y `pdftotext` (poppler).

```bash
sudo apt install poppler-utils      # en Debian/Ubuntu
git clone https://github.com/eroveda/openMar openMar && cd openMar
uv sync
```

Pedí un token gratuito de Global Fishing Watch para uso no comercial en
<https://globalfishingwatch.org/our-apis/tokens> y guardalo en un archivo `.env`
(ver `.env.example`):

```
GFW_API_TOKEN=tu-token
```

El `.env` está en `.gitignore`. No lo compartas ni lo pegues en issues.

## Uso

```bash
uv run openmar descargar todo --desde 2025-01-01 --hasta 2025-12-31
uv run openmar silver      # limpia y unifica
uv run openmar gold        # cruza y arma el mapa
uv run openmar publicar    # copia el mapa a site/data y arma buques.csv
```

Los datos se organizan en tres capas ([ADR 0006](docs/adr/0006-capas-de-datos.md)):

| Capa | Qué tiene |
|---|---|
| `data/bronze/` | Lo que llegó de cada fuente, sin tocar, con un `.meta.json` de origen y fecha |
| `data/silver/` | Una tabla limpia por concepto: buques, mareas, apagones, pesca, registro |
| `data/gold/` | Cruces listos para usar y las capas del mapa |

Para ver el mapa en tu máquina: `python3 -m http.server -d site` y abrí
<http://localhost:8000>.

## Fuentes y cómo citarlas

| Fuente | Qué aporta | Cita |
|---|---|---|
| [Global Fishing Watch](https://globalfishingwatch.org) | Identidad de buques y apagones de AIS | Según sus [términos de uso](https://globalfishingwatch.org/our-apis/documentation#terms-of-use) |
| [INIDEP, repositorio Mar Abierto](https://marabierto.inidep.edu.ar) | Mareas por buque y cobertura de observadores | Citar el informe técnico correspondiente |
| [Registro de Flota Pesquera](https://registroflotapesquera.org) | Armador, matrícula, permisos y sanciones | Círculo de Políticas Ambientales y Sin Azul No Hay Verde |

openMar **no redistribuye** datos de terceros: el repositorio trae el código que
los descarga de la fuente original, y cada usuario los baja por su cuenta.

## Cómo leer los resultados

- **Un apagón de AIS no es una infracción.** Los buques argentinos también reportan
  por VMS a las autoridades, y ese dato no es público. Un apagón es una señal para
  investigar.
- El conjunto público de apagones de GFW sólo incluye cortes de 12 horas o más,
  que GFW marca como posible apagado intencional.
- La "franja de la milla 200" se aproxima con la distancia a la costa (300 a 450 km).
  El cálculo exacto contra la línea de la ZEE está pendiente.
- Los informes del INIDEP incluyen nombres de observadores: openMar no los extrae.

## Estado

- [x] Recolectores de GFW, INIDEP y Registro de Flota Pesquera
- [x] Cruce de apagones con mareas y observadores
- [ ] Apagones contra la línea real de la ZEE
- [x] Mapa con semáforo por buque
- [x] Ficha por buque
- [ ] Extracción de las actas del Consejo Federal Pesquero
- [ ] Más pesquerías además del calamar

## Documentación

| Archivo | Qué es |
|---|---|
| [`docs/adr/`](docs/adr/) | Decisiones de arquitectura, con su porqué |
| [`docs/propuesta-de-valor.md`](docs/propuesta-de-valor.md) | Qué aporta openMar, qué no hace y qué sumar |
| [`docs/contexto.md`](docs/contexto.md) | El problema y quién ya trabaja en esto |
| [`docs/arquitectura.md`](docs/arquitectura.md) | Fuentes, modelo y flujo |
| [`docs/hallazgos-2025.md`](docs/hallazgos-2025.md) | Resultados de la primera corrida |
| [`docs/despliegue.md`](docs/despliegue.md) | Cómo ver y publicar el mapa |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Cómo sumarse |

## Licencia

Código: [MIT](LICENSE). Resultados publicados por el proyecto: CC BY-NC 4.0
(propuesta pendiente de aprobación; ver [`LICENSE-DATOS.md`](LICENSE-DATOS.md) y
la revisión 2026-11 del [ADR 0003](docs/adr/0003-licencias.md)).

## Para periodistas

- Una fila por barco en [`site/data/buques.csv`](site/data/buques.csv) (UTF-8,
  separado por comas). Se regenera con `uv run openmar exportar`.
- Cómo citar a openMar y a cada fuente: [`LICENSE-DATOS.md`](LICENSE-DATOS.md).
- ¿Un error o una réplica? [Abrí un issue](https://github.com/eroveda/openMar/issues/new/choose).
