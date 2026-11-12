# Receitas Toon

Catálogo de receitas de pratos que aparecem em desenhos animados. Cada receita
mostra a **cena do episódio** em que o prato aparece, com ingredientes e modo de
preparo.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-minikube-326CE5?logo=kubernetes&logoColor=white)

Projeto da disciplina **Tópicos Especiais em Sistemas Operacionais (Linux e Docker)**.

## O que tem no catálogo

| Receita | Desenho | Onde aparece |
|---|---|---|
| Hambúrguer de Siri | Bob Esponja | T1E1 "Help Wanted" |
| Cachorro-quente Krusty | Os Simpsons | T28 "Fatzcarraldo" |
| Donut Rosa do Homer | Os Simpsons | T7E6 "Treehouse of Horror VI" |
| Ramen Ichiraku Caseiro | Naruto | Ep. 1 "Enter: Naruto Uzumaki!" |
| Panqueca de Bacon do Finn e Jake | Hora de Aventura | T4E16 "Burning Low" |

## Funcionalidades

- Listar receitas, buscar por nome e filtrar por desenho
- Página da receita com a cena do episódio, ingredientes (dá para marcar o que já separou) e passo a passo
- Curtir receitas e cadastrar novas
- API JSON em `/api/receitas`
- Rodapé mostra o pod que atendeu a requisição (útil para ver o balanceamento no Kubernetes)

## Como rodar

### Local (mais simples)

Usa SQLite, então não precisa de Docker nem PostgreSQL.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x run_local.sh
./run_local.sh
```

O script sempre encerra processos antigos do projeto antes de iniciar um novo, para evitar conflito de porta. Ele tenta usar a porta 5000 e, se ela estiver ocupada, cai para a 5005. A URL correta aparece no terminal.

> Se o app já estiver aberto em outra aba ou terminal, o comando reaproveita a mesma máquina sem deixar um processo antigo preso na porta.

### Docker Compose

```bash
docker compose up --build
# abre em http://localhost:8080
```

### Kubernetes (minikube)

```bash
minikube start --driver=docker

# constrói a imagem dentro do Docker do minikube
eval $(minikube docker-env)
docker build -t receitas-toon:1.0 app/

kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/app.yaml
kubectl get pods -w

minikube service receitas-web --url
```

## Imagens das cenas

O site não traz imagens prontas: cada receita usa um **print do episódio** que
você salva em `app/static/images/cenas/`. O nome do arquivo é o título da
receita sem acentos, em minúsculas e com hífens:

| Receita | Arquivo | O que capturar |
|---|---|---|
| Hambúrguer de Siri | `hamburguer-de-siri.jpg` | Bob Esponja na chapa do Siri Cascudo (T1E1 "Help Wanted"). Alternativa: a montagem em T1 "Pickles" |
| Cachorro-quente Krusty | `cachorro-quente-krusty.jpg` | Homer comendo chili dogs na carrocinha do Deuce (T28 "Fatzcarraldo") |
| Donut Rosa do Homer | `donut-rosa-do-homer.jpg` | Homer com a rosquinha da Lard Lad (T7E6 "Treehouse of Horror VI"). Alternativa: "The Devil and Homer Simpson", T5 |
| Ramen Ichiraku Caseiro | `ramen-ichiraku-caseiro.jpg` | Naruto e Iruka no Ichiraku (episódio 1) |
| Panqueca de Bacon do Finn e Jake | `panqueca-de-bacon-do-finn-e-jake.jpg` | Jake fazendo as panquecas (T4E16 "Burning Low") |

- Formatos: `.jpg`, `.jpeg`, `.png` ou `.webp`. Proporção ideal 16:10 (ex.: 1280x800).
- O site procura o arquivo a cada acesso: não precisa reiniciar.
- Sem arquivo, o card mostra um fundo colorido com o emoji do desenho.
- Receitas cadastradas pelo site seguem a mesma regra (`pizza-do-chaves.jpg`).
- Episódio, descrição da cena e crédito de cada receita ficam em `CENAS`, no
  arquivo `app/seed_data.py`.

> **Sobre o Cachorro-quente Krusty:** "Krusty Dog" é um item do *Bob Esponja*
> (Siri Cascudo), não dos Simpsons. A cena mais próxima nos Simpsons é
> "Fatzcarraldo", em que Homer come chili dogs e o Krusty compra a carrocinha.
> Se preferir, renomeie a receita para algo como "Chili dog do Deuce".

## Arquitetura

```text
Navegador -> Service (NodePort) -> 3 pods receitas-web (Flask) -> Service -> pod postgres (volume persistente)
```

Sem PostgreSQL disponível (ou com `USE_SQLITE=1`), o app usa SQLite
automaticamente.

## Estrutura

```text
app/
  app.py                 rotas Flask e acesso ao banco
  seed_data.py           desenhos, receitas e dados das cenas
  templates/             páginas HTML (Jinja)
  static/css/            estilos
  static/images/cenas/   prints dos episódios
k8s/                     manifestos do Kubernetes
docker-compose.yml       app + PostgreSQL
run_local.sh             execução local com SQLite
tests/                   testes automatizados
```

## Recursos do Kubernetes usados

- Deployment: 3 réplicas do site e 1 do banco
- Service: balanceamento entre os pods
- ConfigMap (configurações) e Secret (usuário e senha do banco)
- PersistentVolumeClaim: os dados do banco não se perdem
- Probes de saúde (readiness e liveness) em `/health`
- Limites de CPU e memória por container

## Testes

```bash
curl http://localhost:5000/health   # deve responder: ok

pip install pytest
python -m pytest tests
```

## Demonstração no Kubernetes

```bash
# 1. balanceamento: recarregue a página e veja o nome do pod mudar no rodapé

# 2. auto-recuperação: apague um pod do site e veja o Kubernetes recriar
kubectl get pods
kubectl delete pod <nome-de-um-pod-receitas-web>
kubectl get pods -w

# 3. escalar
kubectl scale deployment receitas-web --replicas=5

# 4. persistência: apague o pod do banco e veja que as receitas continuam
kubectl delete pod -l app=postgres
kubectl get pods -w

# 5. atualização gradual
kubectl rollout restart deployment/receitas-web
```

## Créditos

Projeto acadêmico, sem fins comerciais. Os desenhos, personagens e imagens
pertencem aos seus respectivos donos: Bob Esponja (Nickelodeon/Paramount),
Os Simpsons (20th Television/Disney), Naruto (Masashi Kishimoto/Shueisha, TV
Tokyo, Pierrot) e Hora de Aventura (Cartoon Network/Warner Bros. Discovery).
