from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection

class Gestor:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Gestor: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def toggle_estado_usuario (self, id_usuario:int, estado:str) -> bool:

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Gestor: "id_usuario" deve ser do tipo Int')
        
        if not isinstance(estado, bool):

            raise TypeError ('Gestor: "estado" deve ser do tipo String')
        
        estados_validos = ['ativo', 'bloqueado', 'inativo']
        if not estado in estados_validos:

            raise TypeError (f'Gestor: "estado" deve ser um desses valores: {estados_validos}')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT usuarios.id_usuario FROM usuarios
                WHERE usuarios.id_usuario = %s;
                """,

                (id_usuario, )

            )

            # Usuário não encontrado

            if cursor.fetchone() == None:
                return None

            cursor.execute (

                """
                UPDATE usuarios
                SET usuarios.status = %s
                WHERE usuarios.id_usuario = %s;
                """,

                (estado, id_usuario)

            )

            self.connection_db.commit()
            return cursor.rowcount > 0 or None

        except Exception as e:

            print(f'Erro - Gestor "toggle_estado_usuario": {e}')

            return False

        finally:

            cursor.close()