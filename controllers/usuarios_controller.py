from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
from controllers.tokens_controller import Tokens
import hashlib

class Usuarios:

    def __init__ (self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Usuarios: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    @staticmethod
    def criptografar (texto:str) -> str:

        texto = hashlib.sha256(texto.encode('utf-8'))
        
        return texto.hexdigest()
    
    def autenticar (self, email:str, senha:str) -> bool:

        """
        Verifica e autentica o usuário e
        retorna seu código de sessão (token)
        """

        if not isinstance(email, str) or not isinstance(senha, str):

            raise TypeError ('Cooperativa: "email" e "senha" devem ser do tipo String')

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            senha = Usuarios.criptografar(senha)

            cursor.execute (

                """
                SELECT
                    id_usuario
                FROM usuarios
                WHERE 
                    usuarios.email = %s
                AND
                    BYTE usuarios.senha_hash = %s;
                """,

                (email, senha)

            )

            data_user = cursor.fetchone()

            if data_user:

                return Tokens(self.connection_db).create(

                    data_user['id_usuario'],
                    'sessao'

                )

            else:

                return False                

        except Exception as e:

            print(f'Erro - Usuarios "autenticar": {e}')

            return False

        finally:

            cursor.close()

    def trocar_senha (self, id_usuario:int, nova_senha:str) -> bool:

        cursor = self.connection_db.cursor()

        try:

            nova_senha = Usuarios.criptografar(nova_senha)

            cursor.execute (

                """
                UPDATE usuarios
                SET usuarios.senha_hash = %s
                WHERE usuarios.id_usuario = %s;
                """,

                (id_usuario, nova_senha)

            )

            return True               

        except Exception as e:

            print(f'Erro - Usuarios "trocar_senha": {e}')

            return False

        finally:

            cursor.close()