from data.connection_controller import Connection
from controllers.email_controller import Email
from mysql.connector.connection import MySQLConnection
from controllers.tokens_controller import Tokens
from controllers.usuarios_controller import Usuarios

class Cooperativa:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def autenticar (self, email:str, senha:str) -> bool:

        """
        Verifica a existência de Cooperativa com
        o email e senha fornecidos e retorna seu
        código de sessão (Token)
        """

        if not isinstance(email, str) or not isinstance(senha, str):

            raise TypeError ('Cooperativa: "email" e "senha" devem ser do tipo String')

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT id_usuario FROM usuarios WHERE 
                    usuarios.email = %s 
                    AND usuarios.senha_hash = SHA2(%s, 256)
                    AND status = 'ativo';
                """,

                (email, senha)

            )

            data_user = cursor.fetchone()

            if data_user:

                return Tokens(self.connection_db).create(

                    data_user['id_usuario'],
                    ''

                )

            else:

                return False                

        except Exception as e:

            print(f'Erro - Cooperativa "autenticar": {e}')

            return False

        finally:

            cursor.close()

    def create (
        self,
        id_usuario: int,
        cnpj: str,
        razao_social: str,
        endereco: str | None,
        cidade: str | None,
        estado: str | None,
        latitude: str | None = None,
        longitude: str | None = None
    ) -> int | None:

        cursor = self.connection_db.cursor()
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

        if len(cnpj_limpo) != 14:
            print(f'Erro - Cooperativa "create": CNPJ formatado incorretamente: {cnpj}')
            return None

        try:
            cursor.execute(
                """
                INSERT INTO cooperativas (
                    id_usuario,
                    cnpj,
                    razao_social,
                    endereco,
                    cidade,
                    estado,
                    latitude,
                    longitude,
                    aprovado
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s,
                    FALSE
                )
                """, (
                    id_usuario,
                    cnpj_limpo,
                    razao_social,
                    endereco,
                    cidade,
                    estado,
                    latitude,
                    longitude
                )
            )

            return cursor.lastrowid

        except Exception as e:
            print(f'Erro - Cooperativa "create" ao inserir na DB: {e}')
            return None

        finally:
            if cursor:
                cursor.close()
    
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
