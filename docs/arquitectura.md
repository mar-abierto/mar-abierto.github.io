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

## Código

| Módulo | Qué hace |
|---|---|
| `openmar/normalize.py` | Lleva los nombres de buques a una forma comparable entre fuentes |
| `openmar/sources/gfw.py` | Cliente de la API de Global Fishing Watch |
| `openmar/sources/inidep.py` | Lectores de los informes del INIDEP |
| `openmar/sources/rfp.py` | Lector del Registro de Flota Pesquera |
| `openmar/cross.py` | Cruce de apagones con mareas |
| `openmar/pipeline.py` | Arma los CSV de salida |
| `openmar/cli.py` | Comandos `openmar descargar` y `openmar cruzar` |
