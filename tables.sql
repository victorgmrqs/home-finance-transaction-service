-- Active: 1759447390748@@127.0.0.1@5432@home_finance
-- ==============================================
-- Tabela: locais
-- ==============================================

CREATE TABLE IF NOT EXISTS locais (
    id SERIAL PRIMARY KEY,
    nome_fantasia VARCHAR(255),
    cnpj VARCHAR(18) UNIQUE,
    razao_social VARCHAR(255),
    categoria VARCHAR(100),
    endereco TEXT,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- ==============================================
-- Tabela: transacoes
-- ==============================================
CREATE TABLE IF NOT EXISTS transacoes (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    valor NUMERIC(12, 2) NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    categoria VARCHAR(100) NOT NULL,
    recorrencia VARCHAR(20) CHECK (
        recorrencia IN (
            'DIARIO',
            'SEMANAL',
            'MENSAL',
            'OCASIONAL'
        )
    ),
    parcelas INT,
    local_id INT REFERENCES locais (id) ON DELETE SET NULL,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes (data);

CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes (tipo);

CREATE INDEX IF NOT EXISTS idx_transacoes_categoria ON transacoes (categoria);

CREATE INDEX IF NOT EXISTS idx_transacoes_local_id ON transacoes (local_id);

-- ==============================================
DROP TABLE IF EXISTS locais;

DROP TABLE IF EXISTS transacoes;
-- ==============================================