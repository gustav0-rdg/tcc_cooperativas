from data.connection_controller import Connection
from mysql.connector import Error

class Cooperativas:

    def get_by_cnpj (cnpj):

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT * FROM cooperativa
                WHERE cooperativa.cnpj = %s
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Error as e:

            print(f'Erro - Cooperativas "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()        