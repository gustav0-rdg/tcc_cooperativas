from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

class Tokens:

    def __init__(self, database:MySQLConnection, cursor:MySQLCursor):
        
        if not isinstance(cursor, MySQLCursor):

            raise TypeError ('Tokens Controller - "cursor" deve ser do tipo MySQLCursor')
        
        if not isinstance(database, MySQLConnection):

            raise TypeError ('Tokens Controller - "database" deve ser do tipo MySQLConnection')

        self.database = database
        self.cursor = cursor

    def create (
            
        self,

        id_usuario:int,
        tipo:str

    ) -> bool:
        
        if not isinstance(id_usuario, int) or not isinstance(tipo, str):

            raise TypeError ('Tokens Controller - "id_usuario" deve ser do tipo Int e "tipo" deve ser do tipo String')

        tipos_validos = ['']

        if not tipo in tipos_validos:

            raise ValueError (f'Tokens Controller - "tipo" deve ser um desses valores: {tipos_validos}')
        
        self.cursor.execute (

            """
            INSERT INTO tokens_validacao (id_token, tipo)
            VALUES (%s, %s);
            """

            (id_usuario, tipo)

        )

        self.database.commit()

        return self.cursor.rowcount > 0       

    def validar (self, token:str) -> bool:

        if not isinstance(token, str) or len(token) < 36:

            raise ValueError ('Tokens Controller - "token" deve ser do tipo String com 36 caractéres')

        self.cursor.execute (

            """
            SELECT
                id_token,
                token,
                tipo,
                usado
            FROM tokens_validacao
            INNER JOIN usuarios ON tokens_validacao.id_usuario = usuarios.id_usuario
            WHERE BYTE tokens_validacao.token = %s;
            """

            (token, )

        )

        return self.cursor.fetchone()
    
    def set_state (self, id_token:int) -> bool:

        if not isinstance(id_token, int):

            raise TypeError ('Tokens Controller - "id_token" deve ser do tipo Int')

        self.cursor.execute (

            """
            UPDATE tokens_validacao
            SET tokens_validacao.usado = TRUE
            WHERE tokens_validacao.id_token = %s;
            """

            (id_token, )

        )

        self.database.commit()

        return self.cursor.rowcount > 0