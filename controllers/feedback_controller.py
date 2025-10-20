import mysql.connector
from data.connection_controller import Connection

class Feedbacks:
    @staticmethod
    def get_all():
        """
        Busca todas as tags de feedback do banco de dados.
        É um método estático porque não depende de uma instância da classe.
        """
        conn = None
        cursor = None
        try:
            conn = Connection.create('local')
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id_feedback_tag, texto, tipo FROM feedback_tags"
            cursor.execute(query)
            feedbacks = cursor.fetchall()
            
            # 4. Retorne a lista de feedbacks
            return feedbacks

        except mysql.connector.Error as e:
            print(f"Ocorreu um erro ao buscar os feedbacks: {e}")
            return [] # Retorna uma lista vazia em caso de erro

        finally:
            # garantindo conexão sempre fechada
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()