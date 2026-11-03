# Contexto

Investigación del 2 de noviembre de 2026. Las cifras vienen de medios, ONG e
informes públicos; las que no son oficiales están marcadas.

## Dos frentes

**Afuera, la milla 201.** Cientos de poteros extranjeros pescan calamar en el borde
de la Zona Económica Exclusiva (ZEE). Ahí es alta mar y es legal, pero el calamar
es el mismo recurso que se cría en aguas argentinas.

- Prefectura registró 776 buques de aguas distantes en doce meses, 418 con bandera
  china ([Infobae, abril 2026](https://www.infobae.com/economia/2026/04/04/impresionante-las-fotos-del-artemis-delatan-la-masiva-presencia-de-buques-chinos-pescando-al-borde-del-mar-argentino/)).
- Oceana documentó más de 6.000 apagones de AIS entre 2018 y abril de 2021, unas
  600.000 horas sin rastro. El 31% de esos barcos terminaba en Montevideo
  ([Oceana, 2021](https://mx.oceana.org/wp-content/uploads/sites/17/2021/06/oceana_argentina_mini_report_finalupdated.pdf)).
- Enrique Piñeyro sobrevoló la milla 200 con su Boeing 787 en 2021 para
  documentarlo ([Meteored](https://www.meteored.com.ar/noticias/actualidad/pesca-extranjera-ilegal-en-el-mar-argentino-sobrevuelo-con-enrique-pineyro-milla-200-depredacion-avion-calamar-buque-meteored.html)).

**Adentro, nuestra flota.** Los "argenchinos": barcos con bandera argentina y
capital chino, que pueden pescar dentro de la ZEE
([Mongabay, febrero 2026](https://es.mongabay.com/2026/02/buques-argentinos-empresas-chinas-pesca-sin-observadores/)).

- 53 de los 84 poteros habilitados serían de capital chino (informe de Milko
  Schvartzman con datos de Global Fishing Watch; no oficial).
- Observadores a bordo, según el INIDEP: en 2025, 7 de 78 buques en 9 de 354
  mareas; en 2024, 12 de 74 buques en 19 de 302 mareas. Entre 2021 y 2024, 62
  embarcaciones nunca llevaron observador. La Disposición 204/2023 lo exige para
  buques de 25 metros o más.
- Denuncias, no verificadas, de que no se cumple el 75% de tripulación argentina
  (Ley 24.922) y de capitanes argentinos que sólo prestan la firma.
- La Subsecretaría de Pesca, el Consejo Federal Pesquero y Cancillería no
  respondieron a las consultas de Mongabay.

## Quién ya trabaja en esto

| Quién | Qué hace | Relación con openMar |
|---|---|---|
| Prefectura Naval, sistema Guardacostas | Monitoreo y multas | Fuente (comunicados de multas) |
| [Skylight](https://skylight.global/news/argentina-success-story) (Allen Institute for AI) | Detección en tiempo real con IA; Prefectura lo usa desde 2025 (caso XINRUN 579) | No competir: la detección ya está |
| Global Fishing Watch | Datos públicos de AIS, radar satelital y luces nocturnas | Fuente principal de recorridos |
| Oceana | Informes de investigación | Antecedente y posible aliado |
| Milko Schvartzman, Círculo de Políticas Ambientales | Informes periódicos | Validar el proyecto con él antes de avanzar |

Argentina no publica los datos VMS de su flota. Perú lo hace desde 2018 y Chile
también, a través de Global Fishing Watch
([Oceana](https://usa.oceana.org/press-releases/chile-publish-vessel-tracking-data-through-global-fishing-watch/)).

## Registro de Flota Pesquera (lanzado el 2 de noviembre de 2026)

El Círculo de Políticas Ambientales y Sin Azul No Hay Verde publicaron
[registroflotapesquera.org](https://registroflotapesquera.org): 520 buques con
matrícula, arte de pesca, armador (titular del permiso), permiso, autorización,
sanciones y CITC, armado con pedidos de acceso a la información pública
([El Sureño](https://www.surenio.com.ar/publican-la-base-de-datos-de-barcos-que-operan-en-el-mar-argentino/)).
Ellos mismos aclaran que autorizaciones y sanciones están incompletas.

**No incluye:** recorridos AIS, mareas, observadores ni dueños reales (socios de
las empresas armadoras).

En Diputados hay un proyecto de Maximiliano Ferraro (junio de 2026) para que el
Registro de la Pesca sea público, digital y abierto, incluida la composición
societaria ([Revista Puerto](https://revistapuerto.com.ar/2026/06/proyecto-de-ley-para-hacer-publicos-todos-los-datos-de-la-pesca-argentina/)).

**Consecuencia para openMar:** la parte de "registro" ya la cubre la sociedad
civil. openMar no la duplica: la usa como fuente y le suma la capa de
**comportamiento** (AIS, mareas, observadores, cruces). El CPA pasa de "validar
con ellos" a socio natural.

## El hueco

Nadie cruza, barco por barco, el registro (armador, permisos, sanciones) con lo que
el barco hace en el mar (recorridos, apagones, mareas, observadores), ni lo publica
de forma sostenida. Tampoco nadie publica los dueños reales detrás de las empresas
armadoras. Eso es openMar.

## Riesgos

- Apunta a empresas reales: cada dato tiene que ser impecable y con fuente.
  Asesoramiento legal desde el principio.
- El dueño real de las empresas puede ser difícil de conseguir.
- No duplicar el trabajo de Schvartzman ni de Oceana: ser su infraestructura.
