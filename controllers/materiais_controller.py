import mysql.connector
from data.connection_controller import Connection

class Materiais:
    def get_all():
        """
        Busca todos os materiais cadastrados no catálogo do banco de dados.

        Utiliza a classe 'Connection' para estabelecer a conexão.

        Retorna:
            list: Uma lista de dicionários, onde cada dicionário representa um material.
                Retorna uma lista vazia em caso de erro ou se nenhum material for encontrado.
        """
        conn = None  # Inicializa a variável de conexão
        try:
            # 1. Cria a conexão usando a sua classe
            conn = Connection.create('local') 

            # Verifica se a conexão foi bem-sucedida
            if not conn:
                print("Falha ao estabelecer a conexão com o banco de dados.")
                return []

            # 2. Cria o cursor para executar comandos SQL
            # O argumento dictionary=True faz com que os resultados venham como dicionários
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id_material_catalogo, nome_padrao, descricao, categoria, imagem_url FROM materiais_catalogo"
            cursor.execute(query)

            # 4. Busca todos os resultados
            materiais = cursor.fetchall()
            
            return materiais

        except mysql.connector.Error as e:
            print(f"Erro ao buscar os materiais: {e}")
            return [] # Retorna uma lista vazia em caso de erro

        finally:
            # 5. Garante que a conexão seja fechada ao final
            if conn and conn.is_connected():
                cursor.close()
                conn.close()