# Analisis de vulnerabilidades

## Relacion con la rubrica

El punto 5 de la rubrica corresponde a Calidad y Seguridad. Para el subpunto de analisis de vulnerabilidades se evaluan tres evidencias:

- Riesgos identificados.
- Vulnerabilidades encontradas.
- Propuestas de mitigacion.

Este documento cubre ese subpunto mediante un analisis automatizado ejecutable en GitHub Actions y una lectura tecnica de los riesgos principales del proyecto Tambo+.

## Enfoque segun el modelo Agile

El proyecto utiliza un enfoque Agile, por lo que la seguridad se integra como una actividad continua y no como una revision final aislada. El analisis se ejecuta en cada pull request hacia `main`, en cada push a la rama principal o de integracion y manualmente desde la pestana Actions de GitHub.

Esto permite que cada incremento del sprint sea revisado antes de integrarse al producto final.

## Tecnicas aplicadas

| Tecnica | Aplicacion en el proyecto | Justificacion |
| --- | --- | --- |
| Pruebas basadas en estructura / caja blanca | Analisis estatico del codigo con CodeQL y Bandit | Se revisa el funcionamiento interno del backend Flask, controladores, servicios y repositorios. |
| Pruebas de seguridad automatizadas | Ejecucion de scanners en GitHub Actions | La guia indica que algunas pruebas de seguridad pueden automatizarse para deteccion temprana de vulnerabilidades comunes. |
| Pruebas basadas en experiencia / ataques | Busqueda de secretos, configuraciones inseguras y superficies administrativas | Permite detectar patrones peligrosos como credenciales expuestas, endpoints administrativos sin control y configuraciones de desarrollo. |
| Gestion de riesgos | Priorizacion por impacto y probabilidad | La rubrica solicita riesgos identificados y mitigaciones, no solo ejecucion de herramientas. |

## Alcance del analisis

El workflow `.github/workflows/security-analysis.yml` revisa:

- Backend Python/Flask en `python/`.
- Dependencias declaradas en `python/requirements.txt`.
- Frontend HTML/JavaScript en `frontend/`, principalmente mediante CodeQL.
- Posibles secretos accidentales en el repositorio.
- Configuraciones que puedan afectar seguridad operativa.

## Workflow en GitHub Actions

Archivo agregado:

```text
.github/workflows/security-analysis.yml
```

El workflow se ejecuta en:

- `pull_request` hacia `main`.
- `push` hacia `main`.
- `push` hacia `codex/unificar-dashboard-recomendaciones`.
- Ejecucion manual con `workflow_dispatch`.
- Ejecucion programada cada lunes.

## Herramientas utilizadas

| Herramienta | Tipo de analisis | Resultado esperado |
| --- | --- | --- |
| CodeQL | SAST para Python y JavaScript | Hallazgos en la pestana Security / Code scanning de GitHub. |
| Bandit | SAST especifico para Python | Reportes `bandit.json` y `bandit.txt`. |
| pip-audit | Analisis de vulnerabilidades conocidas en dependencias Python | Reporte `pip-audit.json`. |
| detect-secrets | Deteccion de secretos accidentales | Reporte `detect-secrets.json`. |
| security_summary.py | Consolidacion de resultados | Reporte `security-summary.md`. |

Los reportes se publican como artifact llamado:

```text
security-analysis-reports
```

## Riesgos identificados

| ID | Riesgo | Evidencia tecnica | Impacto | Mitigacion propuesta |
| --- | --- | --- | --- | --- |
| R-01 | Exposicion de secretos o llaves de Supabase | El backend depende de `SUPABASE_SECRET_KEY` o `SUPABASE_SERVICE_ROLE_KEY` en variables de entorno. | Acceso no autorizado a datos si una llave se filtra. | Usar GitHub Secrets, no subir `.env`, rotar llaves expuestas y ejecutar `detect-secrets` en cada PR. |
| R-02 | Dependencias con vulnerabilidades conocidas | Dependencias Python declaradas en `python/requirements.txt`. | Vulnerabilidades heredadas por librerias externas. | Ejecutar `pip-audit`, actualizar paquetes vulnerables y fijar versiones reproducibles. |
| R-03 | Codigo Python con patrones inseguros | Backend Flask, controladores y servicios analizados por Bandit y CodeQL. | Riesgo de errores de configuracion, manejo inseguro de datos o uso peligroso de librerias. | Revisar hallazgos Bandit/CodeQL y corregir segun severidad. |
| R-04 | Dashboard administrativo expuesto sin autenticacion fuerte | `frontend/dashboard.html` y `/api/admin/dashboard`. | Exposicion de metricas administrativas si el servidor se publica sin control de acceso. | Agregar autenticacion/autorizacion para rutas `/api/admin/*` antes de despliegue real. |
| R-05 | Configuracion de desarrollo en produccion | `app.run(debug=True, host="0.0.0.0", port=port)` en `python/app.py`. | Debug activo puede exponer informacion sensible en ambientes productivos. | Controlar debug con variable de entorno y usar `debug=False` por defecto. |
| R-06 | CORS permisivo | `CORS(app)` en `python/app.py`. | Sitios externos podrian consumir endpoints si no se restringe origen. | Restringir origenes permitidos por variable de entorno. |
| R-07 | Manipulacion de HTML en frontend | Uso de `innerHTML` en vistas del chat y dashboard. | Riesgo XSS si se renderiza contenido no saneado. | Usar `textContent` cuando sea posible y mantener funciones de escape para datos dinamicos. |
| R-08 | Autenticacion de usuario debil para login academico | Login usa `user_code` como password. | Acceso no robusto si se usa fuera del contexto academico/demo. | Reemplazar por autenticacion real con hash de contrasenas o proveedor externo. |

## Vulnerabilidades encontradas

Las vulnerabilidades se consideran encontradas cuando aparecen en alguno de los reportes del workflow:

- `bandit.json`: hallazgos por archivo, linea, severidad y confianza.
- `pip-audit.json`: CVE/GHSA o vulnerabilidades conocidas por dependencia.
- `detect-secrets.json`: posibles secretos en archivos del repositorio.
- CodeQL: alertas en GitHub Code Scanning.

El archivo `security-summary.md` resume los conteos principales para colocarlos como evidencia documental.

### Resultado de validacion local

Antes de subir el workflow se ejecuto una validacion local con las mismas herramientas principales. El resultado confirma que el analisis produce evidencia util para la rubrica:

| Herramienta | Hallazgos |
| --- | --- |
| Bandit | 4 hallazgos: 1 alto, 1 medio y 2 bajos. |
| pip-audit | 6 vulnerabilidades conocidas en 3 dependencias. |
| detect-secrets | 0 posibles secretos detectados. |

Hallazgos Bandit identificados:

| ID | Archivo | Severidad | Hallazgo |
| --- | --- | --- | --- |
| B201 | `python/app.py:62` | Alta | Flask se ejecuta con `debug=True`, lo que no debe usarse en produccion. |
| B104 | `python/app.py:62` | Media | El servidor se enlaza a `0.0.0.0`, exponiendo el servicio en todas las interfaces. |
| B110 | `python/services/chatbot_service.py:198` | Baja | Excepcion capturada con `pass`, lo que puede ocultar errores reales. |
| B110 | `python/services/nlp_service.py:66` | Baja | Excepcion capturada con `pass`, lo que puede ocultar errores reales. |

Vulnerabilidades de dependencias detectadas por pip-audit:

| Dependencia | Version actual | Vulnerabilidades | Version sugerida |
| --- | --- | ---: | --- |
| `flask` | 3.1.0 | 2 | 3.1.3 |
| `flask-cors` | 5.0.0 | 3 | 6.0.0 |
| `python-dotenv` | 1.1.0 | 1 | 1.2.2 |

## Propuestas de mitigacion

| Prioridad | Mitigacion | Responsable sugerido | Estado |
| --- | --- | --- | --- |
| Alta | Mover llaves reales a GitHub Secrets y rotar cualquier llave compartida fuera del repositorio. | Backend / DevOps | Pendiente |
| Alta | Proteger `/api/admin/*` con autenticacion y autorizacion. | Backend | Pendiente |
| Alta | Desactivar debug por defecto y usar `FLASK_DEBUG` solo localmente. | Backend | Identificado por Bandit |
| Media | Restringir CORS a origenes definidos en variable de entorno. | Backend | Pendiente |
| Media | Revisar y corregir hallazgos Bandit/CodeQL de severidad alta o media. | Backend / Frontend | Pendiente |
| Media | Actualizar `flask`, `flask-cors` y `python-dotenv` segun versiones sugeridas por pip-audit. | Backend | Identificado por pip-audit |
| Media | Cambiar `innerHTML` por renderizado seguro donde aplique. | Frontend | Pendiente |
| Baja | Documentar excepciones aceptadas cuando un hallazgo sea falso positivo. | Equipo QA | Pendiente |

## Evidencia para entregar

Para sustentar el analisis ante el docente se recomienda capturar:

1. Pantalla del pull request mostrando el check `Security Analysis`.
2. Pantalla del workflow ejecutado en GitHub Actions.
3. Artifact `security-analysis-reports`.
4. Archivo `security-summary.md`.
5. Captura de Code Scanning si GitHub habilita los resultados de CodeQL.

Con esto se cubren los tres puntos de la rubrica: riesgos identificados, vulnerabilidades encontradas y propuestas de mitigacion.
