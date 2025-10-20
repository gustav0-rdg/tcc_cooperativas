CREATE DATABASE IF NOT EXISTS `recoopera`;

USE `recoopera`;

-- Comandos de configuração para otimizar a criação do banco de dados
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

-- ============================================================================
-- Tabelas responsáveis por gerenciar quem pode acessar o sistema.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `nome` VARCHAR(200) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `senha_hash` VARCHAR(255) NOT NULL,
  `tipo` ENUM('gestor', 'cooperativa') NOT NULL DEFAULT 'cooperativa', 
  `status` ENUM('ativo', 'inativo', 'bloqueado', 'pendente') NOT NULL DEFAULT 'pendente',
  `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `uidx_email` (`email`)
);

CREATE TABLE IF NOT EXISTS `tokens_validacao` (
  `id_token` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_usuario` BIGINT UNSIGNED NOT NULL,
  `token` CHAR(64) NOT NULL, 
  `tipo` ENUM('cadastro', 'recuperacao_senha') NOT NULL,
  `usado` BOOLEAN NOT NULL DEFAULT FALSE, 
  `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_expiracao` DATETIME NOT NULL,
  UNIQUE INDEX `uidx_token` (`token`),
  INDEX `idx_usuario_tipo` (`id_usuario`, `tipo`),
  CONSTRAINT `fk_tokens_usuarios`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- ============================================================================
-- Tabelas que representam as entidades principais do negócio.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `cooperativas` (
  `id_cooperativa` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_usuario` BIGINT UNSIGNED NOT NULL,
  `cnpj` CHAR(14) NOT NULL,
  `razao_social` VARCHAR(255) NOT NULL,
  `endereco` TEXT NULL,
  `cidade` VARCHAR(100) NULL,
  `estado` CHAR(2) NULL,
  `latitude` DECIMAL(10,8) NULL,
  `longitude` DECIMAL(11,8) NULL,
  `aprovado` BOOLEAN NOT NULL DEFAULT FALSE,
  `ultima_atualizacao` DATETIME NULL,
  `data_cadastro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `uidx_cnpj` (`cnpj`),
  UNIQUE INDEX `uidx_id_usuario` (`id_usuario`),
  INDEX `idx_cidade_estado` (`cidade`, `estado`),
  INDEX `idx_ultima_atualizacao` (`ultima_atualizacao`),
  CONSTRAINT `fk_cooperativas_usuarios`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `documentos_cooperativa` (
  `id_documento` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_cooperativa` BIGINT UNSIGNED NOT NULL,
  `arquivo_url` VARCHAR(500) NOT NULL,
  `tipo_documento` ENUM('contrato_social', 'cartao_cnpj', 'alvara', 'outro') NOT NULL,
  `status` ENUM('pendente', 'aceito', 'negado') NOT NULL DEFAULT 'pendente',
  `data_envio` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_avaliacao` DATETIME NULL,
  `motivo_rejeicao` TEXT NULL,
  `id_gestor_avaliador` BIGINT UNSIGNED NULL,
  INDEX `idx_cooperativa_status` (`id_cooperativa`, `status`),
  CONSTRAINT `fk_documentos_cooperativas`
    FOREIGN KEY (`id_cooperativa`)
    REFERENCES `cooperativas` (`id_cooperativa`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_documentos_gestor`
    FOREIGN KEY (`id_gestor_avaliador`)
    REFERENCES `usuarios` (`id_usuario`)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `compradores` (
  `id_comprador` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `cnpj` CHAR(14) NOT NULL,
  `razao_social` VARCHAR(255) NOT NULL,
  `endereco` TEXT NULL,
  `cidade` VARCHAR(100) NULL,
  `estado` CHAR(2) NULL,
  `latitude` DECIMAL(10,8) NULL,
  `longitude` DECIMAL(11,8) NULL,
  `telefone` VARCHAR(20) NULL, 
  `email` VARCHAR(255) NULL,   
  `score_confianca` DECIMAL(4,2) NOT NULL DEFAULT 5.00,
  `numero_avaliacoes` INT UNSIGNED NOT NULL DEFAULT 0,  
  `deletado_em` DATETIME NULL,
  `data_cadastro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `uidx_cnpj` (`cnpj`),
  INDEX `idx_score_confianca` (`score_confianca` DESC), 
  INDEX `idx_cidade_estado` (`cidade`, `estado`),
  INDEX `idx_ativo` (`deletado_em`)
);

CREATE TABLE IF NOT EXISTS `exigencias_compradores` (
  `id_exigencia` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_comprador` BIGINT UNSIGNED NOT NULL,
  `carregamento_coop` BOOLEAN NULL,
  `exige_enfardamento` BOOLEAN NULL,
  `aceita_granel` BOOLEAN NULL,
  `frete_comprador` BOOLEAN NULL,
  `desconta_contaminantes` BOOLEAN NULL,
  `prazo_pagamento_dias` INT UNSIGNED NULL,
  `observacoes` TEXT NULL,
  UNIQUE INDEX `uidx_comprador` (`id_comprador`),
  CONSTRAINT `fk_exigencias_compradores`
    FOREIGN KEY (`id_comprador`)
    REFERENCES `compradores` (`id_comprador`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- Tabelas para catalogar os tipos de materiais recicláveis.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `materiais_catalogo` (
  `id_material_catalogo` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `nome_padrao` VARCHAR(255) NOT NULL,
  `descricao` TEXT NULL,
  `categoria` ENUM('Plástico', 'Papel/Papelão', 'Metal', 'Vidro', 'Madeira', 'Eletrônicos', 'Outros') NOT NULL,
  `imagem_url` VARCHAR(500) NULL,
  UNIQUE INDEX `uidx_nome_padrao` (`nome_padrao`),
  INDEX `idx_categoria` (`categoria`)
);

CREATE TABLE IF NOT EXISTS `materiais_apelidos` (
  `id_apelido` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_material_catalogo` INT UNSIGNED NOT NULL,
  `nome_regional` VARCHAR(255) NOT NULL,
  UNIQUE INDEX `uidx_nome_regional` (`nome_regional`),
  INDEX `idx_material_catalogo` (`id_material_catalogo`),
  CONSTRAINT `fk_apelidos_catalogo`
    FOREIGN KEY (`id_material_catalogo`)
    REFERENCES `materiais_catalogo` (`id_material_catalogo`)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- ============================================================================
-- Tabelas que registram as operações de venda entre cooperativas e compradores.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `vendas` (
  `id_venda` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_cooperativa` BIGINT UNSIGNED NOT NULL,
  `id_comprador` BIGINT UNSIGNED NOT NULL,
  `data_venda` DATETIME NOT NULL,
  `valor_total` DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  INDEX `idx_cooperativa` (`id_cooperativa`),
  INDEX `idx_comprador` (`id_comprador`),
  INDEX `idx_data_venda` (`data_venda` DESC),
  CONSTRAINT `fk_vendas_cooperativas`
    FOREIGN KEY (`id_cooperativa`)
    REFERENCES `cooperativas` (`id_cooperativa`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_vendas_compradores`
    FOREIGN KEY (`id_comprador`)
    REFERENCES `compradores` (`id_comprador`)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `vendas_itens` (
  `id_venda_item` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_venda` BIGINT UNSIGNED NOT NULL,
  `id_material_catalogo` INT UNSIGNED NOT NULL,
  `quantidade_kg` DECIMAL(12,3) NOT NULL CHECK (quantidade_kg > 0), 
  `preco_por_kg` DECIMAL(12,4) NOT NULL CHECK (preco_por_kg > 0), 
  INDEX `idx_venda` (`id_venda`),
  INDEX `idx_material` (`id_material_catalogo`),
  CONSTRAINT `fk_itens_vendas`
    FOREIGN KEY (`id_venda`)
    REFERENCES `vendas` (`id_venda`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_itens_materiais`
    FOREIGN KEY (`id_material_catalogo`)
    REFERENCES `materiais_catalogo` (`id_material_catalogo`)
    ON DELETE RESTRICT ON UPDATE CASCADE
);


-- ============================================================================
-- Tabelas relacionadas ao sistema de reputação dos compradores.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `feedback_tags` (
  `id_feedback_tag` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `texto` VARCHAR(100) NOT NULL,
  `tipo` ENUM('positivo', 'negativo') NOT NULL,
  UNIQUE INDEX `uidx_texto` (`texto`)
);

CREATE TABLE IF NOT EXISTS `avaliacoes_compradores` (
  `id_avaliacao` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_venda` BIGINT UNSIGNED NOT NULL,
  `pontualidade_pagamento` TINYINT UNSIGNED NOT NULL CHECK (pontualidade_pagamento BETWEEN 1 AND 5),
  `logistica_entrega` TINYINT UNSIGNED NOT NULL CHECK (logistica_entrega BETWEEN 1 AND 5),
  `qualidade_negociacao` TINYINT UNSIGNED NOT NULL CHECK (qualidade_negociacao BETWEEN 1 AND 5),
  `comentario_livre` TEXT NULL,
  `data_avaliacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `uidx_id_venda` (`id_venda`),
  CONSTRAINT `fk_avaliacoes_vendas`
    FOREIGN KEY (`id_venda`)
    REFERENCES `vendas` (`id_venda`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `avaliacao_feedback_selecionado` (
  `id_avaliacao` BIGINT UNSIGNED NOT NULL,
  `id_feedback_tag` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id_avaliacao`, `id_feedback_tag`),
  CONSTRAINT `fk_feedback_sel_avaliacoes`
    FOREIGN KEY (`id_avaliacao`)
    REFERENCES `avaliacoes_compradores` (`id_avaliacao`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_feedback_sel_tags`
    FOREIGN KEY (`id_feedback_tag`)
    REFERENCES `feedback_tags` (`id_feedback_tag`)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- ============================================================================
-- Tabelas de apoio, logs e dados pré-processados para performance.
-- ============================================================================

CREATE TABLE IF NOT EXISTS `precos_regionais` (
  `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_material_catalogo` INT UNSIGNED NOT NULL,
  `regiao` VARCHAR(100) NOT NULL,
  `preco_medio` DECIMAL(12,4) NOT NULL,
  `preco_minimo` DECIMAL(12,4) NOT NULL,
  `preco_maximo` DECIMAL(12,4) NOT NULL,
  `desvio_padrao` DECIMAL(10,4) NOT NULL,
  `numero_transacoes` INT UNSIGNED NOT NULL, 
  `data_atualizacao` DATETIME NOT NULL,
  UNIQUE INDEX `uidx_material_regiao_data` (`id_material_catalogo`, `regiao`, `data_atualizacao`),
  INDEX `idx_regiao_material` (`regiao`, `id_material_catalogo`),
  CONSTRAINT `fk_precos_materiais`
    FOREIGN KEY (`id_material_catalogo`)
    REFERENCES `materiais_catalogo` (`id_material_catalogo`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `historico_score` (
  `id_hist` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `id_comprador` BIGINT UNSIGNED NOT NULL,
  `score_calculado` DECIMAL(4,2) NOT NULL,
  `detalhe_json` JSON NULL,
  `data_calculo` DATETIME NOT NULL,
  INDEX `idx_comprador_data` (`id_comprador`, `data_calculo` DESC),
  CONSTRAINT `fk_historico_compradores`
    FOREIGN KEY (`id_comprador`)
    REFERENCES `compradores` (`id_comprador`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `config_sistema` (
  `chave` VARCHAR(100) NOT NULL PRIMARY KEY,
  `valor` VARCHAR(200) NOT NULL,
  `descricao` TEXT NULL
);

CREATE TABLE IF NOT EXISTS `audit_log` (
  `id_log` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `tabela_afetada` VARCHAR(100) NOT NULL,
  `id_registro_afetado` VARCHAR(255) NOT NULL,
  `acao` ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  `detalhes_antigos_json` JSON NULL,
  `detalhes_novos_json` JSON NULL,
  `usuario_responsavel` VARCHAR(255) NULL,
  `timestamp_acao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_tabela_acao` (`tabela_afetada`, `acao`),
  INDEX `idx_timestamp` (`timestamp_acao` DESC)
);


-- ============================================================================
-- Inserção de dados básicos para o funcionamento do sistema.
-- ============================================================================

INSERT INTO `config_sistema` (`chave`, `valor`, `descricao`) VALUES
('peso_pontualidade', '0.5', 'Peso da nota de pontualidade no pagamento'),
('peso_logistica', '0.3', 'Peso da nota de logística e entrega'),
('peso_negociacao', '0.2', 'Peso da nota de qualidade da negociação e comunicação'),
('decaimento_anual_score', '365', 'Dias para decaimento do peso da avaliação. Avaliações mais antigas perdem peso.'),
('avaliacao_neutra_novato', '2.5', 'Score inicial (0-5) para compradores sem avaliações'),
('validade_token_horas', '24', 'Validade do token de validação em horas'),
('dias_inatividade_suspensao', '60', 'Dias sem atualização para suspender acesso da cooperativa'),
('min_avaliacoes_confianca', '10', 'Número mínimo de avaliações para que o score de um comprador atinja confiança estatística máxima.'),
('peso_prior_bayesiano', '3', 'Fator de suavização. Equivalente a adicionar X avaliações neutras no cálculo para evitar que novos compradores com uma única nota alta disparem no ranking.');

INSERT INTO `feedback_tags` (`texto`, `tipo`) VALUES
('Pagou adiantado', 'positivo'),
('Pagou na hora', 'positivo'),
('Logística eficiente', 'positivo'),
('Comunicação clara', 'positivo'),
('Pouca burocracia', 'positivo'),
('Atrasou o pagamento', 'negativo'),
('Difícil de contatar', 'negativo'),
('Logística complicada', 'negativo'),
('Muitas exigências', 'negativo');


-- ============================================================================
-- FUNÇÕES, TRIGGERS, PROCEDURES E EVENTS
-- ============================================================================

DELIMITER $$

-- ----------------------------------------------------------------------------
-- Triggers de HASH de Senha e Geração de TOKEN
-- ----------------------------------------------------------------------------

CREATE TRIGGER `trg_hash_senha_insert`
BEFORE INSERT ON `usuarios`
FOR EACH ROW
BEGIN
    SET NEW.senha_hash = SHA2(NEW.senha_hash, 256);
END$$


CREATE TRIGGER `trg_hash_senha_update`
BEFORE UPDATE ON `usuarios`
FOR EACH ROW
BEGIN
    IF NEW.senha_hash != OLD.senha_hash THEN
        SET NEW.senha_hash = SHA2(NEW.senha_hash, 256);
    END IF;
END$$


CREATE TRIGGER `trg_gerar_token_validacao_insert`
BEFORE INSERT ON `tokens_validacao`
FOR EACH ROW
BEGIN
    SET NEW.token = SHA2(UUID(), 256);
END$$

-- ----------------------------------------------------------------------------
-- Função de Cálculo de Score
-- ----------------------------------------------------------------------------

CREATE FUNCTION `calcular_score_confianca`(p_id_comprador BIGINT UNSIGNED)
RETURNS DECIMAL(4,2)
READS SQL DATA
BEGIN
    DECLARE v_score_bruto DECIMAL(10,8) DEFAULT 0.0;
    DECLARE v_score_ajustado DECIMAL(10,8) DEFAULT 0.0;
    DECLARE v_soma_ponderada DECIMAL(20,10) DEFAULT 0.0;
    DECLARE v_soma_pesos DECIMAL(20,10) DEFAULT 0.0;
    DECLARE v_num_avaliacoes INT DEFAULT 0;
    DECLARE v_peso_pontualidade DECIMAL(4,2);
    DECLARE v_peso_logistica DECIMAL(4,2);
    DECLARE v_peso_negociacao DECIMAL(4,2);
    DECLARE v_decaimento_dias DECIMAL(10,2);
    DECLARE v_aval_neutra DECIMAL(4,2);
    DECLARE v_min_aval_confianca INT;
    DECLARE v_peso_prior DECIMAL(10,2);
    DECLARE v_fator_confianca DECIMAL(10,8);

    SELECT CAST(valor AS DECIMAL(4,2)) INTO v_peso_pontualidade FROM config_sistema WHERE chave = 'peso_pontualidade';
    SELECT CAST(valor AS DECIMAL(4,2)) INTO v_peso_logistica FROM config_sistema WHERE chave = 'peso_logistica';
    SELECT CAST(valor AS DECIMAL(4,2)) INTO v_peso_negociacao FROM config_sistema WHERE chave = 'peso_negociacao';
    SELECT CAST(valor AS DECIMAL(10,2)) INTO v_decaimento_dias FROM config_sistema WHERE chave = 'decaimento_anual_score';
    SELECT CAST(valor AS DECIMAL(4,2)) INTO v_aval_neutra FROM config_sistema WHERE chave = 'avaliacao_neutra_novato';
    SELECT CAST(valor AS SIGNED) INTO v_min_aval_confianca FROM config_sistema WHERE chave = 'min_avaliacoes_confianca';
    SELECT CAST(valor AS DECIMAL(10,2)) INTO v_peso_prior FROM config_sistema WHERE chave = 'peso_prior_bayesiano';

    SELECT COUNT(*) INTO v_num_avaliacoes
    FROM avaliacoes_compradores ac
    JOIN vendas v ON ac.id_venda = v.id_venda
    WHERE v.id_comprador = p_id_comprador;

    IF v_num_avaliacoes = 0 THEN
        RETURN v_aval_neutra;
    END IF;

    SELECT
        SUM(calculo.nota_ponderada * calculo.peso_temporal),
        SUM(calculo.peso_temporal)
    INTO
        v_soma_ponderada, v_soma_pesos
    FROM (
        SELECT
            ((ac.pontualidade_pagamento * v_peso_pontualidade) +
             (ac.logistica_entrega * v_peso_logistica) +
             (ac.qualidade_negociacao * v_peso_negociacao)) * 2 AS nota_ponderada,
            EXP(-DATEDIFF(NOW(), v.data_venda) / v_decaimento_dias) AS peso_temporal
        FROM avaliacoes_compradores ac
        JOIN vendas v ON ac.id_venda = v.id_venda
        WHERE v.id_comprador = p_id_comprador
    ) AS calculo;

    IF v_soma_pesos > 0 THEN
        SET v_score_bruto = v_soma_ponderada / v_soma_pesos;
    ELSE
        RETURN v_aval_neutra;
    END IF;

    SET v_score_ajustado = (v_score_bruto * v_num_avaliacoes + v_aval_neutra * v_peso_prior) /
                           (v_num_avaliacoes + v_peso_prior);

    SET v_fator_confianca = LEAST(v_num_avaliacoes / v_min_aval_confianca, 1.0);
    SET v_score_ajustado = v_aval_neutra + (v_score_ajustado - v_aval_neutra) * v_fator_confianca;

    IF v_score_ajustado > 10.00 THEN SET v_score_ajustado = 10.00; END IF;
    IF v_score_ajustado < 0.00 THEN SET v_score_ajustado = 0.00; END IF;

    RETURN v_score_ajustado / 2;
END$$

-- ----------------------------------------------------------------------------
-- Triggers de Atualização de Vendas e Score
-- ----------------------------------------------------------------------------

CREATE TRIGGER `trg_atualizar_valor_total_venda_insert`
AFTER INSERT ON `vendas_itens`
FOR EACH ROW
BEGIN
    UPDATE vendas v
    SET v.valor_total = (
        SELECT COALESCE(SUM(vi.quantidade_kg * vi.preco_por_kg), 0)
        FROM vendas_itens vi
        WHERE vi.id_venda = NEW.id_venda
    )
    WHERE v.id_venda = NEW.id_venda;
END$$

CREATE TRIGGER `trg_atualizar_valor_total_venda_update`
AFTER UPDATE ON `vendas_itens`
FOR EACH ROW
BEGIN
    UPDATE vendas v
    SET v.valor_total = (
        SELECT COALESCE(SUM(vi.quantidade_kg * vi.preco_por_kg), 0)
        FROM vendas_itens vi
        WHERE vi.id_venda = NEW.id_venda
    )
    WHERE v.id_venda = NEW.id_venda;
END$$

CREATE TRIGGER `trg_atualizar_valor_total_venda_delete`
AFTER DELETE ON `vendas_itens`
FOR EACH ROW
BEGIN
    UPDATE vendas v
    SET v.valor_total = (
        SELECT COALESCE(SUM(vi.quantidade_kg * vi.preco_por_kg), 0)
        FROM vendas_itens vi
        WHERE vi.id_venda = OLD.id_venda
    )
    WHERE v.id_venda = OLD.id_venda;
END$$

CREATE TRIGGER `trg_recalcular_score_apos_avaliacao`
AFTER INSERT ON `avaliacoes_compradores`
FOR EACH ROW
BEGIN
    DECLARE v_novo_score DECIMAL(4,2);
    DECLARE v_id_comprador BIGINT UNSIGNED;
    DECLARE v_num_avaliacoes INT;

    SELECT id_comprador INTO v_id_comprador
    FROM vendas
    WHERE id_venda = NEW.id_venda;

    SET v_novo_score = calcular_score_confianca(v_id_comprador);

    SELECT COUNT(*) INTO v_num_avaliacoes
    FROM avaliacoes_compradores ac
    JOIN vendas v ON ac.id_venda = v.id_venda
    WHERE v.id_comprador = v_id_comprador;

    UPDATE compradores
    SET score_confianca = v_novo_score,
        numero_avaliacoes = v_num_avaliacoes
    WHERE id_comprador = v_id_comprador;

    INSERT INTO historico_score (id_comprador, score_calculado, detalhe_json, data_calculo)
    VALUES (
        v_id_comprador,
        v_novo_score,
        JSON_OBJECT('trigger', 'nova_avaliacao', 'id_avaliacao', NEW.id_avaliacao),
        NOW()
    );
END$$

CREATE TRIGGER `trg_atualizar_data_cooperativa`
AFTER INSERT ON `vendas`
FOR EACH ROW
BEGIN
    UPDATE cooperativas
    SET ultima_atualizacao = NOW()
    WHERE id_cooperativa = NEW.id_cooperativa;
END$$

-- ----------------------------------------------------------------------------
-- Procedures e Events
-- ----------------------------------------------------------------------------

CREATE PROCEDURE `materializar_precos_regionais`()
BEGIN
    TRUNCATE TABLE `precos_regionais`;

    INSERT INTO `precos_regionais`
        (id_material_catalogo, regiao, preco_medio, preco_minimo, preco_maximo, desvio_padrao, numero_transacoes, data_atualizacao)
    SELECT
        vi.id_material_catalogo,
        c.estado AS regiao,
        AVG(vi.preco_por_kg) AS preco_medio,
        MIN(vi.preco_por_kg) AS preco_minimo,
        MAX(vi.preco_por_kg) AS preco_maximo,
        COALESCE(STDDEV(vi.preco_por_kg), 0) AS desvio_padrao,
        COUNT(*) AS numero_transacoes,
        NOW() AS data_atualizacao
    FROM vendas_itens vi
    JOIN vendas v ON vi.id_venda = v.id_venda
    JOIN compradores c ON v.id_comprador = c.id_comprador
    WHERE v.data_venda >= DATE_SUB(NOW(), INTERVAL 90 DAY)
      AND c.deletado_em IS NULL
    GROUP BY vi.id_material_catalogo, c.estado
    HAVING COUNT(*) >= 3;
END$$


CREATE EVENT `evt_materializar_precos_regionais`
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '03:00:00')
DO
BEGIN
    CALL materializar_precos_regionais();
END$$

DELIMITER ;

-- ============================================================================
-- VIEWS E PERMISSÕES DE ACESSO
-- ============================================================================

CREATE OR REPLACE VIEW `v_compradores_publico` AS
SELECT
    id_comprador,
    razao_social,
    cidade,
    estado,
    latitude,
    longitude,
    telefone,
    email,
    score_confianca,
    numero_avaliacoes
FROM compradores
WHERE deletado_em IS NULL;


CREATE OR REPLACE VIEW `v_precos_mercado_anonimizado` AS
SELECT
    mc.nome_padrao AS material,
    mc.categoria,
    c.estado,
    AVG(vi.preco_por_kg) AS preco_medio,
    MIN(vi.preco_por_kg) AS preco_minimo,
    MAX(vi.preco_por_kg) AS preco_maximo,
    STDDEV(vi.preco_por_kg) AS desvio_padrao,
    COUNT(*) AS num_transacoes,
    YEAR(v.data_venda) AS ano,
    MONTH(v.data_venda) AS mes
FROM vendas_itens vi
JOIN vendas v ON vi.id_venda = v.id_venda
JOIN compradores c ON v.id_comprador = c.id_comprador
JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
WHERE v.data_venda >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
  AND c.deletado_em IS NULL
GROUP BY mc.nome_padrao, mc.categoria, c.estado, ano, mes
HAVING COUNT(*) >= 3;


CREATE ROLE IF NOT EXISTS 'gestor_role', 'cooperativa_role';

GRANT ALL PRIVILEGES ON `recoopera`.* TO 'gestor_role';

GRANT SELECT ON `recoopera`.`v_compradores_publico` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`v_precos_mercado_anonimizado` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`config_sistema` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`materiais_catalogo` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`materiais_apelidos` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`feedback_tags` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`precos_regionais` TO 'cooperativa_role';
GRANT SELECT ON `recoopera`.`exigencias_compradores` TO 'cooperativa_role';

GRANT INSERT ON `recoopera`.`vendas` TO 'cooperativa_role';
GRANT INSERT ON `recoopera`.`vendas_itens` TO 'cooperativa_role';
GRANT INSERT ON `recoopera`.`avaliacoes_compradores` TO 'cooperativa_role';
GRANT INSERT ON `recoopera`.`avaliacao_feedback_selecionado` TO 'cooperativa_role';
GRANT INSERT, UPDATE, SELECT ON `recoopera`.`materiais_apelidos` TO 'cooperativa_role';

GRANT INSERT, UPDATE (endereco, cidade, estado, latitude, longitude, telefone, email) ON `recoopera`.`compradores` TO 'cooperativa_role';
GRANT SELECT (`id_comprador`, `razao_social`, `cnpj`) ON `recoopera`.`compradores` TO 'cooperativa_role';

GRANT EXECUTE ON FUNCTION `recoopera`.`calcular_score_confianca` TO 'cooperativa_role';

-- Restaura as configurações originais do MySQL
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;