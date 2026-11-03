# openMar

**El Mar Argentino, a la vista de todos.**

Observatorio pesquero independiente: una ficha pública por cada barco que pesca en
el Mar Argentino, con quién es su dueño, qué permisos tiene, por dónde anduvo y si
cumple las reglas.

Arrancado el 2 de noviembre de 2026.

---

## El problema en tres líneas

- Detectar barcos ya está resuelto: Prefectura usa su sistema Guardacostas y
  Skylight, y Global Fishing Watch publica datos satelitales gratis.
- Lo que nadie mira es **nuestra propia flota**. En 2025 sólo 9 de 354 mareas de
  poteros llevaron observador a bordo, y 53 de los 84 poteros argentinos serían de
  capital chino.
- Los datos para controlarlo existen, pero están desparramados en PDFs, registros y
  mapas que nadie cruza barco por barco.

El detalle, con fuentes, está en [`docs/contexto.md`](docs/contexto.md).

## Qué hace

1. **Ficha por barco**: dueño, permisos, mareas, observadores, recorridos, multas.
2. **Alertas**: AIS apagado cerca de la milla 200, zonas vedadas, mareas sin
   observador, cambios de dueño o de bandera.
3. **Lectura automática** del Boletín Oficial y las actas del Consejo Federal
   Pesquero.
4. **Mapa e informes públicos**, cada dato con su fuente.

## Dónde está cada cosa

| Archivo | Qué es |
|---|---|
| [`docs/contexto.md`](docs/contexto.md) | El problema, quién ya trabaja en esto y el hueco que cubre openMar. |
| [`docs/arquitectura.md`](docs/arquitectura.md) | Fuentes de datos, modelo, flujo y stack. |
| [`docs/etapa-0-demo.md`](docs/etapa-0-demo.md) | El demo: los 84 poteros argentinos. Es lo próximo a construir. |
| `data/` | Datos descargados y procesados. No se versionan (ver [`data/README.md`](data/README.md)). |

## Estado

- [x] Investigación inicial y contexto
- [ ] Etapa 0: demo con los 84 poteros
- [ ] Validar con especialistas (Milko Schvartzman, Círculo de Políticas Ambientales)
- [ ] Propuesta a Enrique Piñeyro

## Principios

- **Cada dato con su fuente.** Si no se puede citar, no se publica.
- **Sumar, no competir.** Prefectura, Global Fishing Watch, Oceana y los
  investigadores ya hacen su parte; openMar es la pieza que los conecta.
- **Abierto.** Licencia propuesta: AGPL-3.0 para el código y CC BY 4.0 para los
  datos. A confirmar antes de publicar.
