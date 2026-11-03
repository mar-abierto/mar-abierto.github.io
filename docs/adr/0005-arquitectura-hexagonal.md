# 0005. Arquitectura hexagonal (puertos y adaptadores)

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

La primera versión creció "sobre la marcha" y quedó con acoples:

- El cruce (`cross.py`) importaba `Trip` desde el módulo del INIDEP y `Gap` desde
  el de GFW: la lógica central dependía de las fuentes.
- La descarga vivía en el CLI y la lectura en `sources/`, sin un contrato común.
- El pipeline tenía rutas fijas a un informe de un año puntual.

Esto hace que sumar una fuente nueva (Prefectura, actas del CFP) o una pesquería
nueva obligue a tocar el núcleo.

## Decisión

Se organiza el código en anillos, con una sola regla: **las dependencias apuntan
hacia adentro**.

```
src/openmar/
├── domain/        modelo y reglas: sin red, sin archivos, sin librerías externas
├── ports.py       contratos (Protocol) que el dominio y la aplicación necesitan
├── adapters/      una carpeta por fuente o salida; cumplen los contratos
├── application/   casos de uso que orquestan adaptadores y dominio
└── cli.py         adaptador de entrada: traduce comandos a casos de uso
```

- **Dominio:** `Vessel`, `Trip`, `AisGap`, `RegistryRecord`, la normalización de
  nombres, el cruce de apagones con mareas y el semáforo.
- **Puertos:** `RawStore` (guardar y leer datos crudos con su procedencia).
- **Adaptadores:** GFW, INIDEP, Registro de Flota Pesquera, almacenamiento en
  disco, exportación a CSV y GeoJSON.
- **Aplicación:** "descargar una fuente", "construir la capa silver", "construir
  la capa gold".

Se usan `Protocol` de Python, sin frameworks de inyección de dependencias: la
aplicación recibe los adaptadores por parámetro.

## Consecuencias

- Una fuente nueva es una carpeta nueva en `adapters/`; el dominio no cambia.
- El dominio se prueba sin red y sin archivos.
- Hay algo más de estructura que en un script; es el precio de que la comunidad
  pueda sumar piezas sin romper el resto.
- No se agregan microservicios, base de datos ni frameworks mientras un CSV
  alcance (YAGNI).

## Deuda conocida

Hoy los casos de uso de `application/` importan adaptadores concretos (lectores
de CSV, GeoJSON y de cada fuente) en lugar de recibirlos por parámetro. No rompe
la regla de dependencias (el dominio sigue sin conocer a nadie), pero se aparta de
esta decisión. Cuando haga falta una segunda implementación de algún adaptador
(por ejemplo, PostGIS en lugar de CSV), se definen los puertos correspondientes en
`ports.py` y se inyectan.
