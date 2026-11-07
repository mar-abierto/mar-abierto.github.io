# Arquitectura

Primera versión. Se ajusta después del demo.

## Fuentes de datos

| Fuente | Qué aporta | Formato | A verificar |
|---|---|---|---|
| Global Fishing Watch (API) | Recorridos AIS, eventos de pesca, apagones (gaps), encuentros entre barcos | API REST con token gratuito para uso no comercial | Términos de uso para publicar datos derivados |
| INIDEP | Cobertura de observadores por buque y marea, informes de pesquería | PDF | Si hay detalle por buque o sólo agregados |
| Consejo Federal Pesquero | Permisos, cuotas, sanciones | Actas en PDF | Frecuencia y formato de publicación |
| Boletín Oficial | Resoluciones de pesca, sanciones | Web / PDF | Búsqueda por fecha y sección |
| Prefectura Naval | Multas, interceptaciones | Comunicados de prensa | — |
| Registros societarios (IGJ y provinciales) | Dueños y socios de las empresas | Variable | La pieza más difícil de conseguir |
| Registros de la OMI | Número IMO, bandera, dueño registrado | Web | — |

## Modelo

```
Empresa ──< Buque ──< Permiso
              │
              ├──< Marea ──── Observador (sí/no)
              ├──< EventoAIS (pesca, apagón, encuentro, entrada a zona)
              ├──< Sanción
              └──< Alerta
Fuente ──< (todo registro guarda de dónde salió y cuándo se tomó)
```

El buque se identifica por número IMO cuando existe; si no, por MMSI, matrícula y
nombre. Reconocer que dos registros escritos distinto hablan del mismo barco
(resolución de entidades) es una de las partes centrales del sistema.

## Flujo

1. **Ingesta**: un recolector por fuente guarda el dato crudo sin tocar, con fecha
   y origen.
2. **Extracción**: los PDF pasan por un extractor con IA que devuelve permisos,
   sanciones y cifras en formato estructurado, con la página de origen.
3. **Resolución de entidades**: une los registros de un mismo barco y de una misma
   empresa.
4. **Reglas y alertas**: mareas sin observador, apagones de AIS cerca de la milla
   200, entradas a zonas vedadas, cambios de dueño o bandera.
5. **Publicación**: fichas por barco, mapa e informes, cada dato con su fuente.

## Stack

- **Lenguaje**: Python 3.12, gestionado con uv. Es lo que usa la comunidad de
  datos abiertos y periodismo de datos.
- **PDF**: `pdftotext -layout` (poppler) para conservar las columnas de las tablas.
- **Salidas**: CSV en `data/processed/`.
- **Próximo**: PostGIS o GeoPandas para el cálculo contra la línea de la ZEE;
  extracción con modelo de lenguaje para las actas del CFP, guardando la página y
  el fragmento de origen de cada valor.

## Descarga de GFW

- **Buques**: la búsqueda se acota a los poteros argentinos que transmitieron en
  el período. Sin acotar, la API anuncia más de 100 buques pero su paginación no
  pasa de 100; si alguna vez entrega menos que el total anunciado, la descarga falla.
- **Identidades**: GFW parte un buque en varias identidades de AIS y ata cada
  evento a la que lo emitió. Se piden eventos para todas las identidades cuyo tramo
  de transmisión se solapa con el período.
- **Errores**: ante 429, 5xx, timeout o corte de conexión se reintenta tres veces
  (esperas de 2, 4 y 8 s); después, `GFWError`. Llegar al tope de páginas con más
  por venir también es `GFWError`: no se publican datos truncados en silencio.
- **Duplicados**: los eventos se deduplican por `id`; los que no tienen id se
  conservan.

## Código

Arquitectura hexagonal ([ADR 0005](adr/0005-arquitectura-hexagonal.md)): las
dependencias apuntan hacia adentro.

| Capa | Módulo | Qué hace |
|---|---|---|
| Dominio | `domain/model.py` | `Trip`, `Coverage`, `AisGap`, `FishingEvent`, `RegistryRecord` |
| Dominio | `domain/names.py` | Nombre para mostrar y clave para cruzar fuentes |
| Dominio | `domain/matching.py` | Cruce de apagones con mareas (fechas locales, ADR 0007) |
| Dominio | `domain/signals.py` | Semáforo de señales (ADR 0008) |
| Dominio | `domain/positions.py` | Zona habitual de pesca de cada buque |
| Puertos | `ports.py` | `RawStore`: guardar y leer la capa bronze |
| Adaptadores | `adapters/gfw.py`, `inidep.py`, `rfp.py`, `geo.py` | Una pieza por fuente |
| Adaptadores | `adapters/filesystem.py`, `tabular.py` | Disco y CSV |
| Aplicación | `application/download.py` | Fuentes → bronze |
| Aplicación | `application/silver.py` | Bronze → silver |
| Aplicación | `application/gold.py` | Silver → gold y mapa |
| Entrada | `cli.py` | `openmar descargar`, `silver`, `gold`, `publicar` |
| Presentación | `site/` | Mapa estático (ADR 0009) |
