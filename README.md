# 🏢 Smart Building - ExpoTech 2026

Projeto desenvolvido para o Projeto Integrador da ExpoTech 2026.

🔗 Repositório oficial:
https://github.com/gustavoazzola76261-arch/expotech2026.1

---

## 🎯 Objetivo

Desenvolver um sistema de automação predial inteligente capaz de monitorar presença e controlar iluminação automaticamente, utilizando API e dashboard web.

---

## ⚙️ Funcionalidades

* Monitoramento de presença (TRUE/FALSE)
* Controle de iluminação (ON/OFF)
* API REST (backend)
* Dashboard web (frontend)
* Simulação de sensores
* Histórico simples de dados

---

## 🧠 Tecnologias Utilizadas

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* React.js

### Outros

* Git/GitHub
* Simulação de sensores

---

## 📁 Estrutura do Projeto

```bash
expotech2026.1/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── sensors.py
│   │   │
│   │   ├── services/
│   │   │   └── automation.py
│   │   │
│   │   ├── models/
│   │   │   └── light.py
│   │   │
│   │   ├── ai/
│   │   │   └── model.py
│   │   │
│   │   └── database/
│   │       └── db.py
│   │
│   └── main.py
│
├── smart-building-dashboard/
│   └── src/
│       ├── components/
│       │   ├── StatusCard.js
│       │   ├── LightControl.js
│       │   └── Chart.js
│       │
│       ├── services/
│       │   └── api.js
│       │
│       ├── App.js
│       └── index.js
│
└── README.md
```

---

## 🧩 Organização do Código

### 🔧 Backend (FastAPI)

* **routes/** → Define os endpoints da API (entrada de dados)
* **services/** → Contém a lógica de negócio (automação)
* **models/** → Estruturas de dados do sistema
* **database/** → Conexão e manipulação do banco
* **ai/** → Módulo preparado para inteligência artificial
* **main.py** → Arquivo principal que inicia a API

---

### 💻 Frontend (React)

* **components/** → Componentes reutilizáveis da interface

  * StatusCard → Exibe estado da presença
  * LightControl → Controle manual da luz
  * Chart → Exibição de histórico

* **services/api.js** → Comunicação com o backend

* **App.js** → Componente principal da aplicação

* **index.js** → Ponto de entrada do React

---


---

## 🚀 Como executar o projeto

### 1. Clonar repositório

```bash
git clone https://github.com/gustavoazzola76261-arch/expotech2026.1.git
cd expotech2026.1
```

---

## 🔧 BACKEND (FastAPI)

### 2. Acessar pasta backend

```bash
cd backend
```

---

### 3. Criar ambiente virtual

```bash
python -m venv venv
```

Ativar:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

---

### 4. Instalar dependências

```bash
pip install fastapi uvicorn
```

---

### 5. Rodar servidor

```bash
uvicorn main:app --reload
```

Acesse:
http://127.0.0.1:8000/docs

---

## 🔌 Testes da API

### Simular sensor

POST /sensor-data

```json
{
  "presenca": true
}
```

---

### Ver status

GET /status

---

### Controlar luz

POST /control-light

```json
{
  "status": "off"
}
```

---

## 💻 FRONTEND (Dashboard)

### 6. Acessar pasta do frontend

```bash
cd ../smart-building-dashboard
```

---

### 7. Instalar dependências

```bash
npm install
```

---

### 8. Rodar frontend

```bash
npm start
```

---

## 📊 Dashboard

O sistema apresenta:

* Status da presença
* Estado da luz
* Visualização de dados
* Controle manual da iluminação

---

## 📌 Status do Projeto

🚧 Sprint 2 concluído:

* Backend funcional ✅
* API criada ✅
* Dashboard inicial ✅
* Integração simulada ✅

---

## 🔮 Próximos Passos (Sprint 3)

* Integração com Arduino/ESP32
* Implementação de IA
* Gráficos de histórico
* Automação inteligente

---

## 👨‍💻 Equipe

Projeto multidisciplinar envolvendo:

* Engenharia de Computação
* Engenharia Elétrica
* Engenharia Civil
* Engenharia de Produção
