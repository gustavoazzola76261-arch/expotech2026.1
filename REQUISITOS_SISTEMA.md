Documento de Requisitos — Sistema de Automação de Infraestrutura Acadêmica
Objetivo do Projeto
Desenvolver um sistema inteligente de automação predial para controle da infraestrutura das salas da faculdade, inicialmente focado em iluminação, permitindo monitoramento, economia de energia, segurança no acesso e escalabilidade para novos dispositivos.

Problema que o Projeto Resolve
Desperdício de energia
Lâmpadas permanecem ligadas sem necessidade.
Falta de controle automático de consumo.
Uso ineficiente de ar-condicionado e iluminação.
Falta de controle centralizado
Controle manual e descentralizado.
Dificuldade de gerenciamento das salas.
Ausência de monitoramento
Não existe histórico de acionamentos.
Não há cálculo de consumo energético.
Não há geração de relatórios.
Falta de rastreabilidade
Não é possível identificar:
quem acionou
quando acionou
qual sala foi utilizada
quanto foi consumido
Baixa escalabilidade do modelo atual
Estrutura atual não suporta crescimento.
Dificuldade para adicionar:
novas salas
novos dispositivos
sensores
automações

Escopo Inicial do Projeto
Estrutura física inicial
5 salas
Até 3 lâmpadas por sala
Componentes iniciais
Controle de iluminação
Monitoramento de consumo
Controle por usuários


Arquitetura do Sistema
Padrão arquitetural
API REST
API First
Arquitetura modular
Estrutura escalável
Objetivos da arquitetura
Facilidade de manutenção
Escalabilidade
Separação de responsabilidades
Integração futura com novos dispositivos

API REST
Requisitos
Comunicação padronizada via HTTP/HTTPS
Uso de métodos REST:
GET
POST
PUT
DELETE
Exemplos de endpoints
GET /salas
GET /salas/{id}/lampadas
POST /lampadas/{id}/ligar
POST /lampadas/{id}/desligar
GET /consumo
Boas práticas
Respostas em JSON
Versionamento de API
Padronização de erros
Documentação automática

API First
Objetivo
Definir toda a estrutura da API antes da implementação.
Deve conter
Endpoints
Regras de acesso
Estrutura de respostas
Estrutura de erros
Métodos HTTP
Contratos da API
Ferramentas recomendadas
Swagger/OpenAPI

Contrato da API
O contrato deve definir
Dados enviados
Dados recebidos
Tipos de campos
Regras de validação
Permissões de acesso
Códigos de retorno HTTP
Objetivo
Garantir:
padronização
previsibilidade
integração segura
facilidade de manutenção

Controle de Usuários e Permissões
Tipos de usuários
Professor
Permissões:
Controlar apenas as lâmpadas da sala em que está vinculado.
Restrições:
Não acessar outras salas.
Não acessar configurações administrativas.

Mestre
Permissões:
Controlar todas as 5 salas.
Monitorar todas as lâmpadas.
Restrições:
Não alterar configurações críticas do sistema.

Administrador
Permissões:
Controle total do sistema.
Gerenciamento de usuários.
Gerenciamento de dispositivos.
Acesso ao ambiente de simulação.
Acesso aos relatórios.
Configuração de automações.
Funções adicionais:
Criar rotinas automáticas.
Configurar horários.
Definir regras de acionamento.

Autenticação e Segurança
Autenticação
OAuth 2.0
JWT
Sessões seguras
Segurança de comunicação
HTTPS/TLS
Criptografia de dados
Proteção contra interceptação
Segurança da API
Seguir recomendações:
OWASP API Security 2023
Pontos obrigatórios
Controle de permissões
Validação de entrada
Proteção contra acesso indevido
Proteção contra brute force
Rate limiting
Logs de segurança

LGPD
O sistema deve
Proteger dados pessoais.
Registrar acessos e ações.
Restringir acesso a dados sensíveis.
Garantir rastreabilidade de operações.
Dados armazenados
Usuários
Histórico de acionamentos
Logs de acesso
Consumo energético

Banco de Dados
Objetivo
Persistência e rastreabilidade das informações do sistema.
Informações armazenadas
Usuários
Nome
Email
Perfil
Permissões
Salas
Identificação
Dispositivos vinculados
Lâmpadas
Potência
Status
Sala vinculada
Histórico de acionamentos
Usuário responsável
Data e hora
Dispositivo acionado
Tipo de ação
Consumo energético
Tempo ligado
Consumo calculado
Histórico diário/mensal

Cálculo de Consumo Energético
Objetivo
Calcular automaticamente o consumo energético das lâmpadas.
Informações utilizadas
Potência oficial da lâmpada
Tempo em que permaneceu ligada
Fórmula utilizada
Consumo (kWh)=Potencia (W)×Tempo (h)1000Consumo\,(kWh)=\frac{Potencia\,(W)\times Tempo\,(h)}{1000}Consumo(kWh)=1000Potencia(W)×Tempo(h)​
Exemplo
Lâmpada de 20W ligada por 5 horas:

20 × 5 / 1000 = 0,1 kWh

Inteligência Artificial
Objetivos da IA
Gerar relatórios automáticos.
Identificar desperdícios.
Detectar padrões de consumo.
Sugerir melhorias de eficiência energética.
Funções previstas
Relatórios automáticos.
Sugestão de economia.
Detecção de uso anormal.
Análise histórica de consumo.
Exemplos de sugestões da IA
Identificação de salas com alto consumo.
Sugestão de horários ideais de desligamento.
Alertas de desperdício energético.

Ambiente de Simulação
Objetivo
Permitir testes sem depender do hardware físico.
Funções
Simular salas.
Simular lâmpadas.
Simular consumo.
Testar automações.
Validar regras da API.
Benefícios
Desenvolvimento mais rápido.
Redução de riscos.
Ambiente seguro para testes.

Automação de Rotinas
Funcionalidades
Agendamento automático.
Ligamento/desligamento programado.
Rotinas por horário.
Rotinas por sala.
Controle administrativo
Apenas administradores podem:
Criar rotinas
Editar rotinas
Remover rotinas

Ar-Condicionado
Controle previsto
Temperatura fixa em 23°C.
Objetivos
Padronização.
Economia energética.
Conforto térmico.
Normas relacionadas
Consultar:
NR-17 (Ergonomia e conforto ambiental)

Escalabilidade
O sistema deve permitir
Adição de novas salas.
Adição de novas lâmpadas.
Inclusão de novos dispositivos.
Integração com sensores.
Dispositivos futuros
Ar-condicionado
Ventiladores
Sensores de presença
Sensores de temperatura
Sensores de luminosidade

Disponibilidade e Estabilidade
O sistema deve
Operar continuamente por vários dias.
Possuir recuperação automática de falhas.
Registrar logs de erros.
Garantir estabilidade da comunicação.
Requisitos técnicos
Reconexão automática.
Monitoramento de falhas.
Persistência de sessões.

Requisitos Técnicos Recomendados
Backend
Tecnologia definida
Python
Framework recomendado
FastAPI
Responsabilidades
API REST
Autenticação OAuth2.0
Regras de negócio
Controle de permissões
Processamento de consumo energético
Comunicação com ESP32
Geração de relatórios
Integração com IA
Logs e monitoramento
Evoluções futuras
Separação em microsserviços
Filas de processamento
WebSockets ou MQTT em tempo real
Balanceamento de carga

Frontend
Tecnologia definida
JavaScript
Framework recomendado
React
Possível evolução
Next.js
Responsabilidades
Dashboard principal
Controle das salas
Controle das lâmpadas
Relatórios de consumo
Painel administrativo
Ambiente de simulação
Visualização de status dos dispositivos
Evoluções futuras
Aplicação mobile
Painel em tempo real
Notificações automáticas
Dashboard analítico avançado

Banco de Dados
Tecnologia recomendada
PostgreSQL
Plataforma online recomendada
Supabase
usando url=https://fdughvepjlbfggtcoxef.supabase.co
service_role =eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZkdWdodmVwamxiZmdndGNveGVmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY4OTA3NiwiZXhwIjoyMDk0MjY1MDc2fQ.nXzG3SbkcltzOcqTeu-WqVFcjxn9Pj-IPBn63_9JBIQ
Responsabilidades
Armazenamento de usuários
Histórico de acionamentos
Histórico de consumo energético
Logs do sistema
Configurações e automações
Evoluções futuras
Replicação de banco
Backup automatizado
Clusterização
Data warehouse para análise avançada

Comunicação IoT
Arquitetura atual
ESP32 realizando requisições HTTP para a API.
Fluxo atual
ESP32 envia estado dos sensores.
Backend processa regras.
ESP32 consulta status dos dispositivos.
ESP32 executa acionamentos físicos.
Tecnologias utilizadas
HTTP/HTTPS
JSON
ESP32
Evoluções futuras
MQTT
Comunicação em tempo real
Redução de polling HTTP
Broker MQTT dedicado
Eventos assíncronos


