import mysql

class Connection:

    def create ():

        try:

            return mysql.connector.connect (

                host = '',
                port = '',

                user = '',
                password = '',
                
                database = ''

            )

        # mysql.connector.Error -> Principais erros relacionados ao MySql

        except mysql.connector.Error as e:

            print(f'Erro - Connection "create": {e}')

            return False