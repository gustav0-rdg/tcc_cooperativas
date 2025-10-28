from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection
from datetime import datetime

class Tokens:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Tokens: Valores inválidos para os parâmetros "connection_db": {connection_db}')

        self.connection_db = connection_db

    def create (
            
        self,

        id_usuario:int,
        tipo:str,
        data_expiracao:datetime

    ) -> bool:
        
        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Tokens - "id_usuario" deve ser do tipo Int')
        
        if not isinstance(tipo, str):

            raise TypeError ('Tokens - "tipo" deve ser do tipo String')

        tipos_validos = ['cadastro', 'recuperacao_senha', 'sessao']

        if not tipo in tipos_validos:

            raise ValueError (f'Tokens - O parâmetro "tipo" deve receber um desses valores: {tipos_validos} mas recebeu: "{tipo}"')

        #endregion
        
        cursor = self.connection_db.cursor(dictionary=True)

        try:

            # Apaga os tokens anteriores pois esta
            # credencial deve ser única

            cursor.execute (

                """
                DELETE FROM tokens_validacao
                WHERE 
                    tokens_validacao.id_usuario = %s
                AND
                    tokens_validacao.tipo = %s;
                """,

                (id_usuario, tipo)

            )

            cursor.execute (

                """
                INSERT INTO tokens_validacao (id_usuario, tipo, data_expiracao)
                VALUES (%s, %s, %s);
                """,

                (id_usuario, tipo, data_expiracao)

            )

            cursor.execute (

                """
                SELECT
                    tokens_validacao.token
                FROM tokens_validacao
                WHERE tokens_validacao.id_token = %s;
                """,

                (cursor.lastrowid, )

            )

            token = cursor.fetchone()['token']
            
            self.connection_db.commit()
            if cursor.rowcount > 0 and token:

                return token

            else:

                return False

        except Exception as e:

            print(f'Erro - Tokens "create": {e}')

            return False

        finally:

            cursor.close() 

    def validar (self, token:str) -> bool:

        #region Exceções

        if not isinstance(token, str):

            raise TypeError ('Tokens - "token" deve ser do tipo String')
        
        if len(token) != 36:

            raise ValueError ('Tokens - "token" deve ter 36 caractéres')
        
        #endregion

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT
                    id_token,
                    id_usuario,
                    token,
                    tipo,
                    usado
                FROM tokens_validacao
                WHERE tokens_validacao.token = %s;
                """,

                (token, )

            )

            return cursor.fetchone()
        
        except Exception as e:

            print(f'Erro - Tokens "validar": {e}')

            return False
        
        finally:

            cursor.close()
    
    def set_state (self, id_token:int) -> bool:

        #region Exceções

        if not isinstance(id_token, int):

            raise TypeError ('Tokens - "id_usuario" deve ser do tipo Int')
        
        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE tokens_validacao
                SET tokens_validacao.usado = TRUE
                WHERE tokens_validacao.id_token = %s;
                """,

                (id_token, )

            )

            self.connection_db.commit()
            return cursor.rowcount > 0
    
        except Exception as e:

            print(f'Erro - Tokens "set_state": {e}')

            return False
        
        finally:

            cursor.close()

    def get_ultimo_token_por_usuario (self, id_usuario:int, tipo:str) -> str | None:

        """
        Busca o token (string) mais recente, válido e não usado 
        de um usuário específico.
        """

        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT token FROM tokens_validacao 
                WHERE id_usuario = %s 
                  AND tipo = %s 
                  AND usado = FALSE
                  AND data_expiracao > NOW()
                ORDER BY data_criacao DESC 
                LIMIT 1
                """,
                (id_usuario, tipo)
            )
            data = cursor.fetchone()
            return data['token'] if data else None
        
        except Exception as e:
            print(f'Erro - Tokens "get_last_token_by_user": {e}')
            return None
        
        finally:
            cursor.close()