import mysql.connector
from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection
from flask import jsonify

class Materiais:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_all(self):
        """
        Busca todos os materiais cadastrados no catálogo do banco de dados.

        Utiliza a classe 'Connection' para estabelecer a conexão.

        Retorna:
            list: Uma lista de dicionários, onde cada dicionário representa um material.
                Retorna uma lista vazia em caso de erro ou se nenhum material for encontrado.
        """
        cursor = self.connection_db.cursor(dictionary=True)

        try:

            # O argumento dictionary=True faz com que os resultados venham como dicionários
            query = "SELECT id_material_catalogo, nome_padrao, descricao, categoria, imagem_url FROM materiais_catalogo"
            cursor.execute(query)

            # 4. Busca todos os resultados
            materiais = cursor.fetchall()
            
            return materiais

        except mysql.connector.Error as e:
            print(f"Erro ao buscar os materiais: {e}")
            return [] # Retorna uma lista vazia em caso de erro

        finally:
            cursor.close()

    def post_cadastrar_sinonimo(self, nome_padrao, sinonimo, id_cooperativa):
        cursor = self.connection_db.cursor(dictionary=True)
        

        try:
            

            query = """
            INSERT INTO materiais_sinonimos (id_material_catalogo, sinonimo, id_cooperativa)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nome_padrao, sinonimo))

            return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200

        except mysql.connector.Error as error:
            print("Erro MySQL:", error)
            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        finally:
            cursor.close()

