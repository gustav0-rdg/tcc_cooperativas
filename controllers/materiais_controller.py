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
            query = "SELECT id_material_base as id_material_catalogo, nome as nome_padrao, descricao FROM materiais_base"
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
            INSERT INTO materiais_apelidos (id_material_catalogo, nome_regional, id_apelido)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nome_padrao, sinonimo, id_cooperativa))
            self.connection_db.commit()
            return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200


        except mysql.connector.Error as error:
            print("Erro MySQL:", error)
            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        finally:
            cursor.close()

    def get_subtipos(self, id_material_base):
        """
        Busca todos os materiais cadastrados no catálogo do banco de dados.

        Utiliza a classe 'Connection' para estabelecer a conexão.

        Retorna:
            list: Uma lista de dicionários, onde cada dicionário representa um subtipo de um determinado material.
                Retorna uma lista vazia em caso de erro ou se nenhum material for encontrado.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT 
                    mc.id_material_base,
                    mc.id_material_catalogo, 
                    mc.nome_especifico, 
                    mc.descricao
                FROM materiais_catalogo AS mc
                WHERE 
                    mc.id_material_base = %s
                GROUP BY 
                    -- Agrupa os resultados por material
                    mc.id_material_catalogo, 
                    mc.nome_especifico, 
                    mc.descricao;
                """
                cursor.execute(query, (id_material_base,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(e)
            return []
    
