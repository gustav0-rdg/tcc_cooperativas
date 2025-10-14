import mysql.connector
from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ

class Compradores:
    
    def create(cnpj):
        conn = Connection.create('local')
        cursor = conn.cursor()
        try:
            validar_cnpj = CNPJ.validar(cnpj)
            data = CNPJ.consultar(cnpj)
            cnpj = data.get('taxId')
            razao_social = data.get('company', {}).get('name')

            # Para o endereço, vamos concatenar as partes
            endereco_info = data.get('address', {})
            rua = endereco_info.get('street', '')
            numero = endereco_info.get('number', '')
            bairro = endereco_info.get('district', '')
            complemento = endereco_info.get('details', '')
            endereco = f"{rua}, {numero} - {bairro} - {complemento}"

            cidade = endereco_info.get('city')
            estado = endereco_info.get('state')

            # Para telefone e email, pegamos o primeiro item da lista (se existir)
            telefone_info = data.get('phones', [{}])[0]
            telefone = f"({telefone_info.get('area')}) {telefone_info.get('number')}" if telefone_info else None

            email_info = data.get('emails', [{}])[0]
            email = email_info.get('address') if email_info else None

            print(cnpj, razao_social, endereco, cidade, estado, telefone, email)
            
            cursor.execute("""
                    INSERT INTO compradores(cnpj, razao_social, endereco, cidade, estado, telefone, email) VALUES (%s,%s,%s,%s,%s,%s,%s);
            """, (cnpj, razao_social, endereco,cidade, estado, telefone, email))
            conn.commit()

        except Exception as e:
            print(e)

        finally:
            conn.close()

    def get_all():
        conn = Connection.create('local')
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
            SELECT razao_social, cnpj, email, telefone, endereco, cidade, estado, score_confianca
            FROM compradores 
        """, ())
            dados = cursor.fetchall()

            return dados or []
        except Exception as e:
            print(e)
        finally: 
            conn.close()

    