# 💰 Exemplos de API - Transações

## Índice

- [Criar Transação](#criar-transação)
- [Listar Transações](#listar-transações)
- [Buscar Transação por ID](#buscar-transação-por-id)
- [Atualizar Transação](#atualizar-transação)
- [Deletar Transação](#deletar-transação)
- [Casos de Uso Comuns](#casos-de-uso-comuns)

---

## Criar Transação

### Transação Simples (Saída)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Supermercado Compra Semanal",
    "valor": 285.50,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "painel_id": 1
  }'
```

**Resposta:**
```json
{
  "code": "TRANSACTION_CREATED",
  "message": "Transação criada com sucesso",
  "data": {
    "id": 1,
    "data": "2025-10-22",
    "descricao": "Supermercado Compra Semanal",
    "valor": 285.5,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "recorrencia": null,
    "parcelas": null,
    "tipo_divisao": "PESSOAL",
    "valor_por_pessoa": null,
    "porcentagem_divisao": null,
    "local_id": null,
    "painel_id": 1
  }
}
```

### Transação de Entrada (Receita)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-01",
    "descricao": "Salário Outubro",
    "valor": 5500.00,
    "tipo": "ENTRADA",
    "categoria": "Salário",
    "recorrencia": "MENSAL",
    "painel_id": 1
  }'
```

### Transação Parcelada

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Notebook Dell Inspiron",
    "valor": 3600.00,
    "tipo": "SAIDA",
    "categoria": "Eletrônicos",
    "parcelas": 12,
    "painel_id": 1
  }'
```

### Gasto Compartilhado 50/50

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Jantar Restaurante Italiano",
    "valor": 180.00,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "tipo_divisao": "COMPARTILHADO_50_50",
    "valor_por_pessoa": 90.00,
    "painel_id": 1
  }'
```

### Gasto Compartilhado Customizado (60/40)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Conta de Luz Apartamento",
    "valor": 150.00,
    "tipo": "SAIDA",
    "categoria": "Utilidades",
    "tipo_divisao": "COMPARTILHADO_CUSTOM",
    "valor_por_pessoa": 90.00,
    "porcentagem_divisao": 60,
    "painel_id": 1
  }'
```

### Transação com Local

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Compra Pão e Leite",
    "valor": 12.50,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "recorrencia": "DIARIO",
    "local_id": 5,
    "painel_id": 1
  }'
```

---

## Listar Transações

### Listar Todas (Paginação Padrão)

```bash
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1" \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "TRANSACTION_LIST_SUCCESS",
  "message": "Lista de transações obtida com sucesso",
  "data": [
    {
      "id": 10,
      "data": "2025-10-22",
      "descricao": "Conta de Luz",
      "valor": 150.0,
      "tipo": "SAIDA",
      "categoria": "Utilidades",
      "recorrencia": null,
      "parcelas": null,
      "tipo_divisao": "COMPARTILHADO_CUSTOM",
      "valor_por_pessoa": 90.0,
      "porcentagem_divisao": 60,
      "local_id": null,
      "painel_id": 1
    }
    // ... mais transações
  ]
}
```

### Filtrar por Período

```bash
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&data_inicio=2025-10-01&data_fim=2025-10-31" \
  -H "X-User-ID: 1"
```

### Filtrar por Tipo

```bash
# Apenas saídas
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=SAIDA" \
  -H "X-User-ID: 1"

# Apenas entradas
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=ENTRADA" \
  -H "X-User-ID: 1"
```

### Filtrar por Categoria

```bash
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&categoria=Alimentação" \
  -H "X-User-ID: 1"
```

### Buscar por Descrição

```bash
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&descricao=supermercado" \
  -H "X-User-ID: 1"
```

### Paginação Customizada

```bash
# 10 resultados por página, página 2
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&page=2&page_size=10" \
  -H "X-User-ID: 1"

# 100 resultados (máximo permitido)
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&page_size=100" \
  -H "X-User-ID: 1"
```

### Filtros Combinados

```bash
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=SAIDA&categoria=Alimentação&data_inicio=2025-10-01&data_fim=2025-10-31&page_size=20" \
  -H "X-User-ID: 1"
```

---

## Buscar Transação por ID

```bash
curl -X GET http://localhost:8000/api/v1/transactions/10 \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "TRANSACTION_DETAIL_SUCCESS",
  "message": "Transação encontrada",
  "data": {
    "id": 10,
    "data": "2025-10-22",
    "descricao": "Conta de Luz Apartamento",
    "valor": 150.0,
    "tipo": "SAIDA",
    "categoria": "Utilidades",
    "recorrencia": null,
    "parcelas": null,
    "tipo_divisao": "COMPARTILHADO_CUSTOM",
    "valor_por_pessoa": 90.0,
    "porcentagem_divisao": 60,
    "local_id": null,
    "painel_id": 1
  }
}
```

---

## Atualizar Transação

### Atualizar Descrição e Valor

```bash
curl -X PUT http://localhost:8000/api/v1/transactions/10 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "descricao": "Conta de Luz Apartamento - Outubro",
    "valor": 165.00
  }'
```

### Alterar Tipo de Divisão

```bash
# Mudar de PESSOAL para COMPARTILHADO_50_50
curl -X PUT http://localhost:8000/api/v1/transactions/5 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "tipo_divisao": "COMPARTILHADO_50_50",
    "valor_por_pessoa": 50.00
  }'
```

### Atualização Completa

```bash
curl -X PUT http://localhost:8000/api/v1/transactions/10 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-23",
    "descricao": "Conta de Luz Revisada",
    "valor": 155.00,
    "tipo": "SAIDA",
    "categoria": "Contas",
    "tipo_divisao": "COMPARTILHADO_50_50",
    "valor_por_pessoa": 77.50
  }'
```

---

## Deletar Transação

```bash
curl -X DELETE http://localhost:8000/api/v1/transactions/10 \
  -H "X-User-ID: 1"
```

**Resposta:**
```json
{
  "code": "TRANSACTION_DELETED",
  "message": "Transação removida com sucesso",
  "data": null
}
```

---

## Casos de Uso Comuns

### 1. Registrar Compra no Supermercado

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-22",
    "descricao": "Supermercado Extra - Compras da Semana",
    "valor": 320.50,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "local_id": 3,
    "painel_id": 1
  }'
```

### 2. Pagar Conta Compartilhada (Aluguel)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-05",
    "descricao": "Aluguel Outubro 2025",
    "valor": 1800.00,
    "tipo": "SAIDA",
    "categoria": "Moradia",
    "recorrencia": "MENSAL",
    "tipo_divisao": "COMPARTILHADO_50_50",
    "valor_por_pessoa": 900.00,
    "painel_id": 1
  }'
```

### 3. Compra Parcelada (Celular)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-15",
    "descricao": "iPhone 15 Pro - Apple Store",
    "valor": 7200.00,
    "tipo": "SAIDA",
    "categoria": "Eletrônicos",
    "parcelas": 10,
    "local_id": 8,
    "painel_id": 1
  }'
```

### 4. Receber Salário

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-01",
    "descricao": "Salário - Empresa XYZ",
    "valor": 6500.00,
    "tipo": "ENTRADA",
    "categoria": "Salário",
    "recorrencia": "MENSAL",
    "painel_id": 1
  }'
```

### 5. Jantar Dividido com Amigos (Customizado)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "data": "2025-10-20",
    "descricao": "Jantar Aniversário - Restaurante Le Bistro",
    "valor": 450.00,
    "tipo": "SAIDA",
    "categoria": "Alimentação",
    "tipo_divisao": "COMPARTILHADO_CUSTOM",
    "valor_por_pessoa": 270.00,
    "porcentagem_divisao": 60,
    "local_id": 12,
    "painel_id": 1
  }'
```

### 6. Listar Gastos do Mês Atual

```bash
# Assumindo outubro/2025
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=SAIDA&data_inicio=2025-10-01&data_fim=2025-10-31&page_size=100" \
  -H "X-User-ID: 1"
```

### 7. Ver Receitas vs Despesas

```bash
# Receitas
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=ENTRADA&data_inicio=2025-10-01&data_fim=2025-10-31" \
  -H "X-User-ID: 1"

# Despesas
curl -X GET "http://localhost:8000/api/v1/transactions?painel_id=1&tipo=SAIDA&data_inicio=2025-10-01&data_fim=2025-10-31" \
  -H "X-User-ID: 1"
```

---

## Usando com Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "X-User-ID": "1"
}

# Criar transação
response = requests.post(
    f"{BASE_URL}/transactions",
    headers=HEADERS,
    json={
        "data": "2025-10-22",
        "descricao": "Compra Teste",
        "valor": 100.00,
        "tipo": "SAIDA",
        "categoria": "Teste",
        "painel_id": 1
    }
)

print(response.json())

# Listar transações
response = requests.get(
    f"{BASE_URL}/transactions",
    headers=HEADERS,
    params={"painel_id": 1, "page_size": 10}
)

for transaction in response.json()["data"]:
    print(f"{transaction['descricao']}: R$ {transaction['valor']}")
```

---

## Usando com JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";
const HEADERS = {
  "Content-Type": "application/json",
  "X-User-ID": "1"
};

// Criar transação
async function criarTransacao() {
  const response = await fetch(`${BASE_URL}/transactions`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      data: "2025-10-22",
      descricao: "Compra Teste JS",
      valor: 150.00,
      tipo: "SAIDA",
      categoria: "Teste",
      painel_id: 1
    })
  });

  const data = await response.json();
  console.log(data);
}

// Listar transações
async function listarTransacoes() {
  const params = new URLSearchParams({
    painel_id: 1,
    page_size: 10
  });

  const response = await fetch(`${BASE_URL}/transactions?${params}`, {
    headers: HEADERS
  });

  const data = await response.json();
  data.data.forEach(t => {
    console.log(`${t.descricao}: R$ ${t.valor}`);
  });
}
```

---

**Última Atualização:** 2025-10-22
**Endpoint Base:** `/api/v1/transactions`
