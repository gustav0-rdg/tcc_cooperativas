import mysql.connector
from mysql.connector import MySQLConnection

info_conexoes = {

    'local': {

        'host': 'localhost',
        'port': '3306',

        'user': 'root',
        'password': 'root',
        
        'database': 'recoopera' 

    },

    'online': {

        'host': 'db-recoopera.mysql.database.azure.com',
        'port': '3306',

        'user': 'godofredo',
        'password': '33351065Aa!',
        
        'database': 'db-recoopera' 

    }

}

class Connection:

    connection_db:MySQLConnection = None

    def __init__ (self, tipo_conexao:str):

        if not tipo_conexao in info_conexoes:

            raise ValueError (f'Erro - Connection: Valor de "tipo_conexao" não é válido: {tipo_conexao}')

        try:

            self.connection_db = mysql.connector.connect(**info_conexoes[tipo_conexao])

        # mysql.connector.Error -> Principais erros relacionados ao MySql

        except mysql.connector.Error as e:

            print(f'Erro - Connection: Erro ao criar conexão com o Banco de Dados: {e}')

    def close (self) -> bool:

        try:

            self.connection_db.close()

            return True

        except mysql.connector.Error as e:

            print(f'Erro - Connection "close": {e}')

            return False
        
    @staticmethod
    def validar (connection_db:MySQLConnection) -> bool:

        if isinstance(connection_db, MySQLConnection) and connection_db.is_connected():

            return True
        
        else:

            return False