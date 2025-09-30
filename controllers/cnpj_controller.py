import requests

class CNPJ:

    @staticmethod
    def validar (cnpj:str) -> bool:

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
    
    @staticmethod
    def consultar (cnpj:str) -> dict:

        url = 'https://open.cnpja.com/office/' + cnpj

        response = requests.get(url)
        response_json = response.json()

        if hasattr(response_json, 'code') and (response_json['code'] == 404 or response_json['code'] == 400):

            return False

        return response_json
