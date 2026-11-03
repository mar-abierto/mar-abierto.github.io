# 0012. Personas en los datos societarios

**Estado:** Propuesta · 3 de noviembre de 2026

## Contexto

Para saber quién está detrás de cada armador se van a usar el Registro Nacional de
Sociedades (CUIT, razón social, domicilio, actividad) y el Boletín Oficial nacional
y provinciales (designación de autoridades, constituciones, sociedades extranjeras
inscriptas). La IGJ no publica socios ni autoridades en forma abierta.

Las autoridades de una sociedad son personas físicas. Que su designación esté
publicada en el Boletín Oficial no hace que cualquier uso sea adecuado: la Ley
25.326 de protección de datos personales sigue aplicando, y un mapa de relaciones
puede sugerir vínculos que no existen.

## Decisión propuesta

1. El mapa de relaciones vincula **empresas con empresas**: domicilio compartido,
   autoridad compartida, matriz extranjera inscripta.
2. El nombre de una persona aparece sólo como figura en una publicación oficial, en
   el rol que esa publicación le da, con el link a la fuente y la fecha.
3. No se publican datos personales que no estén en esa publicación: DNI, domicilio
   particular, estado civil, edad.
4. No se infieren relaciones personales (familia, testaferros) ni se calcula
   ninguna puntuación sobre personas.
5. Se extiende la regla ya vigente para el INIDEP: los nombres de observadores no
   se extraen ni se publican.

## Consecuencias

- El adaptador del Boletín Oficial guarda el texto original en bronze y en silver
  sólo los campos permitidos.
- Una persona que pida una corrección tiene un canal de contacto y la respuesta
  queda registrada.
- Queda en "Propuesta" hasta revisarla con alguien con formación en protección de
  datos personales.
