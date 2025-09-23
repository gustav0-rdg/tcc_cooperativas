-- Remove o banco de dados, se existir
DROP DATABASE IF EXISTS recoopera;

-- Cria o banco de dados
CREATE DATABASE IF NOT EXISTS recoopera;
USE recoopera;

-- Tabela cooperativas
CREATE TABLE IF NOT EXISTS cooperativas (
    cnpj VARCHAR(14) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    salt_senha VARCHAR(255) DEFAULT (UUID())
);

-- Tabela compradores
CREATE TABLE IF NOT EXISTS compradores (
    cnpj VARCHAR(14) PRIMARY KEY,
    credibilidade INT NOT NULL,
    telefone VARCHAR(10),
    email VARCHAR(255)
);

-- Tabela categorias (antes da venda, pois será usada como FK)
CREATE TABLE IF NOT EXISTS categorias (
    categoria_id INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(30) NOT NULL
);

-- Tabela catador
CREATE TABLE IF NOT EXISTS catador (
    cpf VARCHAR(11) PRIMARY KEY,  -- Corrigido de 10 para 11
    cnpj_cooperativa VARCHAR(14) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    telefone VARCHAR(17),
    data_nascimento DATETIME NOT NULL,
    
    CONSTRAINT fk_catador_cooperativa
    FOREIGN KEY (cnpj_cooperativa) REFERENCES cooperativas(cnpj)
);

-- Tabela log
CREATE TABLE IF NOT EXISTS log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    cnpj_cooperativa VARCHAR(14) NOT NULL,
    acao VARCHAR(25) NOT NULL,
    descricao TEXT,
    data_log DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela endereco_comprador
CREATE TABLE IF NOT EXISTS endereco_comprador (
    endereco_comprador_id INT AUTO_INCREMENT PRIMARY KEY,
    cep VARCHAR(8) NOT NULL,
    logradouro VARCHAR(255) NOT NULL,
    bairro VARCHAR(255) NOT NULL,
    numero VARCHAR(255) NOT NULL,
    cidade VARCHAR(255) NOT NULL,
    uf VARCHAR(2) NOT NULL,
    complemento VARCHAR(255),
    cnpj_comprador VARCHAR(14) NOT NULL,
    
    FOREIGN KEY (cnpj_comprador) REFERENCES compradores(cnpj)
);

-- Tabela venda
CREATE TABLE IF NOT EXISTS venda (
    venda_id INT AUTO_INCREMENT PRIMARY KEY,

    cpf_catador_responsavel VARCHAR(11) NOT NULL,
    cnpj_cooperativa VARCHAR(14) NOT NULL,
    cnpj_comprador VARCHAR(14) NOT NULL,
    
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    quantidade_kg DECIMAL(10,2) NOT NULL,
    preco_kg DECIMAL(10,2) NOT NULL,
    
    avaliacao_pagamento TINYINT UNSIGNED NOT NULL,
    
    operacao_logistica VARCHAR(1024),
    consideracoes VARCHAR(1024),
    
    categoria INT NOT NULL,
    
    FOREIGN KEY (cpf_catador_responsavel) REFERENCES catador(cpf),
    FOREIGN KEY (cnpj_cooperativa) REFERENCES cooperativas(cnpj),
    FOREIGN KEY (cnpj_comprador) REFERENCES compradores(cnpj),
    FOREIGN KEY (categoria) REFERENCES categorias(categoria_id)
);