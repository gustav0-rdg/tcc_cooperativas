from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection

class Precos:
    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError("Erro - Precos: Conexão com o banco de dados inválida.")
        self.connection_db = connection_db

    def get_precos_mercado_anonimizado(self, estado=None, ano=None, mes=None):
        """
        Busca preços de mercado anonimizados por material, estado, ano e mês usando a view v_precos_mercado_anonimizado.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = "SELECT * FROM v_precos_mercado_anonimizado WHERE 1=1"
            params = []

            if estado:
                query += " AND estado = %s"
                params.append(estado)
            if ano:
                query += " AND ano = %s"
                params.append(ano)
            if mes:
                query += " AND mes = %s"
                params.append(mes)

            query += " ORDER BY ano DESC, mes DESC, material_nome"

            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Erro em 'get_precos_mercado_anonimizado': {e}")
            return []

        finally:
            cursor.close()

    def get_precos_regionais(self, material_id=None, estado=None):
        """
        Busca preços regionais por material e estado usando a tabela precos_regionais.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = "SELECT * FROM precos_regionais WHERE 1=1"
            params = []

            if material_id:
                query += " AND id_material_base = %s"
                params.append(material_id)
            if estado:
                query += " AND estado = %s"
                params.append(estado)

            query += " ORDER BY estado, id_material_base"

            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Erro em 'get_precos_regionais': {e}")
            return []

        finally:
            cursor.close()
