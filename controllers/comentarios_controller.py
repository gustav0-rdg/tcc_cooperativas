from data.connection_controller import Connection

class Comentarios:
    def __init__(self, connection_db):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos')
        self.connection_db = connection_db

    def get_feedback_tags(self, cnpj):
        query_sql = """
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
        WHERE c.cnpj = %s
        GROUP BY f.texto
        ORDER BY quantidade DESC;
        """
        results = []
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                cursor.execute(query_sql, tuple(cnpj))
                results = cursor.fetchall()
                if results.length == 0:
                    return []
        except Exception as e:
            print(e)
        return results