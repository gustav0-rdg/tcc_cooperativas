from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from mysql.connector import Error

class Cooperativa:

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

    # melhorar nome do metodo
    def ativar (cnpj:str) -> bool:

        """
        A função é a etapa final do cadastro, ativa
        a conta após o registro da cooperativa e sua
        confirmação via email
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativa
                SET cooperativa.estado = 'Confirmado'
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativas "ativar": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def delete (cnpj:str) -> bool:

        """
        Exclui permanentemente a cooperativa
        com o CNPJ fornecido do banco de dados
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                DELETE FROM cooperativa
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativas "delete": {e}')

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

        if not CNPJ.validar(cnpj):

            raise ValueError ('')

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            data_cooperativa = CNPJ.consultar(cnpj)

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