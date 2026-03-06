# k8s_server

Repositorio de infraestructura K8s para el proyecto API Microservice. Contiene los manifests base y el Helm chart usado por ArgoCD para gestionar los ambientes `dev` y `prod`.

## Estructura

```
k8s_server/
├── k8s/
│   ├── base/                        # Manifests planos (referencia)
│   │   └── api-microservice/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── ingress.yaml
│   │       └── hpa.yaml
│   └── charts/
│       └── api-microservice/        # Helm chart principal
│           ├── Chart.yaml
│           ├── values.yaml          # Defaults base
│           ├── values.dev.yaml      # Overrides dev (actualizado por CI)
│           ├── values.prod.yaml     # Overrides prod (actualizado por CI)
│           └── templates/
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── ingress.yaml
│               └── hpa.yaml
```

## Ambientes

| Ambiente | Namespace | Branch | Ingress path |
|----------|-----------|--------|--------------|
| dev | `api-dev` | `develop` | `/dev/users` |
| prod | `api-prod` | `main` | `/prod/users` |

## ArgoCD Applications

| App | Branch | Values file | Namespace |
|-----|--------|-------------|-----------|
| `api-dev` | `develop` | `values.dev.yaml` | `api-dev` |
| `api-prod` | `main` | `values.prod.yaml` | `api-prod` |

ArgoCD monitorea el repo y sincroniza automáticamente cuando detecta cambios en los values files (actualizados por GitHub Actions al hacer push).

## Flujo GitOps

```
Push a develop/main
    ↓
GitHub Actions build imagen y actualiza values.<env>.yaml
    ↓
ArgoCD detecta cambio (polling cada ~3 min)
    ↓
ArgoCD sincroniza → K8s rolling update
```

## Instalar manualmente con Helm

```bash
# Dev
kubectl create namespace api-dev
helm install api-dev ./k8s/charts/api-microservice \
  -n api-dev \
  -f k8s/charts/api-microservice/values.dev.yaml

# Prod
kubectl create namespace api-prod
helm install api-prod ./k8s/charts/api-microservice \
  -n api-prod \
  -f k8s/charts/api-microservice/values.prod.yaml
```

## Comandos útiles

```bash
# Ver estado de los ambientes
kubectl get all -n api-dev
kubectl get all -n api-prod

# Ver HPA
kubectl get hpa -n api-dev
kubectl get hpa -n api-prod

# Ver logs
kubectl logs -l app=api-microservice -n api-dev
kubectl logs -l app=api-microservice -n api-prod

# Rollback con Helm
helm rollback api-dev -n api-dev
```
