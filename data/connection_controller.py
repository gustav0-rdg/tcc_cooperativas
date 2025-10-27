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
        
        'database': 'recoopera' 

    }

}

class Connection:
    connection_db: MySQLConnection = None

    def __init__(self, tipo_conexao: str):
        if not tipo_conexao in info_conexoes:
            raise ValueError(f'Erro - Connection: Tipo de conexão inválido: {tipo_conexao}')

        try:
            print(f"Tentando conectar a: {info_conexoes[tipo_conexao]['host']}...") # Log
            self.connection_db = mysql.connector.connect(**info_conexoes[tipo_conexao])
            print("Conexão bem-sucedida!") 

        except mysql.connector.Error as e:
            print(f'Erro FATAL - Connection: Erro ao criar conexão: {e}')
            self.connection_db = None
            raise ConnectionError(f"Falha ao conectar à base de dados: {e}") from e
        
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