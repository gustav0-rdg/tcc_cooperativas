from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.email_controller import Email
from mysql.connector import Error

class Cooperativa:

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

            print(f'Erro - Cooperativa "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def autenticar (codigo_validacao:str) -> bool:

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
                INNER JOIN validacoes ON validacoes.codigo = %s
                WHERE cooperativa.cnpj = validacoes.cnpj_cooperativa;

                DELETE FROM validacoes
                WHERE validacoes.codigo = %s;
                """,

                (codigo_validacao, ),

                multi=True

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativa "validar": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def delete (cnpj:str) -> bool:

        """
        Exclui permanentemente a cooperativa
        com o CNPJ fornecido do banco de dados.
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                DELETE FROM cooperativa
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativa "delete": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def create (
            
        __self__,

        cnpj:str,

        email:str,
        senha:str,

        validar:bool=True

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        """

        if not CNPJ.validar(cnpj):

            raise ValueError ('')

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            data_cooperativa = CNPJ.consultar(cnpj)

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

                if not validar:

                    return True

                Email.enviar (

                    data_cooperativa['emails']['address'],

                    'Confirme seu e-mail no Recoopera',
                    
                    # CSS Inline e 'table' são usados por questão
                    # de compatibilidade com a maioria dos clients
                    # de e-mail que não suportam o CSS moderno
                    
                    # (Outlook por exemplo usa o motor do Microsoft Word 
                    # para renderizar e-mails)

                    f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin:0; padding:20px;">
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td align="center">
                            <table style="max-width:600px; width:100%; background:#ffffff; padding:20px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                <tr>
                                <td align="center" style="padding: 10px 0;">
                                    <h1 style="color:#2e7d32; margin:0;">Recoopera</h1>
                                    <p style="color:#666; font-size:14px; margin:5px 0 20px;">
                                    Rede de cooperativas de catadores de recicláveis
                                    </p>
                                </td>
                                </tr>

                                <tr>
                                <td style="padding: 20px;">
                                    <h2 style="color:#333; margin-top:0;">Confirme seu e-mail</h2>
                                    <p style="color:#555; line-height:1.5; font-size:16px;">
                                    Olá, seja bem-vindo(a) ao <b>Recoopera</b>!  
                                    Para concluir seu cadastro, precisamos confirmar que este e-mail pertence a você.
                                    </p>

                                    <div style="text-align:center; margin:30px 0;">
                                    <a href="https://seusite.com/verificar?token=XYZ123"
                                        style="background:#2e7d32; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:5px; display:inline-block; font-weight:bold;">
                                        Confirmar meu e-mail
                                    </a>
                                    </div>

                                    <p style="color:#555; font-size:14px; line-height:1.5;">
                                    Se o botão acima não funcionar, copie e cole o link abaixo em seu navegador:
                                    <br>
                                    <a href="https://seusite.com/verificar?token=XYZ123" style="color:#2e7d32; word-break:break-all;">
                                        https://seusite.com/verificar?token=XYZ123
                                    </a>
                                    </p>

                                    <p style="color:#888; font-size:12px; line-height:1.5; margin-top:30px;">
                                    Caso você não tenha solicitado este cadastro, pode ignorar este e-mail com segurança.
                                    </p>
                                </td>
                                </tr>

                                <tr>
                                <td align="center" style="padding: 15px 0; border-top:1px solid #ddd;">
                                    <p style="color:#999; font-size:12px; margin:0;">
                                    © 2025 Recoopera – Transformando reciclagem em oportunidade
                                    </p>
                                </td>
                                </tr>
                            </table>
                            </td>
                        </tr>
                        </table>
                    </body>
                    </html>
                    """

                )

            else:

                return False

        except Error as e:

            print(f'Erro - Cooperativa "create": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()