from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.email_controller import Email
from mysql.connector.connection import MySQLConnection
from controllers.tokens_controller import Tokens
from controllers.usuarios_controller import Usuarios

class Cooperativa:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def get_by_cnpj (self, cnpj:str) -> bool:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        #region Exceções

        if not isinstance(cnpj, str):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo String')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT * FROM cooperativa
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()

    def alterar_aprovacao (self, cnpj:str, aprovado:bool) -> bool:
        
        """
        Altera o estado de aprovação da
        cooperativa, variando entre True or False
        """

        #region Exceções

        if not isinstance(cnpj, str):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo String')
        
        if not isinstance(aprovado, bool):

            raise TypeError ('Cooperativa - "aprovado" deve ser do tipo Booleano')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativas
                SET cooperativas.aprovado = %s
                WHERE cooperativas.cnpj = %s;
                """,

                (aprovado, cnpj)

            )

            self.connection_db.commit()
            return cursor.rowcount > 0

        except Exception as e:

            print(f'Erro - Cooperativa "alterar_aprovacao": {e}')

            return False

        finally:

            cursor.close()

    def create (
            
        self,

        cnpj:str,
        id_usuario:str

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        e relaciona-a com o usuário
        """

        #region Exceções

        if not CNPJ.validar(cnpj):

            raise ValueError (f'Cooperativa "create" - O "cnpj" fornecido não é válido: {cnpj}')
        
        #endregion

        cursor = self.connection_db.cursor()

        try:

            data_cooperativa = CNPJ.consultar(cnpj)

            if not data_cooperativa:

                return False
            
            cursor.execute (

                """
                INSERT INTO cooperativas (id_usuario, cnpj, razao_social, endereco, cidade, estado, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,

                (
                    id_usuario, 
                    cnpj,

                    data_cooperativa['nature']['id'],
                    f'{data_cooperativa['address']['street']}, {data_cooperativa['address']['number']}',    
                    data_cooperativa['address']['city'],
                    data_cooperativa['address']['state'],
                    '',
                    ''       
                )

            )

            self.connection_db.commit()
            return cursor.lastrowid

        except Exception as e:

            print(f'Erro - Cooperativa "create": {e}')

            return False
        
        finally:

            cursor.close()