import mysql.connector
from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ

class Compradores:
    def insert(cnpj):
        try:
            validar_cnpj = CNPJ.validar(cnpj)
            if not validar_cnpj:
                raise ValueError
            conn = Connection.create('local')
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO compradores(cnpj, razao_social, endereco, cidade, estado, telefone, email)
            """)
        except Exception as e:
            print(e)
