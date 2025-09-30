from data.connection_controller import Connection
from mysql.connector import Error
import requests

class Cooperativas:

    def get_by_cnpj (cnpj:str) -> bool:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT * FROM cooperativa
                WHERE cooperativa.cnpj = %s
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Error as e:

            print(f'Erro - Cooperativas "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def validar_cnpj (cnpj:str) -> bool:

        """
        Valida matematicamente se o CNPJ fornecido é válido, 
        sem consulta a qualquer API.
        Referência: https://pt.wikipedia.org/wiki/Cadastro_Nacional_da_Pessoa_Jur%C3%ADdica?utm_source=chatgpt.com#Algoritmo_de_Valida%C3%A7%C3%A3o[carece_de_fontes?]
        """

        # Mínimo 14 digítos

        if len(cnpj) != 14:

            return False
        
        # Elimina sequências com todos os digítos repetidos

        if cnpj == cnpj[0] * 14:

            return False
        
        # Os pesos são fixos e padronizados para a validação do CNPJ

        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        # O resto da soma de todos os digítos multiplicados pelo respectivo peso
        # se menor que 2 retorna 0, se não '11 - resto'

        def calcular_digito (base:str, pesos:list[int]) -> str:

            soma = 0

            for digito, peso in zip(base, pesos):

                soma += int(digito) * peso

            resto = soma % 11

            if resto < 2:

                return 0
            
            else:

                return 11 - resto

        # '[start:end]' -> Retorna os elementos do index de 'start' ao 'end'
        # Funciona para listas, tuplas e strings

        digito_verificador_1 = calcular_digito(cnpj[:12], pesos[1:])
        digito_verificador_2 = calcular_digito(cnpj[:12] + digito_verificador_1, pesos)

        # Se os dois digitos calculados foram iguais
        # aos dois últimos digitos do CNPJ fornecido
        # ele é matematicamente válido

        return cnpj[-2:] == digito_verificador_1 + digito_verificador_2

    def consulta_cnpj (cnpj:str) -> dict:

        url = 'https://open.cnpja.com/office/' + cnpj

        response = requests.get(url)
        response_json = response.json()

        if hasattr(response_json, 'code') and (response_json['code'] == 404 or response_json['code'] == 400):

            return False

        return response_json

    # melhorar nome do metodo
    def ativar (cnpj:str) -> bool:

        """
        A função é a etapa final do cadastro, ativa
        a conta após o registro da cooperativa e sua
        confirmação via email
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativa
                SET cooperativa.estado = 'Confirmado'
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativas "ativar": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def create (
            
        __self__,

        cnpj:str,

        email:str,
        senha:str

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        """

        if not __self__.validar_cnpj(cnpj):

            raise ValueError ('')

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            data_cooperativa = __self__.consulta_cnpj(cnpj)

            if not data_cooperativa:

                return False

            cursor.execute (

                """
                INSERT INTO cooperativa (cnpj, email, senha, estado)
                VALUES (%s, %s, %s, 'Aguardando Confirmação');
                """,

                (cnpj, email, senha)

            )

            connection_db.commit()

            if cursor.rowcount > 0:

                # Enviar Email

                pass

            else:

                return False

        except Error as e:

            print(f'Erro - Cooperativas "create": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()