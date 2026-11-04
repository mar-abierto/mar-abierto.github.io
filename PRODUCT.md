# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Público general argentino**, sin formación técnica en pesca ni en datos. Llega por un link en una nota o en redes y tiene que entender en un minuto qué pasa.
- **Periodistas**, que necesitan una cifra con su fuente y una ficha por barco para linkear desde una nota.
- **Enrique Piñeyro**, posible padrino del proyecto. Denunció la flota extranjera en la milla 201 (sobrevuelo de 2021) y los controles que el Estado no hace. El sitio tiene que conectar con esa historia y mostrar algo que él no tenía.

## Product Purpose

openMar es un observatorio independiente de la flota que pesca calamar en el mar argentino. Cruza datos públicos dispersos (mareas y observadores del INIDEP, señales de posición de Global Fishing Watch, Registro de Flota Pesquera) y responde preguntas que el Estado tiene los datos para responder y no publica.

Hipótesis central: afuera de la milla 200 nadie puede controlar; adentro el Estado sí puede, y casi no controla (1 de cada 15 viajes con observador en 2025).

Éxito: que alguien sin conocimientos previos entienda la hipótesis desde la portada, y que un periodista pueda citar una cifra o un barco con su fuente.

## Positioning

La flota extranjera en la milla 201 ya la muestran Global Fishing Watch, Oceana y la prensa. openMar mira lo que nadie mide: el control a bordo de la flota con bandera argentina, barco por barco, con las mismas reglas para todos.

## Operating Context

Sitio estático, informativo, casi periodístico. Cuatro superficies:
- **Relato** (`index.html`): portada que se lee de arriba abajo como una nota de datos. Modo Read.
- **Tablero** (`tablero.html`): indicadores de la flota y las reglas.
- **Fichas** (`buque.html`): una página por barco, linkeable desde una nota.
- **Mapa** (`mapa.html`): exploración.

## Capabilities and Constraints

- HTML, CSS y JS sin build; CSP `script-src 'self'`. MapLibre en el mapa.
- Ninguna cifra escrita en el HTML: todo sale de `data/resumen.json` y `data/fichas.json`.
- Español rioplatense. Lenguaje llano en el cuerpo; siglas (INIDEP, AIS, VMS) sólo en fuentes y glosario. "Viaje" en vez de "marea", "corte de señal" en vez de "apagón de AIS".
- Borrador privado hasta revisión (`noindex`, badge de borrador).

## Brand Commitments

- Tono: **periodismo de datos sobrio** (referencias: La Nación Data, ProPublica, The Pudding). Creíble antes que llamativo.
- **Señales, no acusaciones** (ADR 0008): un corte de señal no es una infracción.
- **Conductas, no pasaportes** (ADR 0010): el origen del capital nunca es una señal.
- Anti-referencias: dashboard de software (tarjetas, números gigantes, neón sobre fondo oscuro); estética conspiranoica o militante (rojo alarma, tono de panfleto); plantilla hecha con IA (serif en cursiva, eyebrows en mayúsculas, la misma animación en todo).

## Evidence on Hand

Datos reales de la temporada 2025 y la serie 2021–2024 en `site/data/`. Fuentes citadas en `docs/contexto.md`. No hay fotos propias ni testimonios: no inventarlos.

## Product Principles

1. **La pregunta primero.** Cada página dice qué pregunta contesta antes de mostrar un número.
2. **Cada cifra con su fuente** y con lo que no sabemos al lado.
3. **Las mismas reglas para todos los barcos**, publicadas.
4. **Llano antes que técnico**: si un lector común no lo entiende, está mal escrito.

## Accessibility & Inclusion

WCAG 2.2 AA. Contraste real en el cuerpo, gráficos con texto alternativo, colores que no sean la única forma de distinguir categorías, `prefers-reduced-motion` respetado. Mucha lectura desde celular.
