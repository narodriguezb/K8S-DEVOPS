# API Microservice

Microservicio demo construido con **FastAPI** y desplegable con **Docker**. Soporta múltiples ambientes (`dev`, `prod`) mediante variables de entorno, con imágenes generadas automáticamente por GitHub Actions.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida + ambiente activo |
| GET | `/live` | Liveness probe (Kubernetes) |
| GET | `/ready` | Readiness probe (Kubernetes) |
| GET | `/docs` | Swagger UI |

Todos los endpoints retornan el campo `env` indicando el ambiente activo:

```json
{ "status": "ready", "env": "dev", "timestamp": "..." }
```

## Ambientes

La variable de entorno `APP_ENV` controla el ambiente. Se inyecta en el build via `ARG`:

| Ambiente | Branch | Tag Docker |
|----------|--------|------------|
| dev | `develop` | `nestorx211/api-microservice:dev-<sha>` |
| prod | `main` | `nestorx211/api-microservice:prod-<sha>` |

## Correr local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
# Build para dev
docker build --build-arg APP_ENV=dev -t api-microservice:dev .

# Build para prod
docker build --build-arg APP_ENV=prod -t api-microservice:prod .

# Run
docker run -p 8000:8000 api-microservice:dev
```

## CI/CD

| Evento | Acción |
|--------|--------|
| Push a `develop` | Build imagen `:dev-<sha>` → actualiza `values.dev.yaml` |
| Push a `main` | Build imagen `:prod-<sha>` → actualiza `values.prod.yaml` |

ArgoCD detecta el cambio en los values y sincroniza automáticamente.

## Stack

- **Python 3.12**
- **FastAPI 0.115**
- **Uvicorn 0.30**
