# Receitas Toon - Catálogo de receitas de desenhos animados

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes&logoColor=white)

Disciplina: Tópicos Especiais em Sistemas Operacionais (Linux e Docker)

## O que é
Site de catálogo com receitas inspiradas em desenhos animados (Bob Esponja,
Os Simpsons, Scooby-Doo, Naruto, Pokémon, Tom e Jerry e Hora de Aventura).
Funcionalidades: listar, buscar por nome, filtrar por desenho, ver detalhes
(ingredientes e modo de preparo), curtir e cadastrar novas receitas.
API JSON em `/api/receitas`.

## Link de execução local
A aplicação fica disponível em:

- http://localhost:5000
- ou, se a porta 5000 estiver ocupada, http://localhost:5005

O script local detecta automaticamente uma porta disponível e informa a URL correta no terminal.

> Se a porta 5000 estiver sendo usada por outra app antiga, o projeto não sobe na mesma porta. Isso é o motivo do erro interno em algumas execuções locais.

## Arquitetura
Navegador -> Service (NodePort) -> 3 pods `receitas-web` (Flask) -> Service -> pod `postgres` (volume persistente)

## Tecnologias
Linux, Docker, Kubernetes (minikube), Python/Flask, PostgreSQL.

## Opção 1: execução local rápida
Este é o modo mais simples para ver o projeto funcionando no computador.

```bash
chmod +x run_local.sh
./run_local.sh
```

Depois abra:

```text
http://localhost:5000
```

> Esse script usa o modo local com SQLite para funcionar sem depende de Docker ou PostgreSQL no ambiente.

## Opção 2: Docker Compose
```bash
docker compose up --build
# abre em http://localhost:8080
```

## Opção 3: Kubernetes (minikube)
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

## Como testar a aplicação
```bash
curl http://localhost:5000/health
```

Você deve receber:

```text
ok
```

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
