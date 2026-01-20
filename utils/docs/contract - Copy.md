# 📘 CONTRATO OFICIAL DE SINCRONIZAÇÃO (SYNC)

**Projeto:** Sistema de Inventário Distribuído  
**Versão:** 1.0 (Final – Consolidada)  
**Escopo:** DB Server (Postgres/Supabase) ↔ DB Desktop (SQLite) ↔ DB Mobile (SQLite)

---

## 1️⃣ Objetivo do Contrato

Definir **regras formais, determinísticas e auditáveis** para sincronização de dados entre:

- **DB Server (Postgres / Supabase)**  
  Autoridade global, identidade, auditoria, consolidação e RLS.
- **DB Desktop (SQLite)**  
  *System of Record operacional* – gestor dos dados do negócio.
- **DB Mobile (SQLite)**  
  Cliente offline responsável pela **contagem física de estoque**.

O contrato garante:
- Offline-first real  
- Idempotência  
- Resiliência a falhas  
- Auditabilidade  
- Previsibilidade em casos extremos  

---

## 2️⃣ Papéis e Autoridade dos Sistemas

### 2.1 Autoridade por domínio

| Domínio | Autoridade |
|------|-----------|
| Identidade (companies, users) | **DB Server** |
| Dados mestre (produtos, locais, eventos, zonas, targets) | **DB Desktop** |
| Operação de contagem (inventory_items, progress) | Desktop / Mobile |
| Consolidação, auditoria, divergências | **DB Server** |

---

### 2.2 Criação de registros (fonte da verdade)

| Entidade | Onde nasce |
|-------|-----------|
| companies | Server |
| users | Server |
| Todas as demais | Desktop |
| inventory_items (campo) | Mobile ou Desktop |

---

## 3️⃣ Identificadores e Chaves

### 3.1 Identificação universal

Todas as entidades sincronizáveis possuem:

- `uuid` → **Identificador global imutável**
- `server_id` → Preenchido após sync com Server
- `id` → Local (SQLite), irrelevante para sync

📌 **Regra**
- UUID é a chave primária lógica entre sistemas.
- `server_id` pode ser `NULL` até confirmação do Server.

---

### 3.2 Resolução de FKs (decisão formal)

Durante **PUSH**:

- Toda FK é enviada como:
  - `*_uuid` (obrigatório)
  - `*_server_id` (se conhecido)

**Se FK não resolver no Server:**
- ❌ Rejeitar operação  
- ✅ Registrar erro na outbox  
- ❌ Não criar placeholder  
- ❌ Não bloquear outras entidades  

---

## 4️⃣ Estratégia de Sincronização

### 4.1 Tipos de Sync

| Tipo | Direção | Objetivo |
|---|---|---|
| PUSH | Client → Server | Enviar alterações locais |
| PULL | Server → Client | Atualizar cache local |
| FULL | Server → Client | Bootstrap / reset |
| INCREMENTAL | Server → Client | Atualizações desde último sync |

---

## 5️⃣ Controle de Tempo (Clock & Incremental)

### 5.1 Regra definitiva (clock skew resolvido)

- `last_sync_at` **SEMPRE** usa **SERVER TIMESTAMP**
- Nunca usar relógio local

**Regra incremental**

server.updated_at > local.last_server_sync_at


📌 O Server retorna sempre:
- `server_now`
- Esse valor é salvo como `last_server_sync_at`

---

## 6️⃣ Regras de Escrita (PUSH)

### 6.1 Operações permitidas

| Operação | Permitido |
|-------|----------|
| INSERT | ✅ |
| UPDATE | ✅ |
| DELETE físico | ❌ |
| Soft delete | Depende da entidade |

---

### 6.2 Idempotência

- Toda operação é identificada por:
  - `uuid`
  - `operation`
- Reenvio da mesma operação:
  - Retorna **OK sem efeito**
  - Não duplica dados

---

### 6.3 Conflitos (LWW – Last Write Wins)

**Regra final**

Se client.updated_at < server.updated_at → rejeita
Se client.updated_at = server.updated_at → ignora (OK idempotente)
Se client.updated_at > server.updated_at → aceita


---

## 7️⃣ Regras de Leitura (PULL)

### 7.1 Escopo

- Pull é **sempre filtrado por company**
- Mobile recebe:
  - Dados mínimos para operar
  - Dados completos apenas onde necessário (produtos, barcodes)

---

### 7.2 FULL vs INCREMENTAL

| Situação | Tipo |
|------|------|
| Primeiro login | FULL |
| Troca de empresa | FULL + wipe local |
| Operação normal | INCREMENTAL |
| Erro de consistência | FULL |

---

## 8️⃣ Soft Delete e Ativação (decisão final)

### 8.1 Regra unificada por entidade

| Entidade | delete_at | is_active | Regra |
|--------|-----------|----------|------|
| companies | ❌ | ✅ | Nunca deletar |
| users | ❌ | ✅ | Nunca deletar |
| locations | ❌ | ✅ | Desativação lógica |
| products | ❌ | ✅ | Desativação lógica |
| product_barcodes | ❌ | ✅ | Desativação lógica |
| inventory_events | ❌ | ✅ | Não deletar após iniciar |
| inventory_event_targets | ❌ | ✅ | Pode desativar |
| zones | ❌ | ✅ | Pode desativar |
| inventory_items | ❌ | ❌ | Nunca deletar |
| zone_user_progress | ❌ | ❌ | Nunca deletar |
| divergences | ❌ | ❌ | Imutável |
| item_events | ❌ | ❌ | Append-only |
| item_revisions | ❌ | ❌ | Append-only |
| workflow_logs | ❌ | ❌ | Append-only |

📌 **Decisão chave**
- Não misturar `deleted_at` e `is_active`
- `deleted_at` é **exclusivamente Server-side** quando existir
- Desktop/Mobile usam **is_active**

---

## 9️⃣ Regras Específicas do Mobile

### 9.1 Papel do Mobile

- Executa **contagem física**
- Opera offline
- Cria:
  - `inventory_items`
  - `zone_user_progress`
- Nunca:
  - Cria eventos, zonas, produtos
  - Resolve divergências

---

### 9.2 Produtos fora do target

Fluxo suportado:

1. Scanner lê barcode  
2. Produto existe, mas:
   - Fora do target  
   - Ou inativo  
3. Mobile:
   - **Permite contagem**
   - Marca `is_new_product = true`
4. Server decide inclusão posteriormente

---

## 🔟 Resiliência e Falhas

### 10.1 Regra fundamental

> **Falha em uma entidade nunca bloqueia outras**

- Cada item da outbox é independente
- Retry exponencial
- Erros são isolados

---

## 11️⃣ Auditoria e Logging

### 11.1 Client-side

Tabela: `outbox_local`

Campos obrigatórios:
- table_name
- record_uuid
- operation
- attempts
- last_error
- created_at

---

### 11.2 Server-side (obrigatório)

Logging estruturado (JSON):

Campos mínimos:
- entity
- operation
- uuid
- server_id
- error_code
- user_id
- device_id
- request_id
- timestamp

---

## 12️⃣ Segurança e Integridade

- Server valida:
  - Company ownership
  - Role (RLS)
  - FK resolution
- Mobile/Desktop:
  - Nunca confiam em dados locais para autoridade

---

## 13️⃣ Testabilidade (base para QA)

Cada entidade deve ter testes para:
- Insert válido
- Insert duplicado (idempotência)
- FK inválida
- Conflito de timestamp
- Retry após erro
- Sync parcial com falha isolada

---

## 🧾 Resumo Executivo

> Modelo de sincronização offline-first profissional, determinístico e auditável, com separação clara de responsabilidades entre Server, Desktop e Mobile, pronto para produção e testes E2E.