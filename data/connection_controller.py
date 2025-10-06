import mysql

class Connection:

    def create (tipo_conexao: str):

        try:

            # Conecta utilizando uma database local
            if tipo_conexao == 'local':

                return mysql.connector.connect (

                    host = 'localhost',
                    port = '3306',

                    user = 'root',
                    password = 'root',
                    
                    database = 'recoopera' 

                )
            
            # Cria uma conexão utilizando um host online
            elif tipo_conexao == 'online':

                return mysql.connector.connect (
                
                    # Preencher com base no host utilizado
                    host = '',
                    port = '',

                    user = '',
                    password = '',
                    
                    database = ''

                )
            
            else:
                   
                   raise ValueError("Método para conexão inválido!\nInsira um tipo válido para a conexão (local, online).")


        # mysql.connector.Error -> Principais erros relacionados ao MySql

        except mysql.connector.Error as e:

            print(f'Erro - Connection "create": {e}')

            return False