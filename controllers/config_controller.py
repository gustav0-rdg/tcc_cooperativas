from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
from typing import Dict, Any, Optional

class ConfigController:
    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - ConfigController: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_config_value(self, chave: str) -> Optional[Any]:
        """
        Busca o valor de uma configuração do sistema pela chave.
        Converte o valor para o tipo correto (int, float, boolean).
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = "SELECT valor, tipo_valor FROM config_sistema WHERE chave = %s"
                cursor.execute(query, (chave,))
                result = cursor.fetchone()
                if result:
                    value = result['valor']
                    value_type = result['tipo_valor']
                    
                    if value_type == 'int':
                        return int(value)
                    elif value_type == 'float':
                        return float(value)
                    elif value_type == 'boolean':
                        return value.lower() == 'true' or value == '1'
                    elif value_type == 'json':
                        import json
                        return json.loads(value)
                    return value
                return None
        except Exception as e:
            print(f"Erro em get_config_value para a chave {chave}: {e}")
            return None

    def get_all_configs(self) -> Dict[str, Any]:
        """
        Busca todas as configurações do sistema e retorna como um dicionário.
        """
        configs = {}
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = "SELECT chave, valor, tipo_valor FROM config_sistema"
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    key = result['chave']
                    value = result['valor']
                    value_type = result['tipo_valor']

                    if value_type == 'int':
                        configs[key] = int(value)
                    elif value_type == 'float':
                        configs[key] = float(value)
                    elif value_type == 'boolean':
                        configs[key] = value.lower() == 'true' or value == '1'
                    elif value_type == 'json':
                        import json
                        configs[key] = json.loads(value)
                    else:
                        configs[key] = value
            return configs
        except Exception as e:
            print(f"Erro em get_all_configs: {e}")
            return {}

