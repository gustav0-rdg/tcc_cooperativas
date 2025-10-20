import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

info_conexoes = {

    'local': {

        'host': 'localhost',
        'port': '3306',

        'user': 'root',
        'password': 'root',
        
        'database': 'recoopera' 

    },

    'online': {

        'host': '',
        'port': '',

        'user': '',
        'password': '',
        
        'database': '' 

    }

}

class Connection:

    connection_db:MySQLConnection=None,
    cursor:MySQLCursor=None

    def __init__ (self, tipo_conexao:str, is_dict:bool=True):

        if not tipo_conexao in info_conexoes:

            raise ValueError (f'Erro - Connection: Valor de "tipo_conexao" não é válido: {tipo_conexao}')

        try:

            self.connection_db = mysql.connector.connect(info_conexoes[tipo_conexao])
            self.cursor = self.connection_db.cursor(dict=is_dict)

        # mysql.connector.Error -> Principais erros relacionados ao MySql

        except mysql.connector.Error as e:

            print(f'Erro - Connection: Erro ao criar conexão com o Banco de Dados: {e}')

    def close (self) -> bool:

        try:

            self.connection_db.close()
            self.cursor.close()

            return True

        except mysql.connector.Error as e:

            print(f'Erro - Connection "close": {e}')

            return False
        
    @staticmethod
    def validar (connection_db:MySQLConnection, cursor:MySQLCursor):

        if isinstance(cursor, MySQLCursor) and isinstance(connection_db, MySQLConnection):

            return True
        
        else:

            return False