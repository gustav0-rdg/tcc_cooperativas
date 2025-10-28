class CPF:

    @staticmethod
    def validar (cpf:str) -> bool:

        """
        Valida matematicamente se o CPF fornecido é válido, 
        sem consulta a qualquer API.
        """

        if not isinstance(cpf, str):

            raise TypeError ('Cooperativa - "cpf" deve ser do tipo String')

        # Verifica se tem 11 dígitos

        if len(cpf) != 11:

            return False
        
        # Verifica se todos os dígitos são iguais, que é inválido

        if cpf == cpf[0] * 11:

            return False
        
        # Função interna para calcular cada dígito verificador

        def calcular_digito (base: str, peso_inicial: int) -> int:

            soma = 0

            for i, digito in enumerate(base):

                soma += int(digito) * (peso_inicial - i)

            resto = soma % 11

            return 0 if resto < 2 else 11 - resto
        
        digito_verificador_1 = calcular_digito(cpf[:9], 10)
        digito_verificador_2 = calcular_digito(cpf[:9] + str(digito_verificador_1), 11)
        
        return cpf[-2:] == f'{digito_verificador_1}{digito_verificador_2}'