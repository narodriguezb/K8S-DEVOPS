# API Microservice

Microservicio demo construido con **FastAPI** y desplegable con **Docker**.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida |
| GET | `/live` | Liveness probe (Kubernetes) |
| GET | `/ready` | Readiness probe (Kubernetes) |
| GET | `/docs` | Swagger UI (documentación interactiva) |

## Cómo correr

### Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
# Build
docker build -t api-microservice .

# Run
docker run -p 8000:8000 api-microservice
```

La API estará disponible en `http://localhost:8000`

## Stack

- **Python 3.12**
- **FastAPI 0.115**
- **Uvicorn 0.30**
