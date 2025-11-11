import mysql.connector


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
    """Gerencia uma conexão por instância (NUNCA compartilhada entre requests).
    Uso: conn = Connection('local')
    db = conn.connection_db
    ...
    conn.close()
    """

    def __init__(self, tipo_conexao: str = 'local'):
        tipo_conexao='online'
        if tipo_conexao not in info_conexoes:
            raise ValueError(f'Erro - Connection: Valor de "tipo_conexao" não é válido: {tipo_conexao}')

        config = info_conexoes[tipo_conexao].copy()

        try:
            print(f"Tentando conectar a: {config.get('host')}...")
            self.connection_db = mysql.connector.connect(**config)
            print("Conexão bem-sucedida!")

        except mysql.connector.Error as e:
            print(f'Erro - Connection: Erro ao criar conexão com o Banco de Dados ({tipo_conexao}): {e}')
            self.connection_db = None

    def close(self) -> bool:

        if self.connection_db is None:
            print("Aviso - Connection 'close': Conexão inexistente.")
            return False

        try:
            if self.connection_db.is_connected():
                self.connection_db.close()
                print("Conexão fechada.")
                return True
            else:
                print("Aviso - Connection 'close': Conexão já estava fechada.")
                return True
        except mysql.connector.Error as e:
            print(f'Erro - Connection "close": {e}')
            return False

    @staticmethod
    def validar(connection_db) -> bool:
        
        try:
            return connection_db is not None and connection_db.is_connected()
        except Exception:
            return False
