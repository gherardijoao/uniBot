# 🐳 Docker — Guia Completo

Guia para containerizar, rodar e deployar o uniBot com Docker e Docker Compose.

---

## 📋 Pré-requisitos

Instale:
- **Docker Desktop** (Windows): https://www.docker.com/products/docker-desktop
- **Docker CLI** + **Docker Compose** (Linux): `sudo apt install docker.io docker-compose`

Verifique a instalação:
```powershell
docker --version
docker-compose --version
```

---

## 🚀 Início Rápido

### Opção 1: Produção (recomendado para deploy)

```powershell
# 1. Configurar .env
Copy-Item .env.docker.example .env
# Editar .env e preencher GOOGLE_API_KEY, etc

# 2. Build e start
docker-compose up --build

# 3. Acessar
# Backend: http://localhost:8000
# Frontend: http://localhost (porta 80)
```

### Opção 2: Desenvolvimento (com hot reload)

```powershell
# 1. Configurar .env
Copy-Item .env.docker.example .env

# 2. Start com docker-compose.dev.yml
docker-compose -f docker-compose.dev.yml up

# 3. Acessar
# Backend: http://localhost:8000
# Frontend: http://localhost:5173 (Vite dev server)
```

---

## 📁 Estrutura Docker

### `docker-compose.yml` (Produção)

```yaml
services:
  backend:
    # FastAPI em Python 3.11
    # Porta: 8000
    # Volume: chroma_db (persistência)
  
  frontend:
    # React + Vite + Nginx
    # Porta: 80
    # Dependency: backend (health check)
```

### `docker-compose.dev.yml` (Desenvolvimento)

```yaml
services:
  backend:
    # FastAPI com --reload (automatic restart)
    # Porta: 8000
    # Volumes: código + chroma_db

  frontend:
    # Vite dev server
    # Porta: 5173 (dev) + 80 (proxy)
    # Volumes: src + public (hot reload)
```

---

## 🛠️ Comandos Principais

### Build (criar imagens)

```powershell
# Build completo
docker-compose build

# Build apenas backend
docker-compose build backend

# Build com pull de imagens base
docker-compose build --pull
```

### Start (rodar containers)

```powershell
# Iniciar em background
docker-compose up -d

# Iniciar com logs visíveis
docker-compose up

# Iniciar com rebuild
docker-compose up --build
```

### Stop / Restart

```powershell
# Parar todos os containers
docker-compose down

# Parar mas manter volumes
docker-compose down --volumes

# Remover tudo (containers, networks, volumes)
docker-compose down -v

# Reiniciar um serviço
docker-compose restart backend
```

### Logs

```powershell
# Ver logs de todos
docker-compose logs

# Ver logs em tempo real
docker-compose logs -f

# Logs apenas do backend
docker-compose logs backend

# Últimas 50 linhas
docker-compose logs --tail=50
```

### Executar comandos dentro de containers

```powershell
# Terminal interativo no backend
docker-compose exec backend bash

# Rodar comando (ex: Python)
docker-compose exec backend python -c "print('Hello')"

# Fazer ingestão de documentos
docker-compose exec backend python -m app.ingest
```

### Remover volumes e recomeçar

```powershell
# Limpar tudo e começar do zero
docker-compose down -v
docker-compose up --build
```

---

## 🌍 URLs e Portas

| Serviço | URL | Porta | Dev Port |
|---------|-----|-------|----------|
| Backend API | `http://localhost:8000` | 8000 | 8000 |
| Backend Docs (Swagger) | `http://localhost:8000/docs` | 8000 | 8000 |
| Frontend | `http://localhost` | 80 | 5173 |
| Nginx | - | 80 | - |

---

## 🔧 Configuração

### 1. Copiar template `.env`

```powershell
Copy-Item .env.docker.example .env
```

### 2. Preencher `.env`

```bash
# Obrigatório
GOOGLE_API_KEY=sua_chave_do_gemini

# Opcional (SIG)
SIG_BASE_URL=https://sig.ufla.fr
SIG_API_KEY=sua_chave

# Opcional (debug)
LOG_LEVEL=INFO
DEBUG=False
```

### 3. Variáveis de Ambiente por Serviço

Ver `docker-compose.yml` seção `environment:`.

---

## 💾 Volumes e Dados Persistentes

### `chroma_db`
- **O que**: Base de vetores (embeddings)
- **Persistência**: ✅ Sim (volume named)
- **Limpeza**: `docker-compose down -v` (remove volume)

### `backend/data/`
- **O que**: PDFs e TXTs para ingestão
- **Persistência**: ✅ Sim (bind mount)
- **Uso**: Copiar arquivos para `./backend/data/` e rodar `python -m app.ingest`

---

## 🏥 Health Checks

### Backend

```bash
curl http://localhost:8000/health
# {"status": "ok", "rag_initialized": true, ...}
```

### Frontend

```bash
curl http://localhost/health
# ok
```

---

## 🐛 Troubleshooting

### ❌ "Port 8000 already in use"

```powershell
# Parar container anterior
docker-compose down

# Ou usar porta diferente
# Editar docker-compose.yml: "8001:8000"
```

### ❌ "Backend não encontra Chroma DB"

```powershell
# Verificar volume
docker volume ls | grep chroma_db

# Limpar e recomeçar
docker-compose down -v
docker-compose up --build
```

### ❌ "GOOGLE_API_KEY não definida"

```powershell
# Verificar .env
cat .env

# Atualizar .env e reiniciar
docker-compose restart backend
```

### ❌ "Frontend não conecta ao Backend"

```powershell
# Verificar logs
docker-compose logs frontend

# Backend está rodando?
docker-compose ps

# Testar conexão dentro do container
docker-compose exec frontend curl http://backend:8000/health
```

### ❌ "Build falha (módulos Python)"

```powershell
# Limpar cache e rebuild
docker system prune
docker-compose build --no-cache

# Ou instalar dependências localmente
pip install -r backend/requirements.txt
```

---

## 📊 Monitoração

### Ver recursos (CPU, memória, etc)

```powershell
docker stats

# Apenas backend
docker stats unibot-backend
```

### Histórico de logs

```powershell
# Salvar logs em arquivo
docker-compose logs > unibot-logs.txt

# Ver erros apenas
docker-compose logs | Select-String ERROR
```

---

## 🚀 Deploy (Produção)

### Passo 1: Build final

```powershell
docker-compose build --pull
```

### Passo 2: Verificar imagens

```powershell
docker images | Select-String unibot
```

### Passo 3: Start em background

```powershell
docker-compose up -d
```

### Passo 4: Verificar health

```powershell
docker-compose ps
curl http://localhost:8000/health
```

### Passo 5: Fazer backup de dados

```powershell
# Backup do chroma_db
docker run --volumes-from unibot-backend `
  -v C:\backups:/backup `
  alpine tar czf /backup/chroma_db.tar.gz /app/chroma_db
```

---

## 🔄 CI/CD (GitHub Actions - exemplo)

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose up -d && sleep 5 && curl http://localhost:8000/health
```

---

## 📝 Arquivo Útil: `.dockerignore`

Já incluído, mas referência dos arquivos que não são copiados para Docker:

```
node_modules/
__pycache__/
.env
chroma_db/
.git
.vscode/
```

---

## ✅ Checklist de Deploy

- [ ] `.env` configurado com GOOGLE_API_KEY
- [ ] `docker-compose.yml` revisado
- [ ] Build bem-sucedido
- [ ] Health checks passando
- [ ] Dados persistentes em volumes
- [ ] Logs monitoráveis
- [ ] Backup de dados configurado
- [ ] Documentação atualizada

---

## 🎓 Próximos Passos

1. **Kubernetes**: Deploy em produção com K8s
2. **Registry Privado**: Usar Docker Hub ou GitHub Container Registry
3. **Secrets Management**: Usar `.env` seguro ou Docker secrets
4. **Monitoring**: Integrar Prometheus, Grafana
5. **Logging Centralizado**: ELK stack ou CloudWatch

---

## 📚 Referências

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
- [Node.js Docker Best Practices](https://docs.docker.com/language/nodejs/)

---

## 🆘 Suporte

- Verificar `.env` e permissões
- Ver logs: `docker-compose logs`
- Limpar tudo: `docker system prune -a`
- Documentação: Ver `SETUP_WINDOWS.md`, `TOOLS.md`

