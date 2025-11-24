from data.connection_controller import Connection

class Comentarios:
    def __init__(self, connection_db):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos')
        self.connection_db = connection_db

    def get_feedback_tags(self, cnpj):
        query_sql = """
        SELECT
            feedback_texto AS texto,
            feedback_tipo AS tipo,
            quantidade_mencoes AS quantidade
        FROM v_feedback_comprador_agregado
        WHERE cnpj = %s
        ORDER BY quantidade_mencoes DESC;
        """
        results = []
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                cursor.execute(query_sql, (cnpj,))
                results = cursor.fetchall()
        except Exception as e:
            print(e)
        return results
    
    def get_comentarios(self, cnpj):
        query = """
        SELECT
            ac.comentario_livre
        FROM avaliacoes_compradores ac
        INNER JOIN vendas v ON ac.id_venda = v.id_venda
        INNER JOIN compradores co ON v.id_comprador = co.id_comprador
        WHERE co.cnpj = %s AND ac.comentario_livre IS NOT NULL AND ac.comentario_livre != ''
        ORDER BY ac.data_avaliacao DESC
        LIMIT 5;
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (cnpj, ))
                results = cursor.fetchall()

        except Exception as e:
            print(e)

        finally:
            return results
