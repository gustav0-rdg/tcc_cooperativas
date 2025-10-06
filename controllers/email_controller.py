import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from os import getenv

# Carrega as variáveis do arquivo '.env'

load_dotenv()   

class Email:

    remetente = getenv('USUARIO_EMAIL')
    senha = getenv('SENHA_EMAIL')

    @staticmethod
    def enviar (destinatario:str, assunto:str, formatacao_html:str) -> bool:

        """
        Enviar email
        """

        # Cria conexão com o servidor de email
        # 'smtp.gmail.com' -> Endereço do servidor da Gmail
        # 587 -> Porta recomendada para SMTP com conexão segura (.'starttls()')

        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()

        try:

            # O email usa o protocolo MIME (Multipurpose Internet Mail Extensions)
            # pois nele são usados diferentes tipos de conteúdos que precisam
            # ser estruturadas

            email = MIMEMultipart()

            email['From'] = Email.remetente
            email['To'] = destinatario
            email['Subject'] = assunto

            corpo_html = MIMEText(formatacao_html, 'html', 'utf-8')
            email.attach(corpo_html)

            servidor.login(Email.remetente, Email.senha)
            servidor.sendmail(Email.remetente, destinatario, email.as_string())
            
            return True

        except Exception as e:

            print(f'Erro - Email "enviar": {e}')

            return False
        
        finally:

            servidor.quit()