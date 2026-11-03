# openMar — Análisis con el marco universal

openMar es un observatorio pesquero independiente del Mar Argentino. Junta datos
públicos que hoy están desparramados (recorridos satelitales, permisos, dueños de
empresas, cobertura de observadores y sanciones), los cruza barco por barco y
publica una ficha por buque, alertas de incumplimiento, un mapa e informes, cada
dato con su fuente. Es un proyecto **multicapa**: una canalización de datos (ETL)
alimenta una capa de extracción con IA y una API, que a su vez sirven a un portal
web público. Este análisis toma como insumo `README.md` y `docs/`.

```yaml
project:
  name: "openMar"
  type: "Data Pipeline / ETL (multicapa)"
  layers:
    - name: "Ingesta y canalización de datos"
      type: "Data Pipeline / ETL"
    - name: "Extracción de documentos con IA"
      type: "Machine Learning (inferencia con LLM, sin entrenamiento propio)"
    - name: "API del observatorio"
      type: "REST API"
    - name: "Portal público (fichas, mapa, informes)"
      type: "Web App"

dimensions:
  inputs:
    - category: "Recorridos y actividad de buques"
      items:
        - "API de Global Fishing Watch: posiciones AIS, eventos de pesca, apagones (gaps), encuentros entre buques, entradas a zonas"
        - "Token gratuito de GFW para uso no comercial (secreto en .env)"
    - category: "Documentos oficiales"
      items:
        - "Actas del Consejo Federal Pesquero en PDF (permisos, cuotas, sanciones)"
        - "Boletín Oficial: resoluciones de pesca y sanciones"
        - "Informes del INIDEP en PDF: cobertura de observadores por buque y marea, informes de pesquería"
        - "Comunicados de Prefectura Naval sobre multas e interceptaciones"
    - category: "Registros de identidad y propiedad"
      items:
        - "Lista de buques habilitados (nombre, matrícula, MMSI, IMO)"
        - "Registros de la OMI: número IMO, bandera, dueño registrado"
        - "Registros societarios (IGJ y provinciales): socios y dueños de las empresas"
    - category: "Geografía de referencia"
      items:
        - "Línea de las 200 millas (límite de la ZEE)"
        - "Zonas vedadas y áreas marinas protegidas"
        - "Puertos (Mar del Plata, Puerto Madryn, Montevideo, etc.)"
    - category: "Disparadores"
      items:
        - "Ejecución programada de cada recolector (diaria/semanal según fuente)"
        - "Carga manual de una fuente puntual (nota periodística, informe de ONG)"

  processes:
    - category: "Ingesta"
      items:
        - "Recolector por fuente que guarda el dato crudo sin modificar, con URL y fecha de descarga (.meta.json)"
        - "Descarga incremental desde la API de GFW por buque y período"
        - "Detección de documentos nuevos en el Boletín Oficial y en las actas del CFP"
    - category: "Extracción con IA"
      items:
        - "Extracción estructurada de permisos, cuotas, sanciones y coberturas desde PDF con un modelo de lenguaje"
        - "Registro de la página y el fragmento de origen de cada valor extraído"
        - "Validación de esquema y puntaje de confianza; lo dudoso va a revisión humana"
    - category: "Resolución de entidades"
      items:
        - "Unificación de un mismo buque entre fuentes (IMO, MMSI, matrícula, nombre con variantes)"
        - "Unificación de empresas y vínculo buque–empresa–socios"
        - "Historial de cambios de nombre, bandera y dueño"
    - category: "Análisis espacial"
      items:
        - "Cruce de recorridos con la línea de 200 millas y zonas vedadas (PostGIS)"
        - "Ubicación de apagones de AIS respecto del límite"
        - "Reconstrucción de mareas a partir de salidas y llegadas a puerto"
    - category: "Reglas y alertas"
      items:
        - "Mareas sin observador frente a la exigencia de la Disposición 204/2023"
        - "Apagones de AIS mayores a 24 horas cerca de la milla 200"
        - "Actividad de pesca dentro de zonas vedadas"
        - "Cambios de dueño o de bandera"
    - category: "Publicación"
      items:
        - "Armado de la ficha por buque con todas sus fuentes"
        - "Generación periódica de informes y del mapa"
        - "Revisión manual de una muestra contra fuentes originales antes de publicar"

  outputs:
    - category: "Productos públicos"
      items:
        - "Ficha por buque: dueño, permisos, mareas, observadores, recorridos, sanciones, alertas"
        - "Mapa del Mar Argentino con actividad por flota y alertas"
        - "Informe periódico en lenguaje simple con cifras y fuentes"
        - "Buscador por buque, empresa y matrícula"
    - category: "Datos abiertos"
      items:
        - "Descarga de datos procesados (CSV/JSON) bajo CC BY 4.0"
        - "API pública de solo lectura para periodistas e investigadores"
    - category: "Evidencia"
      items:
        - "Paquete de evidencia por caso (fuentes, capturas, fechas, huella digital) para prensa, Congreso o justicia"
    - category: "Notificaciones"
      items:
        - "Avisos de alertas nuevas a suscriptores (periodistas, aliados)"
    - category: "Metadatos"
      items:
        - "Linaje de cada dato: fuente, fecha de descarga, fragmento de origen"

  support:
    - category: "Orquestación y confiabilidad"
      items:
        - "Programador de recolectores con reintentos y cola de fallos"
        - "Reprocesamiento (backfill) de períodos pasados"
        - "Monitoreo de fuentes caídas o con cambio de formato"
    - category: "Calidad y trazabilidad"
      items:
        - "Catálogo de fuentes y linaje de datos"
        - "Revisión humana de extracciones dudosas y de una muestra por publicación"
        - "Versionado de datos procesados"
    - category: "Seguridad y acceso"
      items:
        - "Gestión de secretos (token GFW, claves del modelo de lenguaje)"
        - "Autenticación para el panel interno de revisión"
        - "Límite de solicitudes en la API pública"
    - category: "Legal y riesgo"
      items:
        - "Revisión de términos de uso de GFW para publicar datos derivados"
        - "Asesoramiento legal ante reclamos de empresas señaladas"
        - "Política de correcciones públicas y derecho a réplica"
        - "Licencias: AGPL-3.0 para código, CC BY 4.0 para datos (a confirmar)"
    - category: "Operación"
      items:
        - "Despliegue automatizado (CI/CD) y migraciones de base"
        - "Respaldo de la base y de los datos crudos"
        - "Documentación de API (OpenAPI)"

mapping_to_swebok:
  design_candidates:
    - "Modelo de datos: Empresa, Buque, Permiso, Marea, EventoAIS, Sanción, Alerta, Fuente"
    - "Esquema geográfico (PostGIS): línea de 200 millas, zonas vedadas, recorridos"
    - "Contrato de salida del extractor de PDF (campos + fuente + confianza)"
    - "Formato de la ficha por buque y del paquete de evidencia"
    - "Contrato de la API pública de solo lectura"
  construction_candidates:
    - "Recolector GFW (incremental por buque y período)"
    - "Recolectores de Boletín Oficial, actas CFP, INIDEP y Prefectura"
    - "Extractor de PDF con modelo de lenguaje y registro de origen"
    - "Resolución de entidades de buques y empresas"
    - "Análisis espacial y reconstrucción de mareas"
    - "Motor de reglas y alertas"
    - "Generador de fichas, informes y paquetes de evidencia"
    - "Portal web: buscador, ficha, mapa"
  security_candidates:
    - "Gestión de secretos (GFW, modelo de lenguaje)"
    - "Autenticación del panel de revisión"
    - "Límite de solicitudes y protección de la API pública"
  operations_candidates:
    - "Orquestación de recolectores con reintentos y backfill"
    - "Monitoreo de fuentes y alertas de cambio de formato"
    - "CI/CD, migraciones y respaldos"
    - "Catálogo de fuentes y linaje"

next_step: "Pasar este análisis a swebok-decompose para generar el desglose de trabajo"
```

## Próximo paso

Ejecutar `/blueprint-skills:swebok-decompose` con este archivo como entrada para
generar el desglose de trabajo por áreas SWEBOK. Conviene priorizar los nodos que
necesita la **etapa 0** (`docs/etapa-0-demo.md`): recolector GFW, lista de
buques, extracción de la cobertura de observadores del INIDEP, resolución de
entidades de buques y ficha por buque.
