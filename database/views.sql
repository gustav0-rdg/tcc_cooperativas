CREATE OR REPLACE VIEW v_cooperados_detalhados AS
SELECT
    c.id_cooperado,
    c.id_usuario,
    c.cpf,
    c.telefone,
    coop.logradouro AS endereco,
    coop.cidade AS cidade,
    coop.estado AS estado,
    c.data_vinculo,
    c.deletado_em,
    c.id_cooperativa,
    coop.nome_fantasia AS cooperativa_nome,
    u.nome AS usuario_nome,
    u.email AS usuario_email,
    u.status AS usuario_status
FROM cooperados AS c
JOIN usuarios AS u ON c.id_usuario = u.id_usuario
JOIN cooperativas AS coop ON c.id_cooperativa = coop.id_cooperativa;