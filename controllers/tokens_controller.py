import os
import binascii
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

        if not isinstance(id_usuario, int):
            raise TypeError ('id_usuario deve ser int')

        if not isinstance(tipo, str):
            raise TypeError ('tipo deve ser string')

        tipos_validos = ['validacao_email', 'recuperacao_senha', 'sessao']

        if not tipo in tipos_validos:
            raise ValueError (f'tipo deve ser um de: {tipos_validos}, recebeu: "{tipo}"')

        cursor = self.connection_db.cursor(dictionary=True)

        try:
            # Remove tokens antigos para manter único
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

            token = binascii.hexlify(os.urandom(32)).decode()

            cursor.execute (

                """
                INSERT INTO tokens_validacao (id_usuario, tipo, data_expiracao, token)
                VALUES (%s, %s, %s, %s);
                """,

                (id_usuario, tipo, data_expiracao, token)

            )

            self.connection_db.commit()
            if cursor.rowcount > 0 and token:
                return token
            else:
                return False

        except Exception as e:
            print(f'Erro em create: {e}')
            return False

        finally:
            cursor.close()

    def validar (self, token:str) -> dict | None:

        if not isinstance(token, str):
            return None

        if len(token) != 64:
            return None

        cursor = self.connection_db.cursor(dictionary=True, buffered=True)

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
                WHERE tokens_validacao.token = %s
                AND usado = FALSE
                AND data_expiracao > NOW();
                """,

                (token, )

            )

            return cursor.fetchone()

        except Exception as e:
            print(f'Erro em validar: {e}')
            return None

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
        Busca token mais recente, válido e não usado do usuário.
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
            print(f'Erro em get_ultimo_token_por_usuario: {e}')
            return None

        finally:
            cursor.close()
