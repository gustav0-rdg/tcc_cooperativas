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
        if tipo_conexao not in info_conexoes:
            raise ValueError(f'Erro - Connection: Valor de "tipo_conexao" não é válido: {tipo_conexao}')

        config = info_conexoes[tipo_conexao].copy() 

        if tipo_conexao == 'online':
            print("Configurando SSL para conexão online...")

            config['ssl_disabled'] = False
            config['ssl_verify_cert'] = True

        print(f"Tentando conectar a: {config.get('host')}...") 
        try:
            # Usa a configuração (com ou sem SSL adicionado)
            self.connection_db = mysql.connector.connect(**config)
            print("Conexão bem-sucedida!")

        except mysql.connector.Error as e:
            print(f'Erro - Connection: Erro ao criar conexão com o Banco de Dados ({tipo_conexao}): {e}')
            self.connection_db = None

    def close (self) -> bool:
        if self.connection_db and self.connection_db.is_connected():
            try:
                self.connection_db.close()
                print("Conexão fechada.") # Log
                return True
            except mysql.connector.Error as e:
                print(f'Erro - Connection "close": {e}')
                return False
        elif self.connection_db is None:
             print("Aviso - Connection 'close': Tentativa de fechar uma conexão que falhou ao ser criada.")
             return False 
        else:
             print("Aviso - Connection 'close': Conexão já estava fechada.")
             return True 

    @staticmethod
    def validar (connection_db:MySQLConnection) -> bool:

        if isinstance(connection_db, MySQLConnection) and connection_db.is_connected():
            return True
        else:

            if not isinstance(connection_db, MySQLConnection):
                 print("Connection.validar falhou: Objeto não é MySQLConnection.")
            elif not connection_db.is_connected():
                 print("Connection.validar falhou: is_connected() retornou False.")
            return False