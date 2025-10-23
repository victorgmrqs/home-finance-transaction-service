# 📊 Exemplos de API - Painéis

## Índice

- [Criar Painel](#criar-painel)
- [Listar Painéis](#listar-painéis)
- [Buscar Painel](#buscar-painel)
- [Atualizar Painel](#atualizar-painel)
- [Deletar Painel](#deletar-painel)
- [Compartilhar Painel](#compartilhar-painel)
- [Balanço do Painel](#balanço-do-painel)

---

## Criar Painel

### Painel de Cartão de Crédito

```bash
curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Cartão Nubank",
    "descricao": "Cartão de crédito principal",
    "tipo_conta": "CARTAO_CREDITO",
    "usuario_id": 1
  }'
```

**Resposta:**
```json
{
  "code": "PAINEL_CREATED",
  "message": "Painel criado com sucesso",
  "data": {
    "id": 1,
    "nome": "Cartão Nubank",
    "descricao": "Cartão de crédito principal",
    "tipo_conta": "CARTAO_CREDITO",
    "usuario_id": 1
  }
}
```

### Painel de Conta Bancária

```bash
curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Conta Corrente Inter",
    "descricao": "Conta salário e despesas fixas",
    "tipo_conta": "CONTA_BANCARIA",
    "usuario_id": 1
  }'
```

### Painel de Dinheiro

```bash
curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Carteira",
    "descricao": "Dinheiro em espécie",
    "tipo_conta": "DINHEIRO",
    "usuario_id": 1
  }'
```

---

## Listar Painéis

### Listar Todos os Painéis

```bash
curl -X GET "http://localhost:8000/api/v1/paineis" \
  -H "X-User-ID: 1"
```

### Listar Painéis de um Usuário

```bash
curl -X GET "http://localhost:8000/api/v1/usuarios/1/paineis" \
  -H "X-User-ID: 1"
```

### Filtrar por Nome

```bash
curl -X GET "http://localhost:8000/api/v1/paineis?nome=Nubank" \
  -H "X-User-ID: 1"
```

### Paginação

```bash
curl -X GET "http://localhost:8000/api/v1/paineis?limit=5&offset=0" \
  -H "X-User-ID: 1"
```

---

## Buscar Painel

```bash
curl -X GET http://localhost:8000/api/v1/paineis/1 \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "PAINEL_DETAIL_SUCCESS",
  "message": "Painel encontrado",
  "data": {
    "id": 1,
    "nome": "Cartão Nubank",
    "descricao": "Cartão de crédito principal",
    "tipo_conta": "CARTAO_CREDITO",
    "usuario_id": 1
  }
}
```

---

## Atualizar Painel

### Atualizar Nome e Descrição

```bash
curl -X PUT http://localhost:8000/api/v1/paineis/1 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Cartão Nubank Platinium",
    "descricao": "Cartão de crédito principal com cashback"
  }'
```

### Atualizar Apenas Nome

```bash
curl -X PUT http://localhost:8000/api/v1/paineis/1 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Nubank"
  }'
```

---

## Deletar Painel

```bash
curl -X DELETE http://localhost:8000/api/v1/paineis/1 \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "PAINEL_DELETED",
  "message": "Painel removido com sucesso",
  "data": null
}
```

---

## Compartilhar Painel

### Compartilhar com Permissão de Visualização (VIEWER)

```bash
curl -X POST http://localhost:8000/api/v1/paineis/1/compartilhar \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "usuario_id": 2,
    "tipo_permissao": "VIEWER"
  }'
```

**Resposta:**
```json
{
  "code": "PAINEL_COMPARTILHADO",
  "message": "Painel compartilhado com sucesso",
  "data": {
    "id": 1,
    "painel_id": 1,
    "usuario_id": 2,
    "tipo_permissao": "VIEWER",
    "criado_em": "2025-10-22T10:30:00.000Z",
    "atualizado_em": "2025-10-22T10:30:00.000Z"
  }
}
```

### Compartilhar com Permissão de Edição (EDITOR)

```bash
curl -X POST http://localhost:8000/api/v1/paineis/1/compartilhar \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "usuario_id": 3,
    "tipo_permissao": "EDITOR"
  }'
```

### Compartilhar como Co-proprietário (OWNER)

```bash
curl -X POST http://localhost:8000/api/v1/paineis/1/compartilhar \
  -H "Content-Type: application/json" \
  -H "X-User-ID": 1" \
  -d '{
    "usuario_id": 4,
    "tipo_permissao": "OWNER"
  }'
```

### Listar Compartilhamentos

```bash
curl -X GET http://localhost:8000/api/v1/paineis/1/compartilhamentos \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "COMPARTILHAMENTOS_LISTADOS",
  "message": "Compartilhamentos listados com sucesso",
  "data": [
    {
      "id": 1,
      "painel_id": 1,
      "usuario_id": 2,
      "tipo_permissao": "VIEWER",
      "criado_em": "2025-10-22T10:30:00.000Z",
      "atualizado_em": "2025-10-22T10:30:00.000Z"
    },
    {
      "id": 2,
      "painel_id": 1,
      "usuario_id": 3,
      "tipo_permissao": "EDITOR",
      "criado_em": "2025-10-22T10:35:00.000Z",
      "atualizado_em": "2025-10-22T10:35:00.000Z"
    }
  ]
}
```

### Atualizar Permissão

```bash
# Promover de VIEWER para EDITOR
curl -X PUT http://localhost:8000/api/v1/paineis/1/compartilhamentos/2 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "tipo_permissao": "EDITOR"
  }'
```

### Remover Compartilhamento

```bash
curl -X DELETE http://localhost:8000/api/v1/paineis/1/compartilhamentos/2 \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "COMPARTILHAMENTO_REMOVIDO",
  "message": "Compartilhamento removido com sucesso",
  "data": null
}
```

---

## Balanço do Painel

### Balanço Geral (Todos os Tempos)

```bash
curl -X GET http://localhost:8000/api/v1/paineis/1/balanco \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "BALANCO_CALCULADO",
  "message": "Balanço calculado com sucesso",
  "data": {
    "painel_id": 1,
    "nome_painel": "Cartão Nubank",
    "periodo_inicio": null,
    "periodo_fim": null,
    "total_entradas": 6500.00,
    "total_saidas": 2850.50,
    "saldo": 3649.50,
    "quantidade_transacoes": 42
  }
}
```

### Balanço do Mês Atual

```bash
curl -X GET "http://localhost:8000/api/v1/paineis/1/balanco?data_inicio=2025-10-01&data_fim=2025-10-31" \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "BALANCO_CALCULADO",
  "message": "Balanço calculado com sucesso",
  "data": {
    "painel_id": 1,
    "nome_painel": "Cartão Nubank",
    "periodo_inicio": "2025-10-01",
    "periodo_fim": "2025-10-31",
    "total_entradas": 6500.00,
    "total_saidas": 1250.00,
    "saldo": 5250.00,
    "quantidade_transacoes": 15
  }
}
```

### Balanço do Ano

```bash
curl -X GET "http://localhost:8000/api/v1/paineis/1/balanco?data_inicio=2025-01-01&data_fim=2025-12-31" \
  -H "X-User-ID: 1"
```

### Balanço dos Últimos 30 Dias

```bash
# Calcular data dinamicamente (exemplo com date no Linux)
DATA_INICIO=$(date -d "30 days ago" +%Y-%m-%d)
DATA_FIM=$(date +%Y-%m-%d)

curl -X GET "http://localhost:8000/api/v1/paineis/1/balanco?data_inicio=$DATA_INICIO&data_fim=$DATA_FIM" \
  -H "X-User-ID: 1"
```

---

## Casos de Uso Comuns

### 1. Organizar Finanças por Cartão

```bash
# Criar painel para cada cartão
curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Cartão Nubank",
    "tipo_conta": "CARTAO_CREDITO",
    "usuario_id": 1
  }'

curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Cartão Inter",
    "tipo_conta": "CARTAO_CREDITO",
    "usuario_id": 1
  }'
```

### 2. Compartilhar Painel Familiar

```bash
# Criar painel compartilhado
curl -X POST http://localhost:8000/api/v1/paineis \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "nome": "Despesas Casal",
    "descricao": "Gastos compartilhados do casal",
    "tipo_conta": "CONTA_BANCARIA",
    "usuario_id": 1
  }'

# Compartilhar com cônjuge (permissão total)
curl -X POST http://localhost:8000/api/v1/paineis/5/compartilhar \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "usuario_id": 2,
    "tipo_permissao": "OWNER"
  }'
```

### 3. Ver Gastos do Mês por Painel

```bash
# Balanço do painel no mês
curl -X GET "http://localhost:8000/api/v1/paineis/1/balanco?data_inicio=2025-10-01&data_fim=2025-10-31" \
  -H "X-User-ID: 1"

# Transações detalhadas
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&data_inicio=2025-10-01&data_fim=2025-10-31&tipo=SAIDA" \
  -H "X-User-ID: 1"
```

---

## Usando com Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json", "X-User-ID": "1"}

# Criar painel
response = requests.post(
    f"{BASE_URL}/paineis",
    headers=HEADERS,
    json={
        "nome": "Meu Cartão",
        "tipo_conta": "CARTAO_CREDITO",
        "usuario_id": 1
    }
)
painel = response.json()["data"]
print(f"Painel criado: {painel['id']}")

# Ver balanço
response = requests.get(
    f"{BASE_URL}/paineis/{painel['id']}/balanco",
    headers=HEADERS
)
balanco = response.json()["data"]
print(f"Saldo: R$ {balanco['saldo']}")
```

---

**Última Atualização:** 2025-10-22
**Endpoints Base:** `/api/v1/paineis`, `/api/v1/paineis/{id}/compartilhar`, `/api/v1/paineis/{id}/balanco`
