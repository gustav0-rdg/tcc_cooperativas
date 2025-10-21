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

    
    def get_by_materials(self, material=None):
        """
        Busca e agrupa compradores com base no material ou categoria de material que compraram.

        :param material: (Opcional) String com o nome do material ou a categoria.
                         Se não for fornecido, a função retorna dados para todos os materiais.
        :return: Lista de dicionários, onde cada dicionário representa um comprador e o material.
                 Retorna uma lista vazia se não houver resultados ou em caso de erro.
        """
        if not self.conn or not self.conn.is_connected():
            print("Erro: Não há conexão ativa com o banco de dados.")
            return []

        # A query base é a mesma que desenvolvemos.
        base_query = """
            SELECT
                mc.categoria,
                mc.nome_padrao,
                c.razao_social,
                c.cnpj,
                SUM(vi.quantidade_kg) AS total_kg_comprado
            FROM
                compradores AS c
            INNER JOIN
                vendas AS v ON c.id_comprador = v.id_comprador
            INNER JOIN
                vendas_itens AS vi ON v.id_venda = vi.id_venda
            INNER JOIN
                materiais_catalogo AS mc ON vi.id_material_catalogo = mc.id_material_catalogo
            WHERE
                c.deletado_em IS NULL
        """
        
        params = []
        
        # Adiciona o filtro dinamicamente se um material for especificado
        if material:
            # Filtra tanto por nome quanto por categoria para maior flexibilidade
            base_query += " AND (mc.nome_padrao = %s OR mc.categoria = %s)"
            params.extend([material, material])

        # Adiciona o agrupamento e a ordenação
        final_query = base_query + """
            GROUP BY
                mc.categoria, mc.nome_padrao, c.id_comprador
            ORDER BY
                mc.categoria ASC, mc.nome_padrao ASC, total_kg_comprado DESC;
        """

        results = []
        cursor = self.conn.cursor(dictionary=True) # dictionary=True retorna resultados como dicts

        try:
            print(f"\nExecutando busca para: '{material if material else 'Todos os materiais'}'...")
            
            # Executa a query de forma segura usando parâmetros
            cursor.execute(final_query, tuple(params))
            results = cursor.fetchall()
            
            print(f"Encontrados {len(results)} resultados.")

        except mysql.connector.Error as err:
            print(f"Erro ao executar a consulta: {err}")
        finally:
            cursor.close()
            
        return results
