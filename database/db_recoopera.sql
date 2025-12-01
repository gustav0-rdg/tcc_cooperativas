DROP DATABASE IF EXISTS `recoopera`;
CREATE DATABASE IF NOT EXISTS `recoopera`
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
USE `recoopera`;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
SET NAMES 'utf8mb4';
SET GLOBAL event_scheduler = ON;

-- ====================================================
-- AUTENTICAÇÃO E USUÁRIOS
-- ====================================================
CREATE TABLE usuarios (
  id_usuario BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(200) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  senha_hash VARCHAR(255) NOT NULL COMMENT 'Hash SHA-256 da senha',
  tipo ENUM('root','gestor','cooperativa','cooperado') NOT NULL,
  status ENUM('ativo','inativo','bloqueado','pendente','reprovado') NOT NULL DEFAULT 'pendente',
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultima_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_tipo_status (tipo, status)
) ENGINE=InnoDB COMMENT='Tabela central de usuários do sistema';

CREATE TABLE tokens_validacao (
  id_token BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario BIGINT UNSIGNED NOT NULL,
  token VARCHAR(255) NOT NULL UNIQUE,
  tipo ENUM('sessao','recuperacao_senha','validacao_email') NOT NULL,
  usado BOOLEAN NOT NULL DEFAULT FALSE,
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_expiracao DATETIME NOT NULL,
  ip_origem VARCHAR(45) NULL COMMENT 'IP de onde o token foi gerado',
  INDEX idx_token (token),
  INDEX idx_usuario_tipo (id_usuario, tipo),
  INDEX idx_expiracao (data_expiracao),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Tokens para sessões e recuperação de senha';

-- ====================================================
-- COOPERATIVAS
-- ====================================================
CREATE TABLE cooperativas (
  id_cooperativa BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario BIGINT UNSIGNED NOT NULL UNIQUE,
  cnpj CHAR(14) NOT NULL UNIQUE,
  razao_social VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255),
  email_contato VARCHAR(255),
  telefone VARCHAR(20),
  whatsapp VARCHAR(20),
  site VARCHAR(255),
  cep VARCHAR(9),
  logradouro VARCHAR(255),
  numero VARCHAR(20),
  complemento VARCHAR(100),
  bairro VARCHAR(100),
  cidade VARCHAR(100) NOT NULL,
  estado CHAR(2) NOT NULL,
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultima_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  ultima_atividade DATETIME NULL COMMENT 'Última vez que registrou venda',
  deletado_em DATETIME NULL,
  INDEX idx_cnpj (cnpj),
  INDEX idx_localizacao (estado, cidade),
  INDEX idx_ultima_atividade (ultima_atividade),
  INDEX idx_status_usuario (id_usuario),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Dados das cooperativas cadastradas';

CREATE TABLE documentos_cooperativas (
  id_documento BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  tipo_documento VARCHAR(50) NOT NULL COMMENT 'Ex: estatuto, ata, cnpj',
  nome_arquivo_original VARCHAR(255) NOT NULL,
  nome_arquivo_armazenado VARCHAR(255) NOT NULL UNIQUE,
  caminho_completo VARCHAR(500) NOT NULL,
  tamanho_bytes BIGINT UNSIGNED NOT NULL,
  data_upload DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('pendente','aceito','negado') NOT NULL DEFAULT 'pendente',
  motivo_rejeicao TEXT NULL,
  avaliado_por BIGINT UNSIGNED NULL,
  data_avaliacao DATETIME NULL,
  INDEX idx_cooperativa_status (id_cooperativa, status),
  INDEX idx_tipo (tipo_documento),
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE,
  FOREIGN KEY (avaliado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Documentos enviados pelas cooperativas';

-- ====================================================
-- COOPERADOS
-- ====================================================
CREATE TABLE cooperados (
  id_cooperado BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario BIGINT UNSIGNED NOT NULL UNIQUE,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  cpf CHAR(11) NOT NULL UNIQUE,
  data_vinculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cooperativa (id_cooperativa),
  INDEX idx_cpf (cpf),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Cooperados vinculados às cooperativas';

-- ====================================================
-- COMPRADORES
-- ====================================================
CREATE TABLE compradores (
  id_comprador BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  cnpj CHAR(14) NOT NULL UNIQUE,
  razao_social VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255),
  email VARCHAR(255),
  telefone VARCHAR(20),
  whatsapp VARCHAR(20),
  cep VARCHAR(9),
  logradouro VARCHAR(255),
  numero VARCHAR(20),
  complemento VARCHAR(100),
  bairro VARCHAR(100),
  cidade VARCHAR(100),
  estado CHAR(2),
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultima_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  deletado_em DATETIME NULL,
  score_confianca DECIMAL(4,2) NOT NULL DEFAULT 2.50 COMMENT 'Score de 0 a 5',
  numero_avaliacoes INT UNSIGNED NOT NULL DEFAULT 0,
  INDEX idx_cnpj (cnpj),
  INDEX idx_localizacao (estado, cidade),
  INDEX idx_score (score_confianca DESC)
) ENGINE=InnoDB COMMENT='Compradores de materiais recicláveis';

-- ====================================================
-- MATERIAIS
-- ====================================================
CREATE TABLE materiais_base (
  id_material_base BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL UNIQUE,
  descricao TEXT NULL,
  icone VARCHAR(50) NULL COMMENT 'Nome do ícone para exibição',
  ordem_exibicao TINYINT UNSIGNED NOT NULL DEFAULT 0,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  INDEX idx_ativo_ordem (ativo, ordem_exibicao)
) ENGINE=InnoDB COMMENT='Categorias principais de materiais';

CREATE TABLE materiais_catalogo (
  id_material_catalogo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_material_base BIGINT UNSIGNED NOT NULL,
  nome_especifico VARCHAR(100) NOT NULL,
  descricao TEXT NULL,
  id_cooperativa_criadora BIGINT UNSIGNED NULL COMMENT 'Cooperativa que sugeriu',
  status ENUM('aprovado','inativo') NOT NULL DEFAULT 'aprovado',
  aprovado_por BIGINT UNSIGNED NULL,
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_aprovacao DATETIME NULL,
  deletado_em DATETIME NULL,
  UNIQUE INDEX uidx_base_nome (id_material_base, nome_especifico),
  INDEX idx_base_status (id_material_base, status),
  FOREIGN KEY (id_material_base) REFERENCES materiais_base(id_material_base) ON DELETE RESTRICT,
  FOREIGN KEY (id_cooperativa_criadora) REFERENCES cooperativas(id_cooperativa) ON DELETE SET NULL,
  FOREIGN KEY (aprovado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Materiais específicos aprovados (catálogo global)';

CREATE TABLE materiais_especificos_pendentes (
  id_material_pendente BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_material_base BIGINT UNSIGNED NOT NULL,
  nome_especifico VARCHAR(100) NOT NULL,
  descricao TEXT NULL,
  id_cooperativa_criadora BIGINT UNSIGNED NOT NULL,
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('pendente','aprovado','reprovado') NOT NULL DEFAULT 'pendente',
  motivo_rejeicao TEXT NULL,
  avaliado_por BIGINT UNSIGNED NULL,
  data_avaliacao DATETIME NULL,
  UNIQUE INDEX uidx_base_nome_coop (id_material_base, nome_especifico, id_cooperativa_criadora),
  INDEX idx_status (status),
  FOREIGN KEY (id_material_base) REFERENCES materiais_base(id_material_base) ON DELETE RESTRICT,
  FOREIGN KEY (id_cooperativa_criadora) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE,
  FOREIGN KEY (avaliado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Materiais aguardando aprovação de gestores';

CREATE TABLE materiais_sinonimos (
  id_sinonimo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_material_catalogo BIGINT UNSIGNED NOT NULL,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  nome_sinonimo VARCHAR(100) NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_inativacao DATETIME NULL,
  UNIQUE INDEX uidx_coop_material (id_cooperativa, id_material_catalogo),
  UNIQUE INDEX uidx_coop_sinonimo (id_cooperativa, nome_sinonimo),
  INDEX idx_ativo (ativo),
  FOREIGN KEY (id_material_catalogo) REFERENCES materiais_catalogo(id_material_catalogo) ON DELETE CASCADE,
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Sinônimos personalizados por cooperativa';

-- ====================================================
-- VENDAS E TRANSAÇÕES
-- ====================================================
CREATE TABLE vendas (
  id_venda BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  id_comprador BIGINT UNSIGNED NOT NULL,
  valor_total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  data_venda DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  nf_xml_nome_arquivo VARCHAR(255) NULL,
  nf_xml_caminho VARCHAR(500) NULL,
  nf_numero VARCHAR(50) NULL,
  nf_serie VARCHAR(10) NULL,
  editavel_ate DATETIME NULL COMMENT 'Prazo para edição (24h após criação)',
  observacoes TEXT NULL,
  INDEX idx_cooperativa_data (id_cooperativa, data_venda DESC),
  INDEX idx_comprador_data (id_comprador, data_venda DESC),
  INDEX idx_data_venda (data_venda DESC),
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE RESTRICT,
  FOREIGN KEY (id_comprador) REFERENCES compradores(id_comprador) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Registro de vendas realizadas';

CREATE TABLE vendas_itens (
  id_venda_item BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_venda BIGINT UNSIGNED NOT NULL,
  id_material_catalogo BIGINT UNSIGNED NOT NULL,
  quantidade_kg DECIMAL(12,3) NOT NULL,
  preco_por_kg DECIMAL(12,4) NOT NULL,
  total_item DECIMAL(14,2) NOT NULL,
  INDEX idx_venda (id_venda),
  INDEX idx_material (id_material_catalogo),
  INDEX idx_venda_material (id_venda, id_material_catalogo),
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
  FOREIGN KEY (id_material_catalogo) REFERENCES materiais_catalogo(id_material_catalogo) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Itens individuais de cada venda';

-- ====================================================
-- AVALIAÇÕES E FEEDBACK
-- ====================================================
CREATE TABLE feedback_tags (
  id_feedback_tag BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  texto VARCHAR(100) NOT NULL UNIQUE,
  tipo ENUM('positivo','negativo') NOT NULL,
  categoria VARCHAR(50) NULL COMMENT 'Ex: pagamento, logística, comunicação',
  ordem_exibicao TINYINT UNSIGNED NOT NULL DEFAULT 0,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  INDEX idx_tipo_ativo (tipo, ativo),
  INDEX idx_categoria (categoria)
) ENGINE=InnoDB COMMENT='Tags predefinidas para feedback rápido';

CREATE TABLE avaliacoes_compradores (
  id_avaliacao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_venda BIGINT UNSIGNED NOT NULL UNIQUE,
  id_comprador BIGINT UNSIGNED NOT NULL,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  score TINYINT UNSIGNED NOT NULL CHECK (score BETWEEN 0 AND 5),
  modelo_carregamento ENUM('cooperativa','comprador') NULL,
  padronizacao_fardo BOOLEAN NULL,
  tipo_material_fardo VARCHAR(100) NULL,
  aceita_granel BOOLEAN NULL,
  quem_paga_frete ENUM('cooperativa','comprador') NULL,
  prazo_pagamento_dias TINYINT UNSIGNED NULL,
  desconta_contaminantes BOOLEAN NULL,
  comentario_livre TEXT NULL,
  data_avaliacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_comprador_score (id_comprador, score),
  INDEX idx_cooperativa (id_cooperativa),
  INDEX idx_data (data_avaliacao DESC),
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
  FOREIGN KEY (id_comprador) REFERENCES compradores(id_comprador) ON DELETE RESTRICT,
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Avaliações detalhadas de compradores';

CREATE TABLE avaliacao_feedback_selecionado (
  id_avaliacao BIGINT UNSIGNED NOT NULL,
  id_feedback_tag BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (id_avaliacao, id_feedback_tag),
  FOREIGN KEY (id_avaliacao) REFERENCES avaliacoes_compradores(id_avaliacao) ON DELETE CASCADE,
  FOREIGN KEY (id_feedback_tag) REFERENCES feedback_tags(id_feedback_tag) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Tags selecionadas em cada avaliação';

CREATE TABLE avaliacoes_pendentes (
  id_avaliacao_pendente BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_venda BIGINT UNSIGNED NOT NULL UNIQUE,
  id_cooperativa BIGINT UNSIGNED NOT NULL,
  status_avaliacao ENUM('pendente','concluida','expirada') NOT NULL DEFAULT 'pendente',
  data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_conclusao DATETIME NULL,
  INDEX idx_cooperativa_status (id_cooperativa, status_avaliacao),
  INDEX idx_status_data (status_avaliacao, data_criacao),
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
  FOREIGN KEY (id_cooperativa) REFERENCES cooperativas(id_cooperativa) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Controle de avaliações pendentes';

-- ====================================================
-- ANÁLISE DE PREÇOS E MERCADO
-- ====================================================
CREATE TABLE precos_regionais (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_material_catalogo BIGINT UNSIGNED NOT NULL,
  regiao VARCHAR(100) NOT NULL COMMENT 'Estado ou região',
  preco_medio DECIMAL(12,4) NOT NULL,
  preco_minimo DECIMAL(12,4) NOT NULL,
  preco_maximo DECIMAL(12,4) NOT NULL,
  desvio_padrao DECIMAL(10,4) NOT NULL,
  numero_transacoes INT UNSIGNED NOT NULL,
  periodo_analise VARCHAR(20) NOT NULL COMMENT 'Ex: 2025-Q1, 2025-01',
  data_atualizacao DATETIME NOT NULL,
  UNIQUE INDEX uidx_material_regiao_periodo (id_material_catalogo, regiao, periodo_analise),
  INDEX idx_regiao_data (regiao, data_atualizacao DESC),
  FOREIGN KEY (id_material_catalogo) REFERENCES materiais_catalogo(id_material_catalogo) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Análise de preços por região e período';

CREATE TABLE historico_score (
  id_hist BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_comprador BIGINT UNSIGNED NOT NULL,
  score_calculado DECIMAL(4,2) NOT NULL,
  numero_avaliacoes INT UNSIGNED NOT NULL,
  detalhe_json JSON NULL COMMENT 'Detalhes do cálculo',
  data_calculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_comprador_data (id_comprador, data_calculo DESC),
  FOREIGN KEY (id_comprador) REFERENCES compradores(id_comprador) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Histórico de alterações no score dos compradores';

-- ====================================================
-- CONFIGURAÇÕES E AUDITORIA
-- ====================================================
CREATE TABLE config_sistema (
  chave VARCHAR(100) PRIMARY KEY,
  valor VARCHAR(200) NOT NULL,
  tipo_valor ENUM('string','int','float','boolean','json') NOT NULL DEFAULT 'string',
  descricao TEXT NULL,
  editavel BOOLEAN NOT NULL DEFAULT TRUE,
  data_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='Configurações globais do sistema';

CREATE TABLE audit_log (
  id_log BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tabela_afetada VARCHAR(100) NOT NULL,
  id_registro_afetado VARCHAR(255) NOT NULL,
  acao ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  detalhes_antigos_json JSON NULL,
  detalhes_novos_json JSON NULL,
  usuario_responsavel VARCHAR(255) NULL,
  ip_origem VARCHAR(45) NULL,
  timestamp_acao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_tabela_acao (tabela_afetada, acao),
  INDEX idx_timestamp (timestamp_acao DESC),
  INDEX idx_usuario (usuario_responsavel)
) ENGINE=InnoDB COMMENT='Log de auditoria de todas as operações críticas';

DELIMITER $$

-- ----------------------------------------------------------------------------
-- PROCEDURES 
-- ----------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS SP_VALIDAR_CNPJ_COOPERATIVA$$
CREATE PROCEDURE SP_VALIDAR_CNPJ_COOPERATIVA(
    IN p_cnpj CHAR(14),
    OUT p_valido BOOLEAN,
    OUT p_mensagem VARCHAR(255)
)
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count FROM cooperativas WHERE cnpj = p_cnpj;
    
    IF v_count > 0 THEN
       SET p_valido = FALSE;
       SET p_mensagem = 'CNPJ já cadastrado no sistema';
    ELSE
       IF LENGTH(p_cnpj) = 14 AND p_cnpj REGEXP '^[0-9]{14}' THEN
          SET p_valido = TRUE;
          SET p_mensagem = 'CNPJ válido';
       ELSE
          SET p_valido = FALSE;
          SET p_mensagem = 'CNPJ com formato inválido (deve conter 14 dígitos)';
       END IF;
    END IF;
END$$

DROP PROCEDURE IF EXISTS SP_CRIAR_SINONIMO_MATERIAL$$
CREATE PROCEDURE SP_CRIAR_SINONIMO_MATERIAL(
   IN p_id_cooperativa BIGINT,
   IN p_id_material_catalogo BIGINT,
   IN p_nome_sinonimo VARCHAR(100)
)
BEGIN
   DECLARE v_existe INT;
   SELECT COUNT(*) INTO v_existe FROM materiais_sinonimos
   WHERE id_cooperativa = p_id_cooperativa AND nome_sinonimo = p_nome_sinonimo AND ativo = TRUE;
     
   IF v_existe > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Já existe sinônimo com esse nome para sua cooperativa';
   END IF;
     
   INSERT INTO materiais_sinonimos (id_material_catalogo, id_cooperativa, nome_sinonimo, ativo, data_criacao) 
   VALUES (p_id_material_catalogo, p_id_cooperativa, p_nome_sinonimo, TRUE, NOW())
   ON DUPLICATE KEY UPDATE nome_sinonimo = p_nome_sinonimo, ativo = TRUE, data_inativacao = NULL;
      
   SELECT LAST_INSERT_ID() AS id_sinonimo, 'Sinônimo criado com sucesso' AS mensagem;
END$$

DROP PROCEDURE IF EXISTS SP_SOLICITAR_NOVO_MATERIAL$$
CREATE PROCEDURE SP_SOLICITAR_NOVO_MATERIAL(
   IN p_id_cooperativa BIGINT,
   IN p_id_material_base BIGINT,
   IN p_nome_especifico VARCHAR(100),
   IN p_descricao TEXT
)
BEGIN
   DECLARE v_existe INT;
   
   SELECT COUNT(*) INTO v_existe FROM materiais_catalogo
   WHERE id_material_base = p_id_material_base AND nome_especifico = p_nome_especifico AND status = 'aprovado';
     
   IF v_existe > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Material já existe no catálogo global';
   END IF;
   
   SELECT COUNT(*) INTO v_existe FROM materiais_especificos_pendentes
   WHERE id_material_base = p_id_material_base AND nome_especifico = p_nome_especifico 
     AND id_cooperativa_criadora = p_id_cooperativa AND status = 'pendente';
     
   IF v_existe > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Você já possui uma solicitação pendente para este material';
   END IF;
     
   INSERT INTO materiais_especificos_pendentes (
      id_material_base, nome_especifico, descricao, id_cooperativa_criadora, status, data_criacao
   ) VALUES (
      p_id_material_base, p_nome_especifico, p_descricao, p_id_cooperativa, 'pendente', NOW()
   );
     
   SELECT LAST_INSERT_ID() AS id_material_pendente, 'Solicitação enviada para aprovação' AS mensagem;
END$$

DROP PROCEDURE IF EXISTS SP_BUSCAR_COMPRADORES_PROXIMOS$$
CREATE PROCEDURE SP_BUSCAR_COMPRADORES_PROXIMOS(
   IN p_id_cooperativa BIGINT,
   IN p_raio_km FLOAT,
   IN p_id_material_catalogo BIGINT
)
BEGIN
   DECLARE v_lat DECIMAL(10,8);
   DECLARE v_lon DECIMAL(11,8);
   
   SELECT latitude, longitude INTO v_lat, v_lon FROM cooperativas WHERE id_cooperativa = p_id_cooperativa;
   
   IF v_lat IS NULL OR v_lon IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cooperativa sem coordenadas cadastradas';
   END IF;
   
   SELECT 
      c.id_comprador, c.cnpj, c.razao_social, c.nome_fantasia,
      c.cidade, c.estado, c.telefone, c.email, c.whatsapp,
      c.score_confianca, c.numero_avaliacoes,
      FN_CALCULAR_DISTANCIA(v_lat, v_lon, c.latitude, c.longitude) AS distancia_km,
      COUNT(DISTINCT v.id_venda) AS total_vendas,
      COALESCE(SUM(v.valor_total), 0) AS valor_total_comprado,
      COUNT(DISTINCT v.id_cooperativa) AS num_cooperativas_distintas,
      MAX(v.data_venda) AS ultima_compra
   FROM compradores c
   LEFT JOIN vendas v ON c.id_comprador = v.id_comprador
   LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda 
     AND (p_id_material_catalogo IS NULL OR vi.id_material_catalogo = p_id_material_catalogo)
   WHERE c.deletado_em IS NULL
     AND c.latitude IS NOT NULL 
     AND c.longitude IS NOT NULL
     AND FN_CALCULAR_DISTANCIA(v_lat, v_lon, c.latitude, c.longitude) <= p_raio_km
   GROUP BY c.id_comprador
   ORDER BY c.score_confianca DESC, distancia_km ASC;
END$$

DROP PROCEDURE IF EXISTS SP_ESTATISTICAS_COOPERATIVA$$
CREATE PROCEDURE SP_ESTATISTICAS_COOPERATIVA(
  IN p_id_cooperativa BIGINT,
  IN p_periodo_dias INT
)
BEGIN
  DECLARE v_data_inicio DATETIME;
  SET v_data_inicio = DATE_SUB(NOW(), INTERVAL p_periodo_dias DAY);
  
  -- Resumo Geral
  SELECT
    COUNT(DISTINCT v.id_venda) AS total_vendas,
    COUNT(DISTINCT v.id_comprador) AS total_compradores,
    SUM(v.valor_total) AS receita_total,
    AVG(v.valor_total) AS ticket_medio,
    SUM(vi.quantidade_kg) AS kg_total,
    AVG(vi.preco_por_kg) AS preco_medio_kg,
    COUNT(DISTINCT vi.id_material_catalogo) AS materiais_diferentes
  FROM vendas v
  LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda
  WHERE v.id_cooperativa = p_id_cooperativa AND v.data_venda >= v_data_inicio;
  
  -- Top Materiais
  SELECT
    mb.nome AS categoria,
    mc.nome_especifico AS material,
    SUM(vi.quantidade_kg) AS kg_total,
    SUM(vi.total_item) AS valor_total,
    AVG(vi.preco_por_kg) AS preco_medio,
    COUNT(DISTINCT vi.id_venda) AS num_vendas
  FROM vendas_itens vi
  JOIN vendas v ON vi.id_venda = v.id_venda
  JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
  JOIN materiais_base mb ON mc.id_material_base = mb.id_material_base
  WHERE v.id_cooperativa = p_id_cooperativa AND v.data_venda >= v_data_inicio
  GROUP BY vi.id_material_catalogo
  ORDER BY kg_total DESC LIMIT 5;

  -- Top Compradores
  SELECT
    c.razao_social, c.cidade, c.score_confianca,
    COUNT(DISTINCT v.id_venda) AS num_compras,
    SUM(v.valor_total) AS valor_total,
    MAX(v.data_venda) AS ultima_compra
  FROM vendas v
  JOIN compradores c ON v.id_comprador = c.id_comprador
  WHERE v.id_cooperativa = p_id_cooperativa AND v.data_venda >= v_data_inicio
  GROUP BY v.id_comprador
  ORDER BY valor_total DESC LIMIT 5;
END$$

DROP PROCEDURE IF EXISTS SP_RELATORIO_COMPRADOR$$
CREATE PROCEDURE SP_RELATORIO_COMPRADOR(IN p_id_comprador BIGINT)
BEGIN
  -- Dados Gerais
  SELECT 
    c.*, 
    COUNT(DISTINCT v.id_venda) AS total_compras,
    COUNT(DISTINCT v.id_cooperativa) AS cooperativas_distintas,
    SUM(v.valor_total) AS valor_total_comprado,
    AVG(v.valor_total) AS ticket_medio,
    MIN(v.data_venda) AS primeira_compra,
    MAX(v.data_venda) AS ultima_compra,
    AVG(ac.score) AS media_avaliacoes
  FROM compradores c 
  LEFT JOIN vendas v ON c.id_comprador = v.id_comprador 
  LEFT JOIN avaliacoes_compradores ac ON v.id_venda = ac.id_venda
  WHERE c.id_comprador = p_id_comprador 
  GROUP BY c.id_comprador;

  -- Materiais Comprados
  SELECT
    mb.nome AS categoria, mc.nome_especifico AS material,
    COUNT(DISTINCT v.id_venda) AS num_compras,
    SUM(vi.quantidade_kg) AS kg_total,
    AVG(vi.preco_por_kg) AS preco_medio,
    MIN(vi.preco_por_kg) AS preco_minimo,
    MAX(vi.preco_por_kg) AS preco_maximo
  FROM vendas v
  JOIN vendas_itens vi ON v.id_venda = vi.id_venda
  JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
  JOIN materiais_base mb ON mc.id_material_base = mb.id_material_base
  WHERE v.id_comprador = p_id_comprador
  GROUP BY vi.id_material_catalogo
  ORDER BY kg_total DESC;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGERS 
-- ----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_venda_item_insert$$
CREATE TRIGGER trg_venda_item_insert AFTER INSERT ON vendas_itens FOR EACH ROW
BEGIN
  UPDATE vendas SET valor_total = (SELECT COALESCE(SUM(total_item), 0) FROM vendas_itens WHERE id_venda = NEW.id_venda) WHERE id_venda = NEW.id_venda;
END$$

DROP TRIGGER IF EXISTS trg_venda_item_update$$
CREATE TRIGGER trg_venda_item_update AFTER UPDATE ON vendas_itens FOR EACH ROW
BEGIN
  UPDATE vendas SET valor_total = (SELECT COALESCE(SUM(total_item), 0) FROM vendas_itens WHERE id_venda = NEW.id_venda) WHERE id_venda = NEW.id_venda;
END$$

DROP TRIGGER IF EXISTS trg_venda_item_delete$$
CREATE TRIGGER trg_venda_item_delete AFTER DELETE ON vendas_itens FOR EACH ROW
BEGIN
  UPDATE vendas SET valor_total = (SELECT COALESCE(SUM(total_item), 0) FROM vendas_itens WHERE id_venda = OLD.id_venda) WHERE id_venda = OLD.id_venda;
END$$

-- Trigger de Auditoria de Usuários
DROP TRIGGER IF EXISTS trg_audit_usuario_update$$
CREATE TRIGGER trg_audit_usuario_update AFTER UPDATE ON usuarios FOR EACH ROW
BEGIN
  IF OLD.status != NEW.status OR OLD.tipo != NEW.tipo THEN
    INSERT INTO audit_log (tabela_afetada, id_registro_afetado, acao, detalhes_antigos_json, detalhes_novos_json, timestamp_acao) 
    VALUES ('usuarios', NEW.id_usuario, 'UPDATE', JSON_OBJECT('status', OLD.status, 'tipo', OLD.tipo), JSON_OBJECT('status', NEW.status, 'tipo', NEW.tipo), NOW());
  END IF;
END$$

-- ----------------------------------------------------------------------------
-- EVENTS (Tarefas Agendadas)
-- ----------------------------------------------------------------------------

DROP EVENT IF EXISTS evt_limpeza_tokens$$
CREATE EVENT evt_limpeza_tokens ON SCHEDULE EVERY 1 DAY STARTS CURRENT_TIMESTAMP DO
BEGIN
  DELETE FROM tokens_validacao WHERE data_expiracao < NOW();
END$$

DROP EVENT IF EXISTS evt_limpeza_reprovados$$
CREATE EVENT evt_limpeza_reprovados ON SCHEDULE EVERY 1 DAY STARTS CURRENT_TIMESTAMP DO
BEGIN
  DELETE u FROM usuarios u
  LEFT JOIN cooperativas c ON u.id_usuario = c.id_usuario
  WHERE u.status = 'reprovado' AND u.tipo = 'cooperativa'
    AND (c.id_cooperativa IS NULL OR c.deletado_em IS NOT NULL)
    AND u.data_criacao < DATE_SUB(NOW(), INTERVAL 30 DAY);
END$$

DROP EVENT IF EXISTS evt_suspender_cooperativas_inativas$$
CREATE EVENT evt_suspender_cooperativas_inativas ON SCHEDULE EVERY 1 DAY STARTS CURRENT_TIMESTAMP DO
BEGIN
  UPDATE usuarios u JOIN cooperativas c ON u.id_usuario = c.id_usuario
  SET u.status = 'inativo'
  WHERE u.status = 'ativo' AND (c.ultima_atividade < DATE_SUB(NOW(), INTERVAL 60 DAY) OR c.ultima_atividade IS NULL) AND c.deletado_em IS NULL;
END$$

DROP EVENT IF EXISTS evt_expirar_avaliacoes_pendentes$$
CREATE EVENT evt_expirar_avaliacoes_pendentes ON SCHEDULE EVERY 1 DAY STARTS CURRENT_TIMESTAMP DO
BEGIN
  UPDATE avaliacoes_pendentes SET status_avaliacao = 'expirada'
  WHERE status_avaliacao = 'pendente' AND data_criacao < DATE_SUB(NOW(), INTERVAL 30 DAY);
END$$

-- Trigger para criar token de validação de email ao inserir usuário
DROP TRIGGER IF EXISTS trg_usuario_insert_token$$
CREATE TRIGGER trg_usuario_insert_token AFTER INSERT ON usuarios FOR EACH ROW
BEGIN
  INSERT INTO tokens_validacao (id_usuario, tipo, data_expiracao, token)
  VALUES (NEW.id_usuario, 'validacao_email', DATE_ADD(NOW(), INTERVAL 24 HOUR), HEX(RANDOM_BYTES(32)));
END$$

DELIMITER ;

-- ----------------------------------------------------------------------------
-- VIEWS (Relatórios Prontos)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_avaliacoes_pendentes_detalhadas AS 
SELECT 
   ap.id_avaliacao_pendente, ap.status_avaliacao, ap.data_criacao,
   v.id_venda, v.data_venda, v.valor_total,
   coop.id_cooperativa, coop.razao_social AS cooperativa_nome,
   comp.id_comprador, comp.razao_social AS comprador_nome,
   comp.cnpj AS comprador_cnpj, comp.score_confianca,
   comp.cidade AS comprador_cidade, comp.estado AS comprador_estado,
   comp.telefone AS comprador_telefone, comp.email AS comprador_email,
   GROUP_CONCAT(DISTINCT mc.nome_especifico SEPARATOR ', ') AS materiais_vendidos,
   SUM(vi.quantidade_kg) AS quantidade_total_kg 
FROM avaliacoes_pendentes ap 
JOIN vendas v ON ap.id_venda = v.id_venda 
JOIN cooperativas coop ON ap.id_cooperativa = coop.id_cooperativa 
JOIN compradores comp ON v.id_comprador = comp.id_comprador 
LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda 
LEFT JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo 
WHERE ap.status_avaliacao = 'pendente' 
GROUP BY ap.id_avaliacao_pendente;

CREATE OR REPLACE VIEW v_feedback_comprador_agregado AS 
SELECT 
   c.id_comprador, c.cnpj, c.razao_social,
   ft.id_feedback_tag, ft.texto AS feedback_texto,
   ft.tipo AS feedback_tipo, ft.categoria AS feedback_categoria,
   COUNT(*) AS quantidade_mencoes,
   ROUND(COUNT(*) * 100.0 / c.numero_avaliacoes, 2) AS percentual 
FROM compradores c 
JOIN vendas v ON c.id_comprador = v.id_comprador 
JOIN avaliacoes_compradores ac ON v.id_venda = ac.id_venda 
JOIN avaliacao_feedback_selecionado afs ON ac.id_avaliacao = afs.id_avaliacao 
JOIN feedback_tags ft ON afs.id_feedback_tag = ft.id_feedback_tag 
WHERE c.deletado_em IS NULL AND c.numero_avaliacoes > 0 
GROUP BY c.id_comprador, ft.id_feedback_tag 
ORDER BY c.id_comprador, quantidade_mencoes DESC;

CREATE OR REPLACE VIEW v_dashboard_cooperativa AS 
SELECT 
   c.id_cooperativa, c.razao_social,
   COUNT(DISTINCT v.id_venda) AS total_vendas,
   COUNT(DISTINCT v.id_comprador) AS total_compradores,
   COALESCE(SUM(v.valor_total), 0) AS receita_total,
   COALESCE(AVG(v.valor_total), 0) AS ticket_medio,
   MAX(v.data_venda) AS ultima_venda,
   COUNT(DISTINCT vi.id_material_catalogo) AS materiais_diferentes_vendidos,
   COALESCE(SUM(vi.quantidade_kg), 0) AS kg_total_vendidos,
   COUNT(DISTINCT CASE WHEN v.data_venda >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN v.id_venda END) AS vendas_ultimo_mes 
FROM cooperativas c 
LEFT JOIN vendas v ON c.id_cooperativa = v.id_cooperativa 
LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda 
WHERE c.deletado_em IS NULL 
GROUP BY c.id_cooperativa;

CREATE OR REPLACE VIEW v_cooperativas_pendentes AS
SELECT
  u.id_usuario, u.email, u.nome, u.status, u.data_criacao, u.data_criacao AS data_cadastro,
  c.id_cooperativa, c.cnpj, c.razao_social, c.nome_fantasia,
  c.email_contato, c.telefone, c.cidade, c.estado,
  COUNT(dc.id_documento) AS total_documentos,
  SUM(CASE WHEN dc.status = 'pendente' THEN 1 ELSE 0 END) AS docs_pendentes,
  SUM(CASE WHEN dc.status = 'aceito' THEN 1 ELSE 0 END) AS docs_aceitos,
  GROUP_CONCAT(DISTINCT CONCAT('uploads/documentos/', dc.nome_arquivo_armazenado) SEPARATOR ',') AS arquivo_url
FROM cooperativas c
JOIN usuarios u ON c.id_usuario = u.id_usuario
LEFT JOIN documentos_cooperativas dc ON c.id_cooperativa = dc.id_cooperativa
WHERE u.status = 'pendente' AND c.deletado_em IS NULL
GROUP BY c.id_cooperativa;

CREATE OR REPLACE VIEW v_cooperativas_pendentes_aprovacao AS
SELECT
    c.id_cooperativa,
    u.email,
    c.razao_social,
    c.cnpj,
    c.data_criacao,
    GROUP_CONCAT(doc.caminho_completo SEPARATOR '; ') AS documentos
FROM cooperativas c
JOIN usuarios u ON c.id_usuario = u.id_usuario
LEFT JOIN documentos_cooperativas doc ON c.id_cooperativa = doc.id_cooperativa AND doc.status = 'pendente'
WHERE u.status = 'pendente' AND c.deletado_em IS NULL
GROUP BY c.id_cooperativa, u.email, c.razao_social, c.cnpj, c.data_criacao;

CREATE OR REPLACE VIEW v_cooperados_detalhados AS
SELECT
    c.id_cooperado,
    c.id_usuario,
    c.cpf,
    c.data_vinculo,
    c.id_cooperativa,
    coop.nome_fantasia AS cooperativa_nome,
    u.nome AS usuario_nome,
    u.email AS usuario_email,
    u.status AS usuario_status
FROM cooperados AS c
JOIN usuarios AS u ON c.id_usuario = u.id_usuario
JOIN cooperativas AS coop ON c.id_cooperativa = coop.id_cooperativa;

CREATE OR REPLACE VIEW v_materiais_visiveis AS
SELECT
  c.id_cooperativa,
  mc.id_material_catalogo,
  mb.id_material_base,
  mb.nome AS categoria,
  COALESCE(ms.nome_sinonimo, mc.nome_especifico) AS nome_material,
  mc.nome_especifico AS nome_original,
  mc.descricao,
  mc.status,
  IF(ms.id_sinonimo IS NOT NULL, TRUE, FALSE) AS tem_sinonimo
FROM cooperativas c
CROSS JOIN materiais_catalogo mc
JOIN materiais_base mb ON mc.id_material_base = mb.id_material_base
LEFT JOIN materiais_sinonimos ms ON ms.id_material_catalogo = mc.id_material_catalogo 
  AND ms.id_cooperativa = c.id_cooperativa 
  AND ms.ativo = TRUE
WHERE mc.status = 'aprovado' AND mc.deletado_em IS NULL AND mb.ativo = TRUE;

CREATE OR REPLACE VIEW v_vendas_detalhadas AS
SELECT 
  v.id_venda, v.data_venda, v.valor_total, v.nf_numero, v.observacoes,
  coop.id_cooperativa, coop.razao_social AS cooperativa_nome, 
  coop.cidade AS cooperativa_cidade, coop.estado AS cooperativa_estado,
  comp.id_comprador, comp.razao_social AS comprador_nome, 
  comp.score_confianca, comp.numero_avaliacoes,
  vi.id_venda_item, vi.quantidade_kg, vi.preco_por_kg, vi.total_item,
  mb.nome AS material_categoria, mc.nome_especifico AS material_nome,
  av.score AS avaliacao_score, av.comentario_livre AS avaliacao_comentario
FROM vendas v
JOIN cooperativas coop ON v.id_cooperativa = coop.id_cooperativa
JOIN compradores comp ON v.id_comprador = comp.id_comprador
LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda
LEFT JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
LEFT JOIN materiais_base mb ON mc.id_material_base = mb.id_material_base
LEFT JOIN avaliacoes_compradores av ON v.id_venda = av.id_venda
WHERE coop.deletado_em IS NULL AND comp.deletado_em IS NULL
ORDER BY v.data_venda DESC;

CREATE OR REPLACE VIEW v_compradores_perfil AS
SELECT
  c.id_comprador, c.cnpj, c.razao_social, c.nome_fantasia,
  c.email, c.telefone, c.whatsapp,
  c.cidade, c.estado, c.latitude, c.longitude,
  c.score_confianca, c.numero_avaliacoes, c.data_criacao,
  ROUND(AVG(ac.score), 2) AS media_avaliacoes,
  COUNT(DISTINCT v.id_venda) AS total_vendas,
  COALESCE(SUM(v.valor_total), 0) AS valor_total_comprado,
  COUNT(DISTINCT v.id_cooperativa) AS num_cooperativas_distintas
FROM compradores c
LEFT JOIN vendas v ON c.id_comprador = v.id_comprador
LEFT JOIN avaliacoes_compradores ac ON v.id_venda = ac.id_venda
WHERE c.deletado_em IS NULL
GROUP BY c.id_comprador;

-- ====================================================
-- Lista de cooperativas otimizada para frontend
-- ====================================================
CREATE OR REPLACE VIEW v_cooperativas_list AS
SELECT
  c.id_cooperativa,
  c.id_usuario,
  c.cnpj,
  c.razao_social,
  c.nome_fantasia,
  COALESCE(c.email_contato, u.email) AS email,
  c.telefone,
  c.whatsapp,
  c.site,
  c.cep,
  c.logradouro,
  c.numero,
  c.complemento,
  c.bairro,
  c.cidade,
  c.estado,
  c.latitude,
  c.longitude,
  c.data_criacao,
  c.ultima_atualizacao,
  u.status AS usuario_status,
  CASE
    WHEN u.status = 'ativo' THEN TRUE
    WHEN u.status = 'pendente' THEN NULL
    ELSE FALSE
  END AS aprovado,
  COUNT(DISTINCT v.id_venda) AS total_vendas,
  COALESCE(GROUP_CONCAT(DISTINCT mc.nome_especifico ORDER BY mc.nome_especifico SEPARATOR '|'), NULL) AS materiais_vendidos
FROM cooperativas c
JOIN usuarios u ON u.id_usuario = c.id_usuario
LEFT JOIN vendas v ON v.id_cooperativa = c.id_cooperativa
LEFT JOIN vendas_itens vi ON vi.id_venda = v.id_venda
LEFT JOIN materiais_catalogo mc ON mc.id_material_catalogo = vi.id_material_catalogo
WHERE c.deletado_em IS NULL
GROUP BY c.id_cooperativa;

-- ============================================== 
-- DADOS INICIAIS 
-- ==================================================== 

-- Configurações do Sistema (Regras de Negócio)
INSERT INTO config_sistema (chave, valor, tipo_valor, descricao, editavel) VALUES 
('peso_prior_bayesiano', '3.0', 'float', 'Peso da avaliação neutra no cálculo Bayesiano', TRUE), 
('avaliacao_neutra_novato', '2.5', 'float', 'Score neutro para compradores novos', TRUE), 
('decaimento_anual_score', '365', 'int', 'Dias para decaimento de 63% no peso das avaliações', TRUE), 
('min_avaliacoes_confianca', '10', 'int', 'Mínimo de avaliações para confiança total no score', TRUE), 
('validade_token_horas', '24', 'int', 'Validade dos tokens em horas', TRUE), 
('dias_inatividade_suspensao', '60', 'int', 'Dias sem atividade para suspender cooperativa', TRUE), 
('prazo_edicao_venda_horas', '24', 'int', 'Prazo em horas para editar vendas', TRUE), 
('min_transacoes_preco_regional', '3', 'int', 'Mínimo de transações para calcular preço regional', TRUE)
ON DUPLICATE KEY UPDATE valor = VALUES(valor);

-- Materiais Base (Categorias Principais)
INSERT INTO materiais_base (nome, descricao, icone, ordem_exibicao, ativo) VALUES 
('Plástico', 'Materiais plásticos recicláveis (PET, PEAD, PP, etc)', 'plastic', 1, TRUE), 
('Papel/Papelão', 'Papel, papelão e derivados', 'paper', 2, TRUE), 
('Metal', 'Metais ferrosos e não-ferrosos', 'metal', 3, TRUE), 
('Vidro', 'Vidros e cristais', 'glass', 4, TRUE), 
('Madeira', 'Madeira e derivados', 'wood', 5, TRUE), 
('Eletrônicos', 'Equipamentos eletrônicos e componentes', 'electronics', 6, TRUE), 
('Têxtil', 'Tecidos e materiais têxteis', 'textile', 7, TRUE), 
('Outros', 'Outros materiais recicláveis', 'recycle', 8, TRUE)
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao);

INSERT INTO materiais_catalogo (id_material_base, nome_especifico, descricao, status, data_aprovacao) VALUES
(1, 'PET Cristal', 'Garrafa PET transparente', 'aprovado', NOW()),
(1, 'PET Verde', 'Garrafa PET verde', 'aprovado', NOW()),
(1, 'PET Óleo', 'Garrafa PET de óleo', 'aprovado', NOW()),
(1, 'PEAD Branco', 'Plástico PEAD branco (embalagens)', 'aprovado', NOW()),
(1, 'PEAD Colorido', 'Plástico PEAD colorido', 'aprovado', NOW()),
(2, 'Papelão Ondulado', 'Caixas de papelão', 'aprovado', NOW()),
(2, 'Papel Branco', 'Papel sulfite e similar', 'aprovado', NOW()),
(2, 'Papel Misto', 'Papel misto (jornais, revistas)', 'aprovado', NOW()),
(2, 'Tetra Pak', 'Embalagens longa vida', 'aprovado', NOW()),
(3, 'Alumínio', 'Latas de alumínio e perfis', 'aprovado', NOW()),
(3, 'Cobre', 'Fios e componentes de cobre', 'aprovado', NOW()),
(3, 'Ferro', 'Sucata ferrosa', 'aprovado', NOW()),
(3, 'Aço', 'Latas de aço e estruturas', 'aprovado', NOW()),
(4, 'Vidro Transparente', 'Vidro incolor', 'aprovado', NOW()),
(4, 'Vidro Colorido', 'Vidro âmbar, verde, azul', 'aprovado', NOW()),
(6, 'Placa Eletrônica', 'Placas de circuito impresso', 'aprovado', NOW()),
(6, 'Fio de Cobre', 'Fiação elétrica', 'aprovado', NOW());

INSERT INTO feedback_tags (texto, tipo, categoria, ordem_exibicao, ativo) VALUES
('Pagou adiantado', 'positivo', 'pagamento', 1, TRUE),
('Pagou em dia', 'positivo', 'pagamento', 2, TRUE),
('Boas condições de pagamento', 'positivo', 'pagamento', 3, TRUE),
('Logística eficiente', 'positivo', 'logistica', 4, TRUE),
('Coleta no local', 'positivo', 'logistica', 5, TRUE),
('Frete por conta do comprador', 'positivo', 'logistica', 6, TRUE),
('Comunicação clara', 'positivo', 'comunicacao', 7, TRUE),
('Fácil de contatar', 'positivo', 'comunicacao', 8, TRUE),
('Transparente nas negociações', 'positivo', 'comunicacao', 9, TRUE),
('Pouca burocracia', 'positivo', 'processo', 10, TRUE),
('Processo rápido', 'positivo', 'processo', 11, TRUE),
('Flexível com padrões', 'positivo', 'processo', 12, TRUE),
('Atrasou pagamento', 'negativo', 'pagamento', 13, TRUE),
('Paga pouco', 'negativo', 'pagamento', 14, TRUE),
('Descontou valor sem avisar', 'negativo', 'pagamento', 15, TRUE),
('Logística complicada', 'negativo', 'logistica', 16, TRUE),
('Não coleta no local', 'negativo', 'logistica', 17, TRUE),
('Frete caro', 'negativo', 'logistica', 18, TRUE),
('Difícil de contatar', 'negativo', 'comunicacao', 19, TRUE),
('Não responde mensagens', 'negativo', 'comunicacao', 20, TRUE),
('Comunicação confusa', 'negativo', 'comunicacao', 21, TRUE),
('Muita burocracia', 'negativo', 'processo', 22, TRUE),
('Muitas exigências', 'negativo', 'processo', 23, TRUE),
('Processo demorado', 'negativo', 'processo', 24, TRUE),
('Muito exigente com qualidade', 'negativo', 'qualidade', 25, TRUE),
('Desconta muito por contaminação', 'negativo', 'qualidade', 26, TRUE),
('Critérios de qualidade não claros', 'negativo', 'qualidade', 27, TRUE);

INSERT INTO usuarios (nome, email, senha_hash, tipo, status) VALUES
('Administrador Root', 'root@recoopera.com', '639e4eeb4030a3cce2f9874f7d99e724aabe569c52874b01208d642fbe068227', 'root', 'ativo');

-- ====================================================
-- ÍNDICES ADICIONAIS DE PERFORMANCE
-- ====================================================

CREATE INDEX idx_vendas_coop_data_valor ON vendas(id_cooperativa, data_venda DESC, valor_total);
CREATE INDEX idx_vendas_comp_data ON vendas(id_comprador, data_venda DESC);
CREATE INDEX idx_avaliacoes_comp_score ON avaliacoes_compradores(id_comprador, score, data_avaliacao DESC);
CREATE INDEX idx_materiais_base_ativo ON materiais_catalogo(id_material_base, status, deletado_em);

-- ====================================================
-- OTIMIZAÇÕES FINAIS
-- ====================================================

OPTIMIZE TABLE usuarios;
OPTIMIZE TABLE cooperativas;
OPTIMIZE TABLE compradores;
OPTIMIZE TABLE vendas;
OPTIMIZE TABLE vendas_itens;
OPTIMIZE TABLE avaliacoes_compradores;

ANALYZE TABLE usuarios;
ANALYZE TABLE cooperativas;
ANALYZE TABLE compradores;
ANALYZE TABLE vendas;
ANALYZE TABLE materiais_catalogo;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;