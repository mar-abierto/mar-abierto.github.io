# 0004. No redistribuir datos de terceros

**Estado:** Aceptada · 3 de noviembre de 2026

## Contexto

openMar usa tres fuentes con reglas distintas:

| Fuente | Reglas |
|---|---|
| Global Fishing Watch | API con token personal, uso no comercial, términos de uso propios |
| INIDEP | Informes públicos del Estado; incluyen nombres de observadores |
| Registro de Flota Pesquera (CPA y SANHV) | Dice "formato abierto" pero no publica licencia |

Subir esos datos al repositorio implicaría redistribuirlos bajo nuestra licencia,
algo que no nos corresponde.

## Decisión

- El repositorio trae **código que descarga** los datos, no los datos. `data/`
  está en `.gitignore`.
- Cada usuario descarga con sus propias credenciales (por ejemplo, su token de GFW
  en `.env`).
- Todo lo descargado se guarda con un `.meta.json` que registra la URL de origen y
  la fecha.
- Los nombres de personas que aparecen en los informes (observadores) no se
  extraen ni se publican.
- Lo que sí se publica (el mapa, los informes) son **resultados derivados**, con
  la fuente de cada dato citada.

**Excepción: `site/data/`.** Los GeoJSON del mapa son resultados derivados (lo
que se publica) y se versionan para poder desplegar el sitio desde el repositorio.
No contienen datos crudos de ninguna fuente ni nombres de personas.

## Consecuencias

- No hay conflictos de licencia en el repositorio.
- Reproducir los resultados requiere correr los recolectores: es más lento que
  bajar un CSV, pero cada número es verificable contra su fuente.
- Antes de publicar resultados en forma masiva hay que confirmar los términos de
  GFW y pedir permiso al CPA para mostrar datos de su registro.
