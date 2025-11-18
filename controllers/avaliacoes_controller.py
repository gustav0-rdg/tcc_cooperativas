from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
import datetime

class Avaliacoes:
    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Avaliacoes: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_avaliacoes_pendentes(self, id_cooperativa: int) -> list:
        """
        Busca todas as avaliações pendentes para uma cooperativa específica.

        Args:
            id_cooperativa (int): ID da cooperativa.

        Returns:
            list: Lista de dicionários com as avaliações pendentes.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT
                    ap.id_avaliacao_pendente,
                    ap.id_venda,
                    v.data_venda,
                    v.valor_total,
                    vi.quantidade_kg,
                    vi.preco_por_kg,
                    mb.nome AS material_nome,
                    mc.nome_especifico AS subtipo_nome,
                    c.razao_social AS comprador_nome,
                    c.cnpj AS comprador_cnpj,
                    c.score_confianca,
                    c.endereco,
                    c.cidade,
                    c.estado,
                    c.telefone,
                    c.email
                FROM avaliacoes_pendentes ap
                INNER JOIN vendas v ON ap.id_venda = v.id_venda
                INNER JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                INNER JOIN materiais_base mb ON vi.id_material_base = mb.id_material_base
                INNER JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
                INNER JOIN compradores c ON v.id_comprador = c.id_comprador
                WHERE ap.id_cooperativa = %s AND ap.status_avaliacao = 'pendente'
                ORDER BY v.data_venda DESC;
                """
                cursor.execute(query, (id_cooperativa,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"Erro em get_avaliacoes_pendentes: {e}")
            return []
        finally:
            cursor.close()

    def inserir_avaliacao_pendente(self, id_venda: int, id_cooperativa: int) -> bool:
        """
        Insere uma avaliação pendente para uma venda específica.

        Args:
            id_venda (int): ID da venda.
            id_cooperativa (int): ID da cooperativa.

        Returns:
            bool: True se inserido com sucesso, False caso contrário.
        """
        try:
            with self.connection_db.cursor() as cursor:
                query = """
                INSERT INTO avaliacoes_pendentes (id_venda, id_cooperativa, status_avaliacao, data_criacao)
                VALUES (%s, %s, 'pendente', %s);
                """
                cursor.execute(query, (id_venda, id_cooperativa, datetime.datetime.now()))
                self.connection_db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro em inserir_avaliacao_pendente: {e}")
            self.connection_db.rollback()
            return False
        finally:
            cursor.close()

    def finalizar_avaliacao_pendente(self, id_avaliacao_pendente: int, dados_avaliacao: dict) -> bool:
        """
        Finaliza uma avaliação pendente, inserindo na tabela de avaliações e removendo da pendente.
        
        Corrige o erro de inserção de tags convertendo nomes (strings) para IDs (int).
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            # 1. Buscar o id_venda da avaliação pendente
            cursor.execute("SELECT id_venda FROM avaliacoes_pendentes WHERE id_avaliacao_pendente = %s", (id_avaliacao_pendente,))
            pendente = cursor.fetchone()
            if not pendente:
                return False

            id_venda = pendente['id_venda']

            # 2. Inserir na tabela de avaliações principais
            query_avaliacao = """
            INSERT INTO avaliacoes_compradores
            (id_venda, pontualidade_pagamento, logistica_entrega, qualidade_negociacao, comentario_livre)
            VALUES (%s, %s, %s, %s, %s)
            """
            nota = dados_avaliacao['nota']
            avaliacao_data = (
                id_venda,
                nota,
                nota,
                nota,
                dados_avaliacao.get('analise', '')
            )
            cursor.execute(query_avaliacao, avaliacao_data)
            id_avaliacao = cursor.lastrowid

            # 3. Inserir tags de feedback (CORREÇÃO DO ERRO 1366 AQUI)
            if 'comentarios_rapidos' in dados_avaliacao and dados_avaliacao['comentarios_rapidos']:
                lista_tags = dados_avaliacao['comentarios_rapidos']
                tags_para_inserir = []
                
                # Query para inserir a relação final
                query_insert_relacao = """
                INSERT INTO avaliacao_feedback_selecionado (id_avaliacao, id_feedback_tag)
                VALUES (%s, %s)
                """

                # Verifica o primeiro item para saber se é Texto ou ID
                primeiro_item = lista_tags[0]

                if isinstance(primeiro_item, str):
                    # --- CASO SEJA TEXTO (O Erro que estava dando) ---
                    # Precisamos descobrir o ID de cada tag baseada no nome
                    
                    # ATENÇÃO: Verifique se o nome da tabela é 'feedback_tags' e a coluna é 'nome' ou 'descricao'
                    query_busca_id = "SELECT id_feedback_tag FROM feedback_tags WHERE texto = %s" 
                    
                    for nome_tag in lista_tags:
                        cursor.execute(query_busca_id, (nome_tag,))
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            # Encontrou o ID, adiciona na lista para salvar
                            tags_para_inserir.append((id_avaliacao, resultado['id_feedback_tag']))
                        else:
                            print(f"AVISO: A tag '{nome_tag}' não foi encontrada no banco de dados e será ignorada.")
                
                else:
                    # --- CASO JÁ SEJA INTEIRO (ID) ---
                    # Apenas prepara a lista diretamente
                    tags_para_inserir = [(id_avaliacao, int(tag_id)) for tag_id in lista_tags]

                # Executa a inserção em lote se houver tags válidas
                if tags_para_inserir:
                    cursor.executemany(query_insert_relacao, tags_para_inserir)

            # 4. Remover da tabela de pendentes
            cursor.execute("DELETE FROM avaliacoes_pendentes WHERE id_avaliacao_pendente = %s", (id_avaliacao_pendente,))

            self.connection_db.commit()
            return True

        except Exception as e:
            print(f"Erro em finalizar_avaliacao_pendente: {e}")
            self.connection_db.rollback()
            return False
        finally:
            cursor.close()
    def get_avaliacao_pendente_por_id(self, id_avaliacao_pendente: int) -> dict | None:
        """
        Busca uma avaliação pendente específica por ID.

        Args:
            id_avaliacao_pendente (int): ID da avaliação pendente.

        Returns:
            dict | None: Dados da avaliação pendente ou None se não encontrada.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT
                    ap.id_avaliacao_pendente,
                    ap.id_venda,
                    v.data_venda,
                    v.valor_total,
                    vi.quantidade_kg,
                    vi.preco_por_kg,
                    mb.nome AS material_nome,
                    mc.nome_especifico AS subtipo_nome,
                    c.razao_social AS comprador_nome,
                    c.cnpj AS comprador_cnpj,
                    c.score_confianca,
                    c.endereco,
                    c.cidade,
                    c.estado,
                    c.telefone,
                    c.email
                FROM avaliacoes_pendentes ap
                INNER JOIN vendas v ON ap.id_venda = v.id_venda
                INNER JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                INNER JOIN materiais_base mb ON vi.id_material_base = mb.id_material_base
                INNER JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
                INNER JOIN compradores c ON v.id_comprador = c.id_comprador
                WHERE ap.id_avaliacao_pendente = %s AND ap.status_avaliacao = 'pendente';
                """
                cursor.execute(query, (id_avaliacao_pendente,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"Erro em get_avaliacao_pendente_por_id: {e}")
            return None
        finally:
            cursor.close()
