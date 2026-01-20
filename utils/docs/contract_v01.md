# CONTRATO OFICIAL DE SINCRONISMO (SYNC)
Projeto: Sistema de Inventario Distribuido (Offline-first)
Versao: 1.0 (Consolidada)
Escopo: DB Server (Postgres/Supabase), DB Desktop (SQLite), DB Mobile (SQLite)

---

## 1. Objetivo
Definir regras formais, deterministicas e auditaveis para sincronizacao de dados entre:
- DB Server: autoridade global, identidade, consolidacao, RLS e auditoria.
- DB Desktop: system of record operacional, gestor dos dados do negocio.
- DB Mobile: cliente offline para contagem fisica.

Garantias:
- Offline-first real
- Idempotencia
- Resiliencia a falhas
- Auditabilidade
- Previsibilidade em casos extremos

---

## 2. Autoridade e responsabilidades
### 2.1 Autoridade por dominio
| Dominio | Autoridade |
|---|---|
| Identidade (companies, users) | DB Server |
| Master data (produtos, locais, categorias, barcodes) | DB Desktop |
| Operacao de contagem (inventory_items, zone_user_progress) | Desktop + Mobile |
| Auditoria e divergencias | DB Server |

### 2.2 Onde os registros nascem (source of truth)
| Entidade | Onde nasce |
|---|---|
| companies | Server |
| users | Server |
| master data | Desktop |
| inventory_items | Mobile ou Desktop |
| zone_user_progress | Mobile ou Desktop |

---

## 3. Identidade e chaves
- uuid: identificador global imutavel, chave logica do sync.
- server_id: PK no server, resolvido no backend e devolvido no pull.
- id local: PK do SQLite, irrelevante para sync.

Regra obrigatoria:
- Toda sincronizacao usa uuid como chave idempotente.

---

## 4. Tipos de sync
### 4.1 Push (client -> server)
Origem: Desktop ou Mobile
Transporte: outbox local
Granularidade: 1 registro por operacao
Operacoes: insert, update, soft delete (quando permitido)

### 4.2 Pull (server -> client)
Tipos: full (bootstrap) e incremental
Incremental:
- Regra: server.updated_at > last_server_sync_at
- last_server_sync_at sempre vem do server (server_now)
- Relogio local nunca e usado como referencia

---

## 5. Regras globais
### 5.1 Idempotencia
- Toda operacao e reenviavel sem efeitos colaterais.
- Reenvio do mesmo uuid/operation retorna OK sem modificar estado.

### 5.2 Conflito (LWW)
Comparacao por updated_at:
- client.updated_at < server.updated_at: rejeita
- client.updated_at == server.updated_at: NO-OP (OK idempotente)
- client.updated_at > server.updated_at: aplica

### 5.3 Resiliencia
- Falha em um item nao bloqueia o lote.
- Cada item da outbox e processado isoladamente.
- Erros sao registrados por entidade.

---

## 6. Resolucao de FKs (fechado)
### 6.1 Regra obrigatoria
Toda FK deve ser enviada como:
- *_uuid (obrigatorio)
- *_server_id (opcional, se conhecido)

### 6.2 Comportamento no server
Rejeitar quando:
- FK inexistente
- FK de outra empresa
- FK inativa (is_active=false)
- FK com deleted_at

### 6.3 Resposta padrao
```json
{
  "status": "rejected",
  "error_code": "FK_NOT_RESOLVED",
  "entity": "inventory_items",
  "field": "product_uuid",
  "uuid": "..."
}
```
O registro permanece na outbox e pode ser reenviado. Falha isolada.

---

## 7. Soft delete e exclusao (decisao final)
Regra-mae:
- is_active e o unico mecanismo operacional no sync (desktop e mobile).
- deleted_at e exclusivo do DB Server para auditoria e historico legal.
- deleted_at nao participa do sync (nem push nem pull).
- Desktop/Mobile ignoram deleted_at.

Entidades imutaveis/append-only:
- inventory_items (contagem)
- zone_user_progress (progresso)
- auditoria/logs (inventory_item_events, inventory_item_revisions, workflow_logs)

Empresas e usuarios:
- Nunca deletar.
- Desativacao via is_active=false (server-side).

Correcoes e fechamento:
- inventory_items e zone_user_progress sao append-only por regra.
- Atualizacoes sao permitidas apenas antes do fechamento da zona/evento.
- O fechamento e definido no server por status/lock e e a fonte de verdade para permitir bloqueio de updates.

---

## 8. Operacoes permitidas por entidade
Nota: esta matriz consolida direcao e regras minimas por entidade. Campos sensiveis nunca sao atualizaveis via sync (uuid, id, server_id, company_id, created_at, updated_at).
| Entidade | Origem | INSERT | UPDATE | DELETE fisico | Soft delete |
|---|---|---|---|---|---|
| companies | Server | nao | nao | nao | nunca |
| users | Server | nao | allowlist (name, role, is_active) | nao | is_active |
| locations | Desktop | sim | allowlist | nao | is_active |
| product_categories | Desktop | sim | allowlist | nao | is_active |
| products | Desktop | sim | allowlist | nao | is_active |
| product_barcodes | Desktop | sim | allowlist | nao | is_active |
| inventory_events | Desktop | sim | allowlist | nao | is_active (evitar delete) |
| inventory_event_targets | Desktop | sim | allowlist | nao | is_active |
| zones | Desktop | sim | allowlist | nao | is_active |
| inventory_items | Mobile/Desktop | sim | permitido antes do fechamento (gera eventos) | nao | nao (append-only) |
| zone_user_progress | Mobile/Desktop | sim | allowlist (items_counted, qty_total, is_finished, finished_at) | nao | nao (append-only) |
| devices | Mobile/Desktop | sim | allowlist (last_sync_at, app_version, metadata) | nao | is_blocked (server-only) |
| inventory_divergences | Server | nao | nao | nao | append-only |
| inventory_item_events | Server | nao | nao | nao | append-only |
| inventory_item_revisions | Server | nao | nao | nao | append-only |
| workflow_logs | Server | nao | nao | nao | append-only |

---

## 9. Allowlists finais por entidade operacional
Campos fora da allowlist sao rejeitados explicitamente. Company_id, FKs estruturais e uuid nunca mudam.
| Entidade | Allowlist de UPDATE |
|---|---|
| inventory_events | title, status, event_type, required_counts, required_audits, tolerance_* |
| inventory_event_targets | expected_qty, is_active |
| zones | name, description, count_status, lock_status, is_active |
| locations | code, name, address, is_active |
| products | name, description, uom_*, conversion_factor, cost_price, is_sensitive, serial_number_enabled, is_active |
| product_barcodes | barcode, description, is_active |
| product_categories | code, name, description, is_active |

---

## 10. Fechamento de zona e evento (decisao final)
### 10.1 Fechamento de zona
Estado:
- Tabela: zones
- Campo: count_status
- Valores: not_started, counting, finished, locked

Quem pode fechar:
- Desktop (admin, manager, coordinator, auditor)
- Mobile nao fecha zonas globalmente

Quando fecha:
- Todos os zone_user_progress.is_finished = true
- Se required_counts estiver definido no evento (> 0), deve ser atendido

Acao:
- Desktop executa count_status = "finished"
- Server valida e persiste
- Mobile passa a somente leitura para a zona

### 10.2 Fechamento de evento
Estado:
- Tabela: inventory_events
- Campo: status
- Fluxo: planned -> open -> counting -> closed -> finalized

Quem pode fechar:
- Desktop por decisao explicita do gestor
- Mobile nao fecha eventos

Quando fecha:
- Todas as zonas do evento estao finished
- Auditorias concluidas ou dispensadas (quando aplicavel)

Acao:
- Desktop executa status = "closed"
- Server valida consistencia
- Mobile recebe evento como somente leitura

Estado terminal:
- finalized e terminal.
- Apos finalized, nenhuma entidade relacionada aceita insert/update.

---

## 11. Regras especificas do mobile
- Mobile cria e atualiza apenas: inventory_items, zone_user_progress, devices.
- Mobile nunca cria eventos, zonas, produtos, categorias, barcodes, targets.
- Mobile pode registrar contagem fora do target (is_new_product=true).
- Server decide inclusao posterior.

## 12. Origem e enforcement
- O backend valida origem da operacao por role do usuario, tipo de device e endpoint.
- Operacoes fora do escopo sao rejeitadas com erro explicito:
```json
{
  "status": "rejected",
  "error_code": "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
}
```

## 13. Devices (ciclo de vida)
- devices.is_blocked so pode ser alterado por admin/server.
- devices nao usa is_active; o controle e feito apenas por is_blocked.
- Mobile/Desktop podem apenas atualizar dados tecnicos (last_sync_at, app_version, metadata).
- Se is_blocked=true, o server rejeita push:
```json
{
  "status": "rejected",
  "error_code": "DEVICE_BLOCKED"
}
```

---

## 14. Logging e auditoria
### 14.1 Client (outbox_local)
Campos minimos:
- table_name
- record_uuid
- operation
- attempts
- last_error
- created_at

### 14.2 Server (logging estruturado JSON)
Campos minimos:
- entity
- operation
- uuid
- status
- error_code
- server_timestamp
- correlation_id
- user_id
- device_id

---

## 15. Testabilidade (base para QA)
Cada entidade deve ter testes para:
- insert valido
- insert duplicado (idempotencia)
- FK invalida
- conflito de timestamp
- retry apos erro
- sync parcial com falha isolada
