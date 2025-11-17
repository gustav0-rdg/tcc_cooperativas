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
        Busca todos os materiais base para o filtro de busca de compradores.

        Utiliza a classe 'Connection' para estabelecer a conexão.

        Retorna:
            list: Uma lista de dicionários, onde cada dicionário representa um material base com id_material_base e nome.
                Retorna uma lista vazia em caso de erro ou se nenhum material for encontrado.
        """
        cursor = self.connection_db.cursor(dictionary=True)

        try:

            # O argumento dictionary=True faz com que os resultados venham como dicionários
            query = "SELECT id_material_base, nome FROM materiais_base"
            cursor.execute(query)

            # 4. Busca todos os resultados
            materiais = cursor.fetchall()

            return materiais

        except mysql.connector.Error as e:
            print(f"Erro ao buscar os materiais: {e}")
            return [] # Retorna uma lista vazia em caso de erro

        finally:
            cursor.close()

    def cadastrar_subtipo(self, nome_especifico, id_material_base):
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                INSERT INTO materiais_catalogo(id_material_base, nome_especifico)
                VALUES(%s,%s);
                """
                cursor.execute(query, (id_material_base, nome_especifico))
                self.connection_db.commit()
                return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200

        except mysql.connector.Error as error:

            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        
        finally:
            cursor.close()

    def post_cadastrar_sinonimo(self, nome_padrao, sinonimo, id_cooperativa):
        cursor = self.connection_db.cursor(dictionary=True)


        try:


            query = """
            INSERT INTO materiais_sinonimos (id_material_catalogo, nome_sinonimo, id_cooperativa)
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

    def post_cadastrar_sinonimo_base(self, id_material_base, sinonimo, id_cooperativa):
        cursor = self.connection_db.cursor(dictionary=True)

        try:
            query = """
            INSERT INTO materiais_sinonimos_base (id_material_base, nome_sinonimo, id_cooperativa)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (id_material_base, sinonimo, id_cooperativa))
            self.connection_db.commit()
            return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200

        except mysql.connector.Error as error:
            print("Erro MySQL:", error)
            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        finally:
            cursor.close()

    def cadastrar_material_base(self, nome_material, id_cooperativa):
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                INSERT INTO materiais_base(nome)
                VALUES(%s);
                """
                cursor.execute(query, (nome_material,))
                id_novo = cursor.lastrowid
                self.connection_db.commit()

                # Cadastrar sinônimo para a cooperativa
                query_sinonimo = """
                INSERT INTO materiais_sinonimos_base(id_material_base, nome_sinonimo, id_cooperativa)
                VALUES(%s, %s, %s);
                """
                cursor.execute(query_sinonimo, (id_novo, nome_material, id_cooperativa))
                self.connection_db.commit()

                return jsonify({'message': 'Material registrado com sucesso!', 'id_material_base': id_novo}), 200

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
    
