import requests

class CNPJ:

    @staticmethod
    def validar (cnpj:str) -> bool:
        """
        Valida CNPJ matematicamente, sem API.
        """
        if len(cnpj) != 14:
            return False

        # Remove sequências repetidas
        if cnpj == cnpj[0] * 14:
            return False

        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        def calcular_digito (base:str, pesos:list[int]) -> str:
            soma = 0
            for digito, peso in zip(base, pesos):
                soma += int(digito) * peso
            resto = soma % 11
            if resto < 2:
                return 0
            else:
                return 11 - resto

        digito_verificador_1 = calcular_digito(cnpj[:12], pesos[1:])
        digito_verificador_2 = calcular_digito(cnpj[:12] + str(digito_verificador_1), pesos)

        # Verifica dígitos calculados
        return cnpj[-2:] == str(digito_verificador_1) + str(digito_verificador_2)

    @staticmethod
    def consultar (cnpj:str) -> dict:
        """
        Consulta dados do CNPJ via API.
        """
        url = 'https://open.cnpja.com/office/' + cnpj

        response = requests.get(url)
        response_json = response.json()

        if hasattr(response_json, 'code') and (response_json['code'] == 404 or response_json['code'] == 400):
            return False

        return response_json
