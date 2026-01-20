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

## 7. Soft delete e exclusao
Regra-mae:
- Nao misturar deleted_at e is_active como mecanismo operacional.
- is_active: controle operacional e visibilidade.
- deleted_at: uso interno de auditoria no server, nao participa do sync.
- Desktop/Mobile ignoram deleted_at.

Entidades imutaveis/append-only:
- inventory_items (contagem)
- zone_user_progress (progresso)
- auditoria/logs (inventory_item_events, inventory_item_revisions, workflow_logs)

Empresas e usuarios:
- Nunca deletar.
- Desativacao via is_active=false.

---

## 8. Operacoes permitidas por entidade
Nota: esta matriz consolida direcao e regras minimas por entidade.
| Entidade | Origem | INSERT | UPDATE | DELETE fisico | Soft delete |
|---|---|---|---|---|---|
| companies | Server | nao | nao | nao | nunca |
| users | Server | nao | update limitado | nao | is_active |
| locations | Desktop | sim | allowlist | nao | is_active |
| product_categories | Desktop | sim | allowlist | nao | is_active |
| products | Desktop | sim | allowlist | nao | is_active |
| product_barcodes | Desktop | sim | allowlist | nao | is_active |
| inventory_events | Desktop | sim | allowlist | nao | is_active (evitar delete) |
| inventory_event_targets | Desktop | sim | allowlist | nao | is_active |
| zones | Desktop | sim | allowlist | nao | is_active |
| inventory_items | Mobile/Desktop | sim | permitido (correcoes) | nao | nunca (append-only) |
| zone_user_progress | Mobile/Desktop | sim | permitido (progresso) | nao | nunca (append-only) |
| inventory_divergences | Server | nao | nao | nao | append-only |
| inventory_item_events | Server | nao | nao | nao | append-only |
| inventory_item_revisions | Server | nao | nao | nao | append-only |
| workflow_logs | Server | nao | nao | nao | append-only |

---

## 9. Regras especificas do mobile
- Mobile cria e atualiza apenas: inventory_items, zone_user_progress, devices.
- Mobile nunca cria eventos, zonas, produtos, categorias, barcodes, targets.
- Mobile pode registrar contagem fora do target (is_new_product=true).
- Server decide inclusao posterior.

---

## 10. Logging e auditoria
### 10.1 Client (outbox_local)
Campos minimos:
- table_name
- record_uuid
- operation
- attempts
- last_error
- created_at

### 10.2 Server (logging estruturado JSON)
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

## 11. Testabilidade (base para QA)
Cada entidade deve ter testes para:
- insert valido
- insert duplicado (idempotencia)
- FK invalida
- conflito de timestamp
- retry apos erro
- sync parcial com falha isolada

---

## 12. Pontos incoerentes ou incompletos (registro oficial)
1) Soft delete historico vs sync:
   - Regra atual diz deleted_at nao participa do sync.
   - Documentos anteriores exigiam pull de deleted_at.
   - Necessario alinhar: ou deleted_at participa do pull, ou is_active e unico mecanismo.

2) Operacoes permitidas em companies/users:
   - Matriz define update limitado em users, mas handlers anteriores permitem update amplo.
   - Necessario definir allowlist final e aplicar no backend.

3) Inventory_items e zone_user_progress:
   - Append-only declarado, mas ha fluxos de correcao.
   - Necessario definir se "correcao" e update permitido ou novo evento.

4) Origem desktop vs mobile:
   - Contrato define direcao, mas handlers nao validam origem.
   - Necessario enforcement no backend (role/device).

5) devices:
   - Soft delete via is_blocked aceito do client? definir quem pode bloquear.

---

## 13. Resumo do que falta
- Fechar decisao sobre deleted_at no pull (participa ou nao participa).
- Definir allowlists finais por entidade no backend (users, inventory_items, progress).
- Definir politica definitiva de correcao em inventory_items (update vs append-only).
- Definir validacao de origem (desktop/mobile) nos handlers.
- Definir regra de bloqueio de devices (quem pode setar is_blocked).
