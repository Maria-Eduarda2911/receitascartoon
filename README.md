# Receitas Toon - Catálogo de receitas de desenhos animados

Disciplina: Tópicos Especiais em Sistemas Operacionais (Linux e Docker)

## O que é
Site de catálogo com receitas inspiradas em desenhos animados (Bob Esponja,
Os Simpsons, Scooby-Doo, Naruto, Pokémon, Tom e Jerry e Hora de Aventura).
Funcionalidades: listar, buscar por nome, filtrar por desenho, ver detalhes
(ingredientes e modo de preparo), curtir e cadastrar novas receitas.
API JSON em `/api/receitas`.

## Arquitetura
Navegador -> Service (NodePort) -> 3 pods `receitas-web` (Flask) -> Service -> pod `postgres` (volume persistente)

## Tecnologias
Linux, Docker, Kubernetes (minikube), Python/Flask, PostgreSQL.

## Opção 1: só Docker
```bash
docker compose up --build
# abra http://localhost:8080
```

## Opção 2: Kubernetes (minikube)
```bash
minikube start --driver=docker

# constroi a imagem dentro do Docker do minikube
eval $(minikube docker-env)
docker build -t receitas-toon:1.0 app/

kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/app.yaml
kubectl get pods -w

minikube service receitas-web --url
```

## Recursos do Kubernetes usados
- Deployment (3 réplicas do site + 1 do banco)
- Service (balanceamento de carga entre os pods)
- ConfigMap (configurações) e Secret (usuário e senha do banco)
- PersistentVolumeClaim (dados do banco não se perdem)
- Probes de saúde (readiness e liveness)
- Limites de CPU e memória por container

## Demonstração
```bash
# 1. balanceamento: recarregue a página e veja o nome do pod mudar no rodapé

# 2. auto-recuperação: apague um pod do site e veja o Kubernetes recriar
kubectl get pods
kubectl delete pod <nome-de-um-pod-receitas-web>
kubectl get pods -w

# 3. escalar
kubectl scale deployment receitas-web --replicas=5

# 4. persistência: cadastre uma receita, apague o banco e veja que ela continua
kubectl delete pod -l app=postgres
kubectl get pods -w

# 5. atualização gradual
kubectl rollout restart deployment/receitas-web
```
