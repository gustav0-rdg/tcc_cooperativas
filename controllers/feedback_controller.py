import mysql.connector
from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection

class Feedbacks:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_all(self):
        """
        Busca todas as tags de feedback do banco de dados.
        É um método estático porque não depende de uma instância da classe.
        """
        conn = None
        cursor = None
        cursor = self.connection_db.cursor(dictionary=True)

        try:
            
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