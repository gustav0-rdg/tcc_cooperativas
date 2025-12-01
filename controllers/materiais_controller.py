import mysql.connector
from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection
from flask import jsonify

class Materiais:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_all(self, id_cooperativa: int = None):
        """
        Busca todos os materiais base. Se um id_cooperativa for fornecido,
        substitui os nomes dos materiais pelos sinônimos da cooperativa, se existirem.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            if id_cooperativa:
                # A query utiliza a view v_materiais_visiveis que já possui a lógica de sinônimos
                query = """
                    SELECT DISTINCT
                        id_material_base,
                        categoria AS nome_padrao
                    FROM v_materiais_visiveis
                    WHERE id_cooperativa = %s
                    ORDER BY categoria;
                """
                cursor.execute(query, (id_cooperativa,))
            else:
                # Query original para usuários não logados ou sem cooperativa
                query = """
                    SELECT id_material_base, nome as nome_padrao 
                    FROM materiais_base 
                    WHERE ativo = TRUE
                    ORDER BY ordem_exibicao, nome;
                """
                cursor.execute(query)

            materiais = cursor.fetchall()
            return materiais

        except mysql.connector.Error as e:
            print(f"Erro ao buscar os materiais: {e}")
            return []

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
            # Primeiro, encontrar um id_material_catalogo associado ao id_material_base
            cursor.execute(
                "SELECT id_material_catalogo FROM materiais_catalogo WHERE id_material_base = %s LIMIT 1",
                (id_material_base,)
            )
            material_catalogo = cursor.fetchone()

            if not material_catalogo:
                return jsonify({'message': 'Nenhum material de catálogo encontrado para a base fornecida.'}), 404

            id_material_catalogo = material_catalogo['id_material_catalogo']

            query = """
            INSERT INTO materiais_sinonimos (id_material_catalogo, nome_sinonimo, id_cooperativa)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (id_material_catalogo, sinonimo, id_cooperativa))
            self.connection_db.commit()
            return jsonify({'message': 'Sinônimo registrado com sucesso!'}), 200

        except mysql.connector.Error as error:
            print("Erro MySQL:", error)
            self.connection_db.rollback()
            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        finally:
            cursor.close()

    def cadastrar_material_base(self, nome_material, id_cooperativa):
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                self.connection_db.start_transaction()

                query_base = "INSERT INTO materiais_base(nome) VALUES(%s);"
                cursor.execute(query_base, (nome_material,))
                id_material_base = cursor.lastrowid

                query_catalogo = """
                INSERT INTO materiais_catalogo(id_material_base, nome_especifico, status, data_aprovacao)
                VALUES(%s, %s, 'aprovado', NOW());
                """
                cursor.execute(query_catalogo, (id_material_base, nome_material))
                id_material_catalogo = cursor.lastrowid

                query_sinonimo = """
                INSERT INTO materiais_sinonimos(id_material_catalogo, id_cooperativa, nome_sinonimo)
                VALUES(%s, %s, %s);
                """
                cursor.execute(query_sinonimo, (id_material_catalogo, id_cooperativa, nome_material))

                self.connection_db.commit()

                return jsonify({'message': 'Material registrado com sucesso!', 'id_material_base': id_material_base}), 200

        except mysql.connector.Error as error:
            print("Erro MySQL:", error)
            self.connection_db.rollback()
            return jsonify({'message': 'Erro ao salvar no banco de dados.'}), 500

        finally:
            cursor.close()

    def get_subtipos(self, id_material_base: int, id_cooperativa: int = None):
        """
        Busca todos os subtipos de um material. Se um id_cooperativa for fornecido,
        substitui os nomes dos subtipos pelos sinônimos da cooperativa, se existirem.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            if id_cooperativa:
                # Query que busca o nome do sinônimo ou o nome original
                query = """
                    SELECT
                        v.id_material_base,
                        v.id_material_catalogo,
                        v.nome_material AS nome_especifico,
                        v.nome_original,
                        v.descricao
                    FROM v_materiais_visiveis v
                    WHERE v.id_material_base = %s AND v.id_cooperativa = %s;
                """
                cursor.execute(query, (id_material_base, id_cooperativa))
            else:
                # Query original para usuários não logados
                query = """
                    SELECT 
                        mc.id_material_base,
                        mc.id_material_catalogo, 
                        mc.nome_especifico,
                        mc.nome_especifico AS nome_original,
                        mc.descricao
                    FROM materiais_catalogo AS mc
                    WHERE mc.id_material_base = %s AND mc.status = 'aprovado' AND mc.deletado_em IS NULL;
                """
                cursor.execute(query, (id_material_base,))
            
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao buscar subtipos: {e}")
            return []
        finally:
            cursor.close()
