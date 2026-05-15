# Política de segurança — Campus IoT

## O que não deve ir para o GitHub

| Item | Motivo |
|------|--------|
| `backend/.env`, `frontend/.env`, `IA/.env` | Senhas de banco, `SECRET_KEY`, `GROQ_API_KEY`, `ESP32_DEVICE_KEY` |
| `esp32/campus_iot/config.h` | Wi‑Fi e `DEVICE_KEY` do hardware |
| `crewAI.py` (cópia local com chave) | Use apenas `crewAI.py.example` no repositório |
| `.venv/`, `node_modules/` | Dependências — reinstale com `pip` / `npm` |
| Dumps de banco (`*.sql`, `*.db`) | Podem conter dados reais de usuários |

No repositório ficam apenas arquivos **`.env.example`** com placeholders.

## Antes do primeiro push

Na raiz do projeto (PowerShell):

```powershell
.\scripts\check-before-github.ps1
```

O script falha se encontrar arquivos sensíveis rastreados ou padrões de chave em arquivos versionados.

## Credenciais vazadas

Se uma chave foi commitada por engano:

1. Revogue a chave no provedor (Groq, Supabase, etc.).
2. Gere novas credenciais e atualize o `.env` local.
3. Remova o segredo do histórico do Git (`git filter-repo` ou suporte do GitHub) — não basta um commit novo.

## Reportar vulnerabilidades

Em ambiente acadêmico, reporte à equipe do projeto e à coordenação do curso antes de divulgar publicamente.
