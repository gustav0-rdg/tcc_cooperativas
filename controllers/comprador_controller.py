import mysql.connector
from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
from controllers.cnpj_controller import CNPJ

class Compradores:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def create(self, cnpj):
        cursor = self.connection_db.cursor(dictionary=True)

        try:
            validar_cnpj = CNPJ.validar(cnpj)
            data = CNPJ.consultar(cnpj)
            print(data)
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

            phones_list = data.get('phones', [])
            # Verifica se existe um número de telefone no JSON
            telefone_info = phones_list[0] if phones_list else {}
            telefone = f"({telefone_info.get('area')}) {telefone_info.get('number')}" if telefone_info.get('area') else None

            emails_list = data.get('emails', [])
            # Verifica se existe um email
            email_info = emails_list[0] if emails_list else {}
            email = email_info.get('address') if email_info else None
                        
            cursor.execute("""
                    INSERT INTO compradores(cnpj, razao_social, endereco, cidade, estado, telefone, email) VALUES (%s,%s,%s,%s,%s,%s,%s);
            """, (cnpj, razao_social, endereco,cidade, estado, telefone, email))
            self.connection_db.commit()

        except Exception as e:
            print(e)
        finally:
            cursor.close()

    def get_all(self):
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute("""
            SELECT razao_social, cnpj, email, telefone, endereco, cidade, estado, score_confianca
            FROM compradores 
        """, ())
            dados = cursor.fetchall()

            return dados
        except Exception as e:
            return []
        finally: 
            cursor.close()

    
    def get_by_materials(self, material, subtipo):
        """
        Busca e agrupa compradores com base no material que compraram.
        """
        query = """
            SELECT
                mb.nome,
                c.razao_social,
                c.cnpj,
                SUM(vi.quantidade_kg) AS quantidade_kg,
                SUM(v.valor_total) AS valor_total,
                AVG(c.score_confianca) AS score_confianca,
                SUM(c.numero_avaliacoes) AS numero_avaliacoes
            FROM compradores AS c
            INNER JOIN vendas AS v ON c.id_comprador = v.id_comprador
            INNER JOIN vendas_itens AS vi ON v.id_venda = vi.id_venda
            INNER JOIN materiais_base AS mb ON vi.id_material_catalogo = mb.id_material_base
            INNER JOIN materiais_catalogo AS mc ON mb.id_material_base = mc.id_material_base
            WHERE c.deletado_em IS NULL AND mb.id_material_base = %s AND mc.id_material_catalogo = %s
            GROUP BY mb.nome, c.id_comprador, c.razao_social, c.cnpj
            ORDER BY quantidade_kg DESC;
        """
        # Usar 'with' garante que o cursor será fechado mesmo se ocorrer um erro
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                print(f"\nExecutando busca para: '{material if material else 'Todos os materiais'}'...")
                
                # Executa a query de forma segura
                cursor.execute(query, (material, subtipo))
                results = cursor.fetchall()
                
                print(f"Encontrados {len(results)} resultados.")

        except mysql.connector.Error as err:
            print(f"Erro ao executar a consulta: {err}")
            # É uma boa prática relançar a exceção ou retornar algo que indique o erro
            # para a camada superior (a rota Flask).
            return {"erro": str(err)} # Exemplo
            
        return results