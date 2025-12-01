import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
import html

class Email:

    @staticmethod
    def gerar_template_aprovacao(razao_social: str) -> str:

        """
        Gera o template HTML para email de aprovação de cadastro
        """
        razao_social_escaped = html.escape(razao_social)
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #F6FBF2;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #F6FBF2; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden;">
                            <tr>
                                <td style="padding: 20px 40px; background-color: #004D2B; text-align: center; color: #ffffff;">
                                    <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Recoopera</h1>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 40px 40px 30px 40px; color: #333333;">
                                    <h2 style="margin-top: 0; font-size: 22px; color: #004D2B;">Cadastro Aprovado!</h2>
                                    <p style="font-size: 16px; line-height: 1.6;">Olá, <strong>{razao_social_escaped}</strong>!</p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Temos o prazer de informar que o seu cadastro na plataforma Recoopera foi <strong>aprovado</strong> com sucesso.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Você já pode acessar a plataforma e começar a utilizar todas as nossas ferramentas para fortalecer a sua cooperativa.
                                    </p>
                                    
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="margin-top: 30px; margin-bottom: 30px;">
                                        <tr>
                                            <td align="center" style="background-color: #00A859; border-radius: 8px;">
                                                <a href="http://127.0.0.1:5000/login" target="_blank" style="display: inline-block; padding: 14px 28px; font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 8px;">
                                                    Acessar Plataforma
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Se você não solicitou este cadastro, por favor, ignore este e-mail.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Atenciosamente,<br>
                                        Equipe Recoopera
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 20px 40px; background-color: #f9f9f9; text-align: center; color: #888888; font-size: 12px;">
                                    <p style="margin: 0;">&copy; 2024 Recoopera. Todos os direitos reservados.</p>
                                    <p style="margin: 5px 0 0 0;">Este é um e-mail automático, por favor, não responda.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    
    @staticmethod
    def gerar_template_rejeicao(razao_social: str, motivo: str, justificativa: str) -> str:

        """
        Gera o template HTML para email de REJEIÇÃO de cadastro
        """
        
        razao_social_escaped = html.escape(razao_social)
        motivo_escaped = html.escape(motivo)
        justificativa_escaped = html.escape(justificativa)

        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #F6FBF2;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #F6FBF2; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden;">
                            <tr>
                                <td style="padding: 20px 40px; background-color: #6AB633; text-align: center; color: #ffffff;">
                                    <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Recoopera</h1>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 40px 40px 30px 40px; color: #333333;">
                                    <h2 style="margin-top: 0; font-size: 22px; color: #D32F2F;">Cadastro Rejeitado</h2>
                                    <p style="font-size: 16px; line-height: 1.6;">Olá, <strong>{razao_social_escaped}</strong>,</p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Agradecemos pelo seu interesse em se cadastrar na plataforma Recoopera.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Após uma análise, seu cadastro infelizmente <strong>não foi aprovado</strong>. Nossos gestores identificaram que o seu cadastro não cumpre os requisitos necessários para se juntar à plataforma.
                                    </p>
                                    
                                    <div style="background-color: #FFF8F8; border: 1px solid #FFCDD2; border-radius: 8px; padding: 20px; margin-top: 25px; margin-bottom: 25px;">
                                        <h3 style="margin-top: 0; color: #D32F2F; font-size: 18px;">Motivo da Rejeição</h3>
                                        <p style="font-size: 16px; line-height: 1.6; margin: 0 0 10px 0;">
                                            <strong>{motivo_escaped}</strong>
                                        </p>
                                        <p style="font-size: 16px; line-height: 1.6; margin: 0; font-style: italic;">
                                            "{justificativa_escaped}"
                                        </p>
                                    </div>
                                    
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Para mais detalhes ou para tentar corrigir a pendência, por favor, entre em contato conosco.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Atenciosamente,<br>
                                        Equipe Recoopera
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 20px 40px; background-color: #f9f9f9; text-align: center; color: #888888; font-size: 12px;">
                                    <p style="margin: 0;">&copy; 2024 Recoopera. Todos os direitos reservados.</p>
                                    <p style="margin: 5px 0 0 0;">Este é um e-mail automático, por favor, não responda.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    @staticmethod
    def gerar_template_recuperacao_senha(nome_usuario: str, url_recuperacao: str) -> str:

        """
        Gera o template HTML para email de RECUPERAÇÃO DE SENHA
        """

        # Escapar, escaped ou percent-enconding -> Processo de converter caractéres 
        # especiais em formato seguro para serem transmitidos pela internet 
        
        nome_usuario_escaped = html.escape(nome_usuario)
        url_recuperacao_escaped = html.escape(url_recuperacao) 
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #F6FBF2;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #F6FBF2; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden;">
                            
                            <!-- Cabeçalho (Estilo "Aprovação" - Verde Escuro) -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: #004D2B; text-align: center; color: #ffffff;">
                                    <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Recoopera</h1>
                                </td>
                            </tr>
                            
                            <!-- Conteúdo Principal -->
                            <tr>
                                <td style="padding: 40px 40px 30px 40px; color: #333333;">
                                    <h2 style="margin-top: 0; font-size: 22px; color: #004D2B;">Redefinição de Senha</h2>
                                    
                                    <p style="font-size: 16px; line-height: 1.6;">Olá, <strong>{nome_usuario_escaped}</strong>!</p>
                                    
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Recebemos uma solicitação para redefinir a senha da sua conta na plataforma Recoopera.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Se foi você quem solicitou, clique no botão abaixo para criar uma nova senha. Este link expirará em breve.
                                    </p>
                                    
                                    <!-- Botão (Estilo "Aprovação" - Verde Claro) -->
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="margin-top: 30px; margin-bottom: 30px;">
                                        <tr>
                                            <td align="center" style="background-color: #00A859; border-radius: 8px;">
                                                <a href="{url_recuperacao_escaped}" target="_blank" style="display: inline-block; padding: 14px 28px; font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 8px;">
                                                    Redefinir Minha Senha
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Se você não fez esta solicitação, por favor, ignore este e-mail. Sua senha permanecerá a mesma.
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.6;">
                                        Atenciosamente,<br>
                                        Equipe Recoopera
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer (Padrão) -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: #f9f9f9; text-align: center; color: #888888; font-size: 12px;">
                                    <p style="margin: 0;">&copy; 2024 Recoopera. Todos os direitos reservados.</p>
                                    <p style="margin: 5px 0 0 0;">Este é um e-mail automático, por favor, não responda.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    @staticmethod
    def enviar (destinatario:str, assunto:str, formatacao_html:str) -> bool:

        """
        Envia email via SMTP.
        """

        remetente = getenv('USUARIO_EMAIL')
        senha = getenv('SENHA_EMAIL')

        # Verifica credenciais
        if not remetente or not senha:
            print(f'Erro em enviar: Credenciais não configuradas (USUARIO_EMAIL e SENHA_EMAIL no .env)')
            return False

        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()

        try:

            email = MIMEMultipart()

            email['From'] = remetente
            email['To'] = destinatario
            email['Subject'] = assunto

            corpo_html = MIMEText(formatacao_html, 'html', 'utf-8')
            email.attach(corpo_html)

            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatario, email.as_string()) 
            
            return True
        
        except Exception as e:

            print(f'Erro - Email "enviar": {e}')
            return False
        
        finally:

            servidor.quit()