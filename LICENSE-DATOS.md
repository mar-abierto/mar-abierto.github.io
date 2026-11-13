# Licencia de los datos y resultados de openMar

El **código** de openMar se publica bajo la [licencia MIT](LICENSE). Este archivo
cubre otra cosa: los **resultados** que publica el proyecto.

## Qué cubre

Los resultados derivados que openMar publica en el sitio y en `site/data/`:

- las cifras, tablas y gráficos del sitio (la historia, el tablero de empresas,
  las fichas por barco y el mapa);
- los archivos de `site/data/`: `buques.csv`, `fichas.json`, `resumen.json` y los
  GeoJSON del mapa;
- los informes con hallazgos que publique el proyecto.

**No cubre** los datos de las fuentes originales, que openMar no redistribuye
(ver [ADR 0004](docs/adr/0004-no-redistribuir-datos-de-terceros.md)). Cada fuente
conserva sus propias condiciones; si las bajás vos, valen esas.

## Licencia: CC BY-NC 4.0

Los resultados se publican bajo
[Creative Commons Atribución-NoComercial 4.0 Internacional (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/deed.es).

Podés copiarlos, redistribuirlos, adaptarlos y usarlos en notas periodísticas,
investigaciones, clases y trabajos de organizaciones, siempre que:

1. **Atribuyas** a openMar y a las fuentes, como se indica abajo.
2. **No los uses con fines comerciales.**

### Por qué no comercial

Una parte de los resultados (cortes de señal, escalas en puerto, eventos de
pesca e identidad de los barcos) se calcula con datos de Global Fishing Watch,
que ofrece su API sólo para uso no comercial, bajo CC BY-NC 4.0. Una obra
derivada no puede dar más permisos que su fuente, así que los resultados heredan
esa condición.

Publicar una nota en un medio que se financia con publicidad o suscripciones,
usando y citando estos datos, es el uso periodístico que el proyecto busca. Si
tenés dudas sobre otro uso, abrí un issue en
<https://github.com/eroveda/openMar/issues>.

## Cómo atribuir

### A openMar

> openMar (versión X.Y.Z). La flota calamarera argentina, barco por barco.
> Temporada, datos generados el DD/MM/AAAA. URL del sitio.

La versión y la fecha están en `site/data/publicacion.json`, y la cita completa
aparece en la sección "Datos y cómo citar" de la portada.

### A Global Fishing Watch

En una página web o una visualización, el texto **"Powered by Global Fishing
Watch."** con un link a <https://globalfishingwatch.org>, como piden sus
[términos de licencia](https://globalfishingwatch.org/our-apis/documentation/docs/license-rate-limits).

En una bibliografía, con el formato de esos términos:

> Global Fishing Watch. [año del aviso de copyright de su portada]. Actualizado a
> diario. [Nombre y versión del conjunto de datos] ([período]). Consultado el
> [AAAA-MM-DD]. https://globalfishingwatch.org/our-apis/

Los conjuntos de datos que usa openMar son `public-global-vessel-identity`,
`public-global-gaps-events`, `public-global-fishing-events` y
`public-global-port-visits-events`, en su versión `latest` a la fecha de la
descarga.

El nombre y el logo de Global Fishing Watch no se pueden usar para sugerir que
respalda un trabajo sin su permiso por escrito.

### Al INIDEP

Citá el informe técnico del que sale cada dato. openMar usa:

> INIDEP. Informe Técnico Oficial 026/2025, Anexo 1 (detalle de las mareas de la
> flota potera). Repositorio Mar Abierto, https://marabierto.inidep.edu.ar

> INIDEP. Informe de observadores a bordo 2024, Tabla 9 (designación de
> observadores 2021–2024). Repositorio Mar Abierto, https://marabierto.inidep.edu.ar

Los informes del INIDEP incluyen nombres de observadores. openMar no los extrae
ni los publica, y pide no republicarlos.

### Al Registro de Flota Pesquera

> Registro de Flota Pesquera, Círculo de Políticas Ambientales y Sin Azul No Hay
> Verde. https://registroflotapesquera.org

El registro no publica una licencia explícita; la matrícula, el armador y las
sanciones se citan como dato de esa fuente.

## Lo que estos datos no dicen

Un corte de señal no es una infracción, y el semáforo marca dónde mirar, no
culpables ([ADR 0008](docs/adr/0008-senales-no-acusaciones.md)). Quien reuse los
resultados debería conservar esa advertencia.

## Correcciones y réplicas

Si encontrás un error o sos parte de una empresa que aparece en los datos y
querés responder, abrí un issue en
<https://github.com/eroveda/openMar/issues/new/choose>.
