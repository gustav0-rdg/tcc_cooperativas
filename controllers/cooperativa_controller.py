from data.connection_controller import Connection
from mysql.connector import Error
import requests

class Cooperativas:

    def get_by_cnpj (cnpj:str) -> bool:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor(dictionary=True)

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

    def create (
            
        __self__,

        cnpj:str,

        email:str,
        senha:str

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        """

        if not __self__.validar_cnpj(cnpj):

            raise ValueError ('')

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            data_cooperativa = __self__.consulta_cnpj(cnpj)

            if not data_cooperativa:

                return False

            cursor.execute (

                """
                INSERT INTO cooperativa (cnpj, email, senha, estado)
                VALUES (%s, %s, %s, 'Aguardando Confirmação');
                """,

                (cnpj, email, senha)

            )

            connection_db.commit()

            if cursor.rowcount > 0:

                # Enviar Email

                pass

            else:

                return False

        except Error as e:

            print(f'Erro - Cooperativas "create": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()