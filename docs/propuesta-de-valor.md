# Propuesta de valor

> Borrador del 3 de noviembre de 2026. Ordena qué hace openMar, qué no hace y por
> qué. Sirve para decidir qué sumar al proyecto y qué dejar afuera.

## En una frase

**openMar responde preguntas sobre el Mar Argentino que el Estado tiene los datos
para responder y no publica.**

## Lo que ya existe y no repetimos

| Qué | Quién ya lo hace |
|---|---|
| Mostrar la flota extranjera en la milla 201 | Global Fishing Watch, Oceana, Prefectura, la prensa cada temporada |
| Detectar barcos en el mar | Prefectura, Skylight, Global Fishing Watch |
| Armadores, permisos y sanciones por buque | Registro de Flota Pesquera (CPA y Sin Azul No Hay Verde) |

Si openMar compite en "ver barcos", pierde: otros lo hacen con más recursos. Estas
fuentes se usan, se citan y no se duplican.

## Lo que nadie hace: cruzar

Cada fuente está publicada por separado. Nadie las junta:

- INIDEP: mareas por buque y si hubo observador a bordo.
- Global Fishing Watch: recorridos, eventos de pesca, apagones de AIS, visitas a puerto.
- Registro de Flota Pesquera: matrícula, armador, sanciones.
- Consejo Federal Pesquero: permisos y cuotas.
- Boletín Oficial y Registro Nacional de Sociedades: empresas, domicilios, autoridades.

Un dato como "este barco apagó el AIS 13 veces en mareas sin observador y nunca
llevó uno en cuatro años" no sale de ninguna fuente sola. Ese es el aporte.

## Las preguntas

1. ¿Qué buques casi nunca llevan observador, y eso cambia con los años?
2. ¿Qué pasa con el AIS cuando no hay nadie mirando a bordo?
3. ¿Cuánto pesca cada empresa contra la cuota que tiene asignada?
4. ¿Las sanciones se pagan, o el barco sigue pescando igual?
5. ¿Quién está detrás de cada armador?
6. ¿Dónde descarga cada buque: en puertos argentinos o en el exterior?

La bandera del proyecto son la 1 y la 2, **el control ausente a bordo**: es lo más
avanzado, lo que nadie más mide y lo que conecta con la historia de Enrique
Piñeyro de denunciar controles que el Estado no hace.

## Conductas, no pasaportes

Ser "argenchino" (buque con bandera argentina y capital extranjero) **no es una
infracción**: el capital extranjero en la pesca es legal. Si el mensaje fuera "son
chinos", la respuesta obvia es "damos trabajo a los argentinos", y el proyecto
quedaría como xenófobo. Además, nuestros propios datos no lo sostienen: entre los
8 buques con señales repetidas de 2025 hay empresas marplatenses tradicionales.

Por eso (ADR 0010):

- **Las mismas reglas para todos:** observador, AIS, sanciones, cuota, descarga.
- **El origen del capital nunca entra en el semáforo.**
- **El dueño es un dato de transparencia** en la ficha del buque, no una señal.

Dónde sí importa quién es el dueño:

- **Transparencia:** quién decide y quién se queda con la renta de un recurso público.
- **Doble acceso al mismo stock:** si un mismo grupo pesca adentro con permiso
  argentino y afuera, en la milla 201, sin ningún control. Es una pregunta de
  política pesquera, no una acusación.
- **Concentración:** si existen topes de cuota por empresa y un mismo dueño los
  supera a través de varias sociedades. *Hay que confirmar el marco legal antes
  de afirmar nada.*

### "Damos trabajo a los argentinos" se mide

No se discute: se convierte en indicador, igual para todas las empresas.

| Pregunta | Dato | Estado |
|---|---|---|
| ¿Dónde descargan? | Visitas a puerto de Global Fishing Watch (por ejemplo, Montevideo frente a Puerto Madryn) | Disponible en la API que ya usamos |
| ¿Cuánto se procesa en tierra? | Desembarques y exportaciones por especie y producto | Datos públicos, a buscar |
| ¿Tripulación argentina? | Rol de tripulación | No es público; los gremios (SOMU) podrían aportar |

## El sitio: cuatro piezas

De lo general a lo particular:

1. **Portada infográfica (el relato).** Cuatro o cinco números que cuentan la
   historia mientras se baja: "354 mareas en 2025 → 23 con observador → 52
   apagones en mareas sin nadie mirando → 8 buques con señales repetidas". Cada
   número con su fuente y con lo que no sabemos. Es lo que se comparte.
2. **Tablero de control.** Las preguntas de arriba como indicadores con su
   evolución en el tiempo. Para periodistas, legisladores y el CFP.
3. **Mapa.** El que ya existe, como herramienta para explorar.
4. **Ficha por buque.** Una página por barco con todo cruzado. Es lo que se
   linkea desde una nota periodística.

## Empresas y dueños: de dónde sale el dato

| Fuente | Qué trae | Qué no trae |
|---|---|---|
| Registro Nacional de Sociedades ([datos.jus.gob.ar](https://datos.jus.gob.ar/dataset/registro-nacional-de-sociedades)) | CUIT, razón social, domicilio legal y fiscal, actividad. Abierto. | Socios y autoridades |
| Boletín Oficial, segunda sección (nacional y provinciales) | Designación de autoridades, constituciones, sociedades extranjeras inscriptas | Composición accionaria completa |
| IGJ | Socios y autoridades de sociedades de CABA | Acceso abierto: requiere informe pago y a veces interés legítimo |

Con eso se arma un **mapa de relaciones entre empresas**: domicilio compartido,
autoridad compartida, matriz extranjera inscripta. Las personas físicas se tratan
según el ADR 0012.

## Sumar y no sumar

| Idea | Decisión | Por qué |
|---|---|---|
| Portada infográfica con los datos actuales | Sumar primero | No necesita datos nuevos; es lo que se muestra |
| Visitas a puerto | Sumar | Misma API; responde a "damos trabajo" |
| Flota extranjera en la milla 201 | Sumar sólo en relación | Verla sola ya existe; vale si se vincula a grupos con buques adentro (ADR 0011) |
| Incursiones en la ZEE | Sumar con revisión manual | Exige cálculo contra la línea real y una decisión sobre Malvinas (ADR 0011) |
| Actualización diaria | Sumar | Gratis; GFW publica con unos 4 días de demora |
| Luces nocturnas (VIIRS) | Más adelante | Muestra barcos que pescan sin AIS; es lo más nuevo y lo más trabajoso |
| Tiempo real | No | Es pago y no se puede redistribuir (ADR 0004) |
| Nacionalidad del capital como señal | No | ADR 0010 |
