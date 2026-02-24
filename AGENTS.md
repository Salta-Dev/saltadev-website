# AGENTS.md

Guía de prácticas para agentes de IA que trabajan en este codebase.

## Comandos de Ejecución

Usar siempre `uv run` para ejecutar cualquier comando Python:

```bash
# Ejecutar servidor de desarrollo
uv run python saltadev/manage.py runserver

# Ejecutar tests
uv run pytest

# Ejecutar un script específico
uv run python script.py
```

## Pre-commit (Obligatorio Antes de Commitear)

**SIEMPRE** ejecutar pre-commit antes de hacer cualquier commit:

```bash
# Verificar todos los archivos
uv run pre-commit run --all-files

# Verificar solo archivos staged
uv run pre-commit run
```

### Hooks Configurados
- **ruff**: Linting + autofix + formato
- **biome**: Formato JS/CSS/HTML
- **bandit**: Análisis de seguridad Python
- **detect-secrets**: Detección de secretos
- **mypy**: Type checking

Si pre-commit falla, **corregir todos los errores** antes de commitear.

## Análisis de Seguridad con Docker

Antes de commitear cambios significativos, ejecutar SonarQube y Semgrep:

### Levantar SonarQube
```bash
# Iniciar SonarQube (primera vez toma ~2 min)
docker compose -f docker/docker-compose.sonarqube.yml up -d sonarqube

# Esperar a que esté listo en http://localhost:9000
# Credenciales por defecto: admin/admin
```

### Ejecutar Análisis
```bash
# SonarQube scanner
docker compose -f docker/docker-compose.sonarqube.yml --profile scan run --rm sonar-scanner

# Semgrep (genera semgrep-report.json)
docker compose -f docker/docker-compose.sonarqube.yml --profile scan run --rm semgrep
```

### Si Hay Findings
1. Revisar el reporte de Semgrep (`semgrep-report.json`)
2. Revisar dashboard de SonarQube (`http://localhost:9000`)
3. **Corregir todos los issues de seguridad** antes de commitear
4. Re-ejecutar el análisis para confirmar correcciones

## Actualización de Documentación

Si los cambios afectan:
- Nuevas dependencias → Actualizar sección de instalación en README.md
- Nuevos comandos → Actualizar sección de desarrollo en README.md
- Cambios en arquitectura → Actualizar diagramas/estructura en README.md
- Nuevas variables de entorno → Actualizar sección de configuración en README.md
- Cambios en Docker → Actualizar sección de Docker en README.md

## Flujo de Trabajo Completo

1. **Hacer cambios** en el código
2. **Ejecutar tests**: `uv run pytest`
3. **Ejecutar pre-commit**: `uv run pre-commit run --all-files`
4. **Corregir** cualquier error reportado
5. **Si cambios significativos**: Ejecutar SonarQube + Semgrep
6. **Corregir** cualquier issue de seguridad
7. **Actualizar README.md** si es necesario
8. **Commitear** solo cuando todo pase

## Tests

```bash
# Todos los tests
uv run pytest

# Tests específicos
uv run pytest tests/test_users.py -v

# Con coverage
uv run pytest --cov=saltadev --cov-report=term-missing
```

## Linting Manual (si necesario)

```bash
# Solo verificar
uv run ruff check saltadev

# Verificar y corregir automáticamente
uv run ruff check saltadev --fix

# Formato
uv run ruff format saltadev

# Type checking
uv run mypy saltadev

# Seguridad
uv run bandit -r saltadev -x "**/tests/**"
```
