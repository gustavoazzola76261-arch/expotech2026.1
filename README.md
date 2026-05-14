# Campus IoT — Automação de infraestrutura acadêmica

Sistema **API-first** para controle de iluminação por sala, com **FastAPI (Python)**, **PostgreSQL (Supabase/local)**, **React (TypeScript)** e autenticação **OAuth2 Password Grant + JWT**.

Documento de requisitos: `REQUISITOS_SISTEMA.md`.

**Guia passo a passo para instalar dependências, configurar o Postgres, subir API e interface:** veja [`GUIA_EXECUCAO.md`](GUIA_EXECUCAO.md).

## O que já está implementado (Etapas 1–4)

| Etapa | Conteúdo |
|-------|-----------|
| **1 — Arquitetura** | Monorepo `backend/` + `frontend/`, API versionada `/api/v1`, camadas (modelos, schemas, serviços, rotas). |
| **2 — Backend** | FastAPI, OAuth2 (`/api/v1/auth/token`), JWT, RBAC (professor / mestre / admin), CRUD mínimo de usuários (admin), controle de lâmpadas, histórico de acionamentos com cálculo de kWh ao desligar, resumo de consumo (**admin**), rate limit no login. |
| **3 — Banco** | Modelagem Postgres (usuários, salas, lâmpadas, vínculo professor–sala, logs de acionamento), migrations **Alembic**. |
| **4 — Frontend** | Login, listagem de salas (mestre/admin), professor direto na sala, controle on/off por lâmpada, resumo de consumo (admin), painel de usuários (admin). |

**Próximas etapas (não feitas neste ciclo):** firmware ESP32, simulação, IA, hardening ampliado, MQTT.

## Estrutura do repositório

```
backend/
  alembic/                 # migrations
  app/
    api/v1/endpoints/      # rotas REST
    core/                  # segurança (JWT, hash)
    models/                # SQLAlchemy
    schemas/               # Pydantic
    services/              # regras de acesso / usuários
    main.py
    seed.py                # dados de demonstração
  requirements.txt
  .env.example
frontend/
  src/                     # React + Vite
  package.json
  .env.example
REQUISITOS_SISTEMA.md
README.md
```

## Pré-requisitos

- Python **3.11+**
- Node.js **20+** (recomendado)
- PostgreSQL acessível (local ou **Supabase** — use a *connection string* do painel, **sem** commitar segredos)

## Backend — como executar

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env          # edite DATABASE_URL, SECRET_KEY, CORS_ORIGINS
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Documentação interativa: `http://localhost:8000/docs`
- **Health:** [http://localhost:8000/health](http://localhost:8000/health) ou [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) — `{"status":"ok"}`
- **Raiz:** [http://localhost:8000/](http://localhost:8000/) — metadados da API (útil para confirmar que o processo certo está no ar)

### OAuth2 (usuário e senha)

`POST /api/v1/auth/token` com corpo **form-urlencoded**:

- `username`: e-mail do usuário
- `password`: senha

Resposta: `{ "access_token": "...", "token_type": "bearer" }`  
Demais rotas: cabeçalho `Authorization: Bearer <token>`.

### Usuários de demonstração (após `seed`)

| E-mail | Senha | Papel |
|--------|--------|--------|
| `admin@fecaf.local` | `Admin12345!` | Admin |
| `mestre@fecaf.local` | `Mestre12345!` | Mestre |
| `professor@fecaf.local` | `Professor123!` | Professor (sala 1) |

**Altere essas senhas** antes de qualquer ambiente real.

## Frontend — como executar

```bash
cd frontend
npm install
copy .env.example .env        # opcional: VITE_API_URL vazio usa proxy do Vite
npm run dev
```

Abra `http://localhost:5173`. O proxy encaminha `/api` e `/health` para `http://127.0.0.1:8000`.

## Endpoints principais

| Método | Caminho | Descrição |
|--------|---------|-----------|
| POST | `/api/v1/auth/token` | Login OAuth2 password |
| GET | `/api/v1/me` | Perfil + salas (professor) |
| GET | `/api/v1/rooms` | Lista de salas (filtrada por papel) |
| GET | `/api/v1/rooms/{id}/lamps` | Lâmpadas da sala |
| POST | `/api/v1/lamps/{id}/command` | `{"action":"on"\|"off"}` |
| GET | `/api/v1/consumption/summary` | Soma de kWh (somente **admin**) |
| GET | `/api/v1/consumption/monthly` | Série mensal de kWh; query `months=1\|3\|6\|12`, opcional `room_id` (**admin**) |
| GET/POST | `/api/v1/admin/users` | Lista / cria usuário (admin) |
| PATCH | `/api/v1/admin/users/{id}` | Atualiza usuário (admin) |

## Segurança e LGPD (base)

- Senhas com **bcrypt**; JWT com expiração configurável.
- Infraestrutura para **rate limiting** (SlowAPI) disponível no app; endpoints podem ser protegidos conforme necessidade.
- **RBAC** por objeto (sala/lâmpada) para professor.
- Logs de acionamento com usuário e energia estimada ao desligar.
- **Não** versionar `.env`, chaves Supabase ou `service_role` — use apenas variáveis de ambiente.

## Licença

Projeto acadêmico — defina a licença conforme a instituição.
