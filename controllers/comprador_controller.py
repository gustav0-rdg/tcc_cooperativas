import mysql.connector
from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
from controllers.cnpj_controller import CNPJ
from controllers.endereco_controller import Endereco

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

            # ===== ENDEREÇO - Formatação correta sem "None" =====
            endereco_info = data.get('address', {})
            partes_endereco = []
            
            rua = endereco_info.get('street', '').strip()
            numero = endereco_info.get('number', '').strip()
            bairro = endereco_info.get('district', '').strip()
            complemento = endereco_info.get('details', '').strip()
            
            # Monta o endereço apenas com partes não vazias
            if rua:
                if numero:
                    partes_endereco.append(f"{rua}, {numero}")
                else:
                    partes_endereco.append(rua)
            
            if bairro:
                partes_endereco.append(bairro)
            
            if complemento:
                partes_endereco.append(complemento)
            
            endereco = ' - '.join(partes_endereco) if partes_endereco else None

            cidade = endereco_info.get('city')
            estado = endereco_info.get('state')

            # ===== TELEFONES - Separar fixo e WhatsApp =====
            phones_list = data.get('phones', [])
            telefone = None
            whatsapp = None
            
            for phone in phones_list:
                phone_type = phone.get('type', '').upper()
                area = phone.get('area', '').strip()
                number = phone.get('number', '').strip()
                
                if not number:
                    continue
                
                # Formata o telefone
                if area:
                    phone_formatted = f"({area}) {number}"
                else:
                    phone_formatted = number
                
                # Identifica se é celular/WhatsApp ou fixo
                # Celular geralmente tem type='MOBILE' ou número começa com 9
                if phone_type == 'MOBILE' or (len(number) >= 9 and number[0] == '9'):
                    if not whatsapp:  # Pega o primeiro celular como WhatsApp
                        whatsapp = phone_formatted
                elif phone_type == 'LANDLINE' or not whatsapp:
                    if not telefone:  # Pega o primeiro fixo
                        telefone = phone_formatted
            
            # Se não encontrou WhatsApp mas tem telefone, usa o telefone como WhatsApp também
            if not whatsapp and telefone:
                whatsapp = telefone

            # ===== EMAIL =====
            emails_list = data.get('emails', [])
            email = None
            
            if emails_list:
                email_info = emails_list[0]
                email = email_info.get('address', '').strip() if email_info else None
            
            # ===== INSERÇÃO NO BANCO =====
            cursor.execute("""
                    INSERT INTO compradores(cnpj, razao_social, endereco, cidade, estado, telefone, email) VALUES (%s,%s,%s,%s,%s,%s,%s);
            """, (cnpj, razao_social, endereco,cidade, estado, telefone, email))
            self.connection_db.commit()
            
            print(f"✅ Comprador cadastrado: {razao_social}")
            print(f"   Endereço: {endereco}")
            print(f"   Telefone: {telefone}")
            print(f"   WhatsApp: {whatsapp}")
            print(f"   Email: {email}")

        except Exception as e:
            print(f"❌ Erro ao cadastrar comprador: {e}")
            self.connection_db.rollback()
        finally:
            cursor.close()

    def get(self):
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * from compradores;
            """)
            compradores = cursor.fetchall()
            return compradores
        except Exception as e:
            print(e)
            return []

    def get_all(self, user_lat:float, user_lon:float, material_id=None, estado=None, raio_km=None) -> list:

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.id_comprador,
                    c.razao_social, 
                    c.cnpj, 
                    c.email, 
                    c.telefone, 
                    c.endereco, 
                    c.cidade, 
                    c.estado, 
                    c.score_confianca, 
                    c.latitude, 
                    c.longitude,
                    c.numero_avaliacoes,
                    c.data_cadastro,
                    MAX(vi.preco_por_kg) AS `preco_maximo`,
                    MIN(vi.preco_por_kg) AS `preco_minimo`,
                    AVG(vi.preco_por_kg) AS `preco_medio`
                FROM compradores c
                LEFT JOIN vendas v ON c.id_comprador = v.id_comprador
                LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda
            """

            params = []
            where_clauses = []

            # Filtro por material (se comprou esse material)

            if material_id:

                where_clauses.append("LIKE vi.id_material_base = %s")
                params.append(material_id)

            # Filtro por estado

            if estado:

                where_clauses.append("c.estado = %s")
                params.append(estado)

            # Adiciona WHERE se houver filtros

            if where_clauses:

                query += " WHERE " + " AND ".join(where_clauses)

            query += """
                GROUP BY 
                    c.id_comprador, c.razao_social, c.cnpj, c.email, c.telefone, 
                    c.endereco, c.cidade, c.estado, c.score_confianca, 
                    c.latitude, c.longitude, c.numero_avaliacoes, c.data_cadastro
            """

            query += " ORDER BY c.score_confianca DESC;"

            cursor.execute(query, params)

            compradores = cursor.fetchall()
            compradores_filtrados = []

            # Para cada comprador, calcular a distância até o usuário
            if user_lat != None and user_lon != None:

                for comprador in compradores:

                    # Calculando a distância usando a função Haversine

                    distancia = Endereco.haversine(user_lat, user_lon, comprador['latitude'], comprador['longitude'])
                    comprador['distancia'] = round(distancia, 2)

                    if raio_km is None or distancia <= raio_km:
                        compradores_filtrados.append(comprador)

            compradores_filtrados.sort(key=lambda x: x['distancia'])
            return compradores_filtrados

        except Exception as e:

            print(f"Erro ao buscar compradores: {e}")
            return []
        
        finally:

            cursor.close()
    def get_by_materials(self, material, subtipo):
        """
        Busca e agrupa compradores com base no material que compraram usando v_compradores_publico.
        """
        query = """
            SELECT
                mb.nome AS material_base,
                c.razao_social,
                SUM(vi.quantidade_kg) AS quantidade_kg,
                SUM(v.valor_total) AS valor_total,
                AVG(c.score_confianca) AS score_confianca,
                SUM(c.numero_avaliacoes) AS numero_avaliacoes
            FROM v_compradores_publico AS c
            INNER JOIN vendas AS v ON c.id_comprador = v.id_comprador
            INNER JOIN vendas_itens AS vi ON v.id_venda = vi.id_venda
            INNER JOIN materiais_catalogo AS mc ON vi.id_material_catalogo = mc.id_material_catalogo
            INNER JOIN materiais_base AS mb ON vi.id_material_base = mb.id_material_base
            WHERE mb.id_material_base = %s
            AND mc.id_material_catalogo = %s
            GROUP BY mb.nome, c.id_comprador, c.razao_social
            ORDER BY quantidade_kg DESC;

        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                print(f"\nExecutando busca para: '{material if material else 'Todos os materiais'}'...")

                # Executa a query de forma segura
                cursor.execute(query, (material, subtipo))
                results = cursor.fetchall()

                print(f"Encontrados {len(results)} resultados.")

        except mysql.connector.Error as err:
            print(f"Erro ao executar a consulta: {err}")

            return {"erro": str(err)}

        return results

    def get_compradores_destaque(self, material_id=None, estado=None, score_min=None) -> list[dict]:
        """
        Busca os compradores em destaque (melhores scores) usando a view v_compradores_destaque.
        Aplica filtros opcionais: material_id, estado, score_min.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = """
            SELECT * FROM v_compradores_destaque
            WHERE 1=1
            """
            params = []

            if material_id:
                query += """
                AND EXISTS (
                    SELECT 1 FROM vendas v
                    JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                    WHERE v.id_comprador = v_compradores_destaque.id_comprador
                    AND vi.id_material_base = %s
                )
                """
                params.append(material_id)

            if estado:
                query += " AND estado = %s"
                params.append(estado)

            if score_min:
                query += " AND score_confianca >= %s"
                params.append(float(score_min))

            query += " ORDER BY score_confianca DESC LIMIT 20;"

            cursor.execute(query, params)
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Erro em 'get_compradores_destaque': {e}")
            return []

        finally:
            cursor.close()

    def get_detalhes_comprador(self, id_comprador: int) -> dict:
        """
        Busca detalhes de um comprador, incluindo materiais já comprados
        e a faixa de preço (min/max) por material.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        detalhes = {
            "materiais_comprados": [],
            "avaliacoes_recentes": []
        }
        try:
            query_materiais = """
            SELECT
                mc.nome_especifico AS material_nome,
                COUNT(v.id_venda) AS total_vendas,
                MIN(v.valor_total / vi.quantidade_kg) AS preco_min_kg,
                MAX(v.valor_total / vi.quantidade_kg) AS preco_max_kg
            FROM vendas v
            JOIN vendas_itens vi ON v.id_venda = vi.id_venda
            JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
            WHERE v.id_comprador = %s AND vi.quantidade_kg > 0
            GROUP BY mc.nome_especifico
            ORDER BY total_vendas DESC;
            """
            cursor.execute(query_materiais, (id_comprador,))
            detalhes["materiais_comprados"] = cursor.fetchall()

            query_avaliacoes = """
            SELECT
                ac.pontualidade_pagamento,
                ac.logistica_entrega,
                ac.qualidade_negociacao,
                ac.comentario_livre,
                ac.data_avaliacao
            FROM avaliacoes_compradores ac
            JOIN vendas v ON ac.id_venda = v.id_venda
            WHERE v.id_comprador = %s
            ORDER BY ac.data_avaliacao DESC;
            """
            cursor.execute(query_avaliacoes, (id_comprador,))
            detalhes["avaliacoes_recentes"] = cursor.fetchall()

            return detalhes

        except Exception as e:
            print(f"Erro em 'get_detalhes_comprador': {e}")
            return detalhes

        finally:
            cursor.close()
