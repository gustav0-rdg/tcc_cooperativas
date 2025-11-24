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
            
            latitude = 0
            longitude = 0
            
            coordenadas = Endereco.get_coordenadas(f'{rua}, {cidade}, {estado}, Brasil')
            
            if not coordenadas is None:
                latitude, longitude = coordenadas

            # ===== INSERÇÃO NO BANCO =====
            query = """
                INSERT INTO compradores(
                    cnpj, razao_social, nome_fantasia, email, telefone, whatsapp, 
                    cep, logradouro, numero, complemento, bairro, cidade, estado,
                    latitude, longitude
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    razao_social = VALUES(razao_social),
                    nome_fantasia = VALUES(nome_fantasia),
                    email = VALUES(email),
                    telefone = VALUES(telefone),
                    whatsapp = VALUES(whatsapp),
                    cep = VALUES(cep),
                    logradouro = VALUES(logradouro),
                    numero = VALUES(numero),
                    complemento = VALUES(complemento),
                    bairro = VALUES(bairro),
                    cidade = VALUES(cidade),
                    estado = VALUES(estado),
                    ultima_atualizacao = NOW();
            """
            params = (
                data.get('taxId'),
                data.get('company', {}).get('name'),
                data.get('company', {}).get('alias'),
                email,
                telefone,
                whatsapp,
                endereco_info.get('zip'),
                rua,
                numero,
                complemento,
                bairro,
                cidade,
                estado,
                latitude,
                longitude
            )
            cursor.execute(query, params)
            self.connection_db.commit()
            
            print(f"✅ Comprador cadastrado/atualizado: {razao_social}")
            print(f"   Endereço: {rua}, {numero} - {bairro}")
            print(f"   Telefone: {telefone}")
            print(f"   WhatsApp: {whatsapp}")
            print(f"   Email: {email}")

        except Exception as e:
            print(f"❌ Erro ao cadastrar comprador: {e}")
            self.connection_db.rollback()
        finally:
            cursor.close()

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
                    CONCAT_WS(', ', c.logradouro, c.numero, c.bairro) AS endereco,
                    c.cidade, 
                    c.estado, 
                    c.score_confianca, 
                    c.latitude, 
                    c.longitude,
                    c.numero_avaliacoes,
                    c.data_criacao,
                    MAX(vi.preco_por_kg) AS `preco_maximo`,
                    MIN(vi.preco_por_kg) AS `preco_minimo`,
                    AVG(vi.preco_por_kg) AS `preco_medio`
                FROM compradores c
                LEFT JOIN vendas v ON c.id_comprador = v.id_comprador
                LEFT JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                LEFT JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
            """

            params = []
            where_clauses = []

            # Filtro por material (se comprou esse material)

            if material_id:

                where_clauses.append("mc.id_material_base = %s")
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
                    endereco, c.cidade, c.estado, c.score_confianca, 
                    c.latitude, c.longitude, c.numero_avaliacoes, c.data_criacao
            """

            query += " ORDER BY c.score_confianca DESC;"

            cursor.execute(query, params)

            compradores = cursor.fetchall()
            compradores_filtrados = []

            # Para cada comprador, calcular a distância até o usuário
            if user_lat is not None and user_lon is not None:
                for comprador in compradores:
                    # Calculando a distância usando a função Haversine
                    if comprador.get('latitude') and comprador.get('longitude'):
                        distancia = Endereco.haversine(user_lat, user_lon, comprador['latitude'], comprador['longitude'])
                        comprador['distancia'] = round(distancia, 2)
                    else:
                        comprador['distancia'] = None  # Usar None em vez de float('inf')

                    # Adicionar à lista se o raio não for um filtro ou se a distância for válida
                    if raio_km is None or (comprador['distancia'] is not None and comprador['distancia'] <= raio_km):
                        compradores_filtrados.append(comprador)
            else:
                # Se o usuário não tem lat/lon, não podemos calcular distâncias
                for comprador in compradores:
                    comprador['distancia'] = None
                compradores_filtrados = compradores


            # Ordena a lista: compradores com distância aparecem primeiro, ordenados pela distância.
            # Os sem distância (None) vão para o final.
            compradores_filtrados.sort(key=lambda x: (x.get('distancia') is None, x.get('distancia')))
            
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
                SUM(vi.total_item) AS valor_total,
                AVG(c.score_confianca) AS score_confianca,
                c.numero_avaliacoes
            FROM compradores AS c
            INNER JOIN vendas AS v ON c.id_comprador = v.id_comprador
            INNER JOIN vendas_itens AS vi ON v.id_venda = vi.id_venda
            INNER JOIN materiais_catalogo AS mc ON vi.id_material_catalogo = mc.id_material_catalogo
            INNER JOIN materiais_base AS mb ON mc.id_material_base = mb.id_material_base
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
            SELECT 
                c.id_comprador,
                c.razao_social,
                c.cidade,
                c.estado,
                c.score_confianca,
                c.numero_avaliacoes
            FROM compradores c
            WHERE c.deletado_em IS NULL
            """
            params = []

            if material_id:
                query += """
                AND EXISTS (
                    SELECT 1 FROM vendas v
                    JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                    JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
                    WHERE v.id_comprador = c.id_comprador
                    AND mc.id_material_base = %s
                )
                """
                params.append(material_id)

            if estado:
                query += " AND c.estado = %s"
                params.append(estado)

            if score_min:
                query += " AND c.score_confianca >= %s"
                params.append(float(score_min))

            query += " ORDER BY c.score_confianca DESC, c.numero_avaliacoes DESC LIMIT 20;"

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
        Busca todos os detalhes de um comprador para o modal, incluindo
        informações de contato, materiais, avaliações e tags de feedback.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        detalhes = {}

        try:
            # 1. Buscar informações primárias do comprador (contato, cnpj)
            query_comprador = """
            SELECT razao_social, cnpj, email, telefone, whatsapp,
                   logradouro, numero, complemento, bairro, cidade, estado
            FROM compradores
            WHERE id_comprador = %s;
            """
            cursor.execute(query_comprador, (id_comprador,))
            comprador_info = cursor.fetchone()

            if not comprador_info:
                return None  # Retorna None se o comprador não for encontrado
            
            detalhes.update(comprador_info)

            # 2. Buscar materiais já comprados
            query_materiais = """
            SELECT
                material_nome,
                COUNT(DISTINCT id_venda) AS total_vendas,
                MIN(preco_por_kg) AS preco_min_kg,
                MAX(preco_por_kg) AS preco_max_kg
            FROM v_vendas_detalhadas
            WHERE id_comprador = %s AND quantidade_kg > 0
            GROUP BY material_nome
            ORDER BY total_vendas DESC;
            """
            cursor.execute(query_materiais, (id_comprador,))
            detalhes["materiais_comprados"] = cursor.fetchall()

            # 3. Buscar avaliações recentes
            query_avaliacoes = """
            SELECT
                avaliacao_score AS score,
                avaliacao_comentario AS comentario_livre,
                data_venda AS data_avaliacao
            FROM v_vendas_detalhadas
            WHERE id_comprador = %s AND avaliacao_score IS NOT NULL
            ORDER BY data_venda DESC;
            """
            cursor.execute(query_avaliacoes, (id_comprador,))
            detalhes["avaliacoes_recentes"] = cursor.fetchall()

            # 4. Buscar tags de feedback agregadas usando o CNPJ
            comprador_cnpj = comprador_info.get('cnpj')
            if comprador_cnpj:
                query_tags = """
                SELECT
                    feedback_texto AS texto,
                    feedback_tipo AS tipo,
                    quantidade_mencoes AS quantidade
                FROM v_feedback_comprador_agregado
                WHERE cnpj = %s
                ORDER BY quantidade_mencoes DESC;
                """
                cursor.execute(query_tags, (comprador_cnpj,))
                detalhes["feedback_tags"] = cursor.fetchall()
            else:
                detalhes["feedback_tags"] = []

            return detalhes

        except Exception as e:
            print(f"Erro em 'get_detalhes_comprador': {e}")
            return None

        finally:
            cursor.close()
