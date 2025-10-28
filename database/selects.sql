-- SELECT DOS VALORES MINIMOS E MAXIMOS

WITH VendasIndividuais AS (
    SELECT
        mc.categoria,
        mc.nome_padrao,
        c.razao_social,
        c.cnpj,
        vi.quantidade_kg,
        v.valor_total,
        (v.valor_total / vi.quantidade_kg) AS preco_por_kg
    FROM compradores AS c
    INNER JOIN vendas AS v ON c.id_comprador = v.id_comprador
    INNER JOIN vendas_itens AS vi ON v.id_venda = vi.id_venda
    INNER JOIN materiais_catalogo AS mc ON vi.id_material_catalogo = mc.id_material_catalogo
    WHERE
        c.deletado_em IS NULL
        AND mc.id_material_catalogo = 2
        AND vi.quantidade_kg > 0
),

-- CTE 2: Usa Funções de Janela para rankear as compras. (Sem alterações)
VendasRankeadas AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY cnpj ORDER BY quantidade_kg ASC) AS rank_menor,
        ROW_NUMBER() OVER(PARTITION BY cnpj ORDER BY quantidade_kg DESC) AS rank_maior
    FROM VendasIndividuais
)

-- Final: Usa agregação condicional para pivotar os resultados
SELECT
    razao_social,
    cnpj,

    -- Extrai o valor da coluna 'quantidade_kg' APENAS da linha que representa a menor venda
    MAX(CASE WHEN rank_menor = 1 THEN quantidade_kg END) AS venda_menor_kg,

    -- Extrai o valor da coluna 'valor_total' APENAS da linha que representa a menor venda
    MAX(CASE WHEN rank_menor = 1 THEN valor_total END) AS valor_total_venda_menor,

    -- Extrai o valor da coluna 'quantidade_kg' APENAS da linha que representa a maior venda
    MAX(CASE WHEN rank_maior = 1 THEN quantidade_kg END) AS venda_maior_kg,

    -- Extrai o valor da coluna 'valor_total' APENAS da linha que representa a maior venda
    MAX(CASE WHEN rank_maior = 1 THEN valor_total END) AS valor_total_venda_maior

FROM VendasRankeadas
WHERE rank_menor = 1 OR rank_maior = 1 -- Opcional, mas otimiza por reduzir os dados antes de agrupar
GROUP BY
    razao_social,
    cnpj
ORDER BY
    razao_social;


-- SELECT CONTAGEM DOS VALORES IFOOD


SELECT 
	f.texto,
	COUNT(f.texto) AS quantidade,
    c.razao_social,
    c.id_comprador,
    c.score_confianca,
    c.endereco,
    ac.data_avaliacao
FROM compradores AS c
INNER JOIN vendas AS v ON c.id_comprador = v.id_comprador
INNER JOIN avaliacoes_compradores AS ac ON v.id_venda = ac.id_venda
INNER JOIN avaliacao_feedback_selecionado AS afs ON ac.id_avaliacao = afs.id_avaliacao
INNER JOIN feedback_tags AS f ON afs.id_feedback_tag = f.id_feedback_tag
WHERE c.cnpj = '43948405000169'
GROUP BY f.texto
ORDER BY quantidade DESC;

select * from vendas;