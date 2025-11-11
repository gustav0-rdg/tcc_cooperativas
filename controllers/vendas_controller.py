from data.connection_controller import Connection
from mysql.connector import MySQLConnection
import datetime
from controllers.comprador_controller import Compradores
from controllers.materiais_controller import Materiais

class Vendas:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def _buscar_id_cooperativa(self, cnpj: str) -> int:
        """
        Busca o ID de uma cooperativa ativa na tabela cooperativas a partir de seus cnpj
        Args: 
            cnpj (str): O CNPJ da cooperativa.
        return:
            int: O id da cooperativa buscada.
        """

        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        with self.connection_db.cursor() as cursor:
            query = "SELECT id_cooperativa FROM cooperativas WHERE cnpj = %s"
            cursor.execute(query, (cnpj,))
            result = cursor.fetchone()
        if result:
            id_cooperativa = result[0]
            print(f"Cooperativa encontrada: CNPJ - {cnpj} Corresponde ao ID: {id_cooperativa}")
            return id_cooperativa
        else:
            raise ValueError("Erro - Nenhuma cooperativa encontrada com o CNPJ indicado")
        
    def _buscar_id_comprador(self, cnpj: str) -> int:
        """
        Busca o ID de um comprador ativo na tabela `compradores` a partir do seu CNPJ.

        Args:
            cnpj (str): O CNPJ do comprador a ser buscado.

        Returns:
            int: O ID do comprador encontrado.

        Raises:
            CompradorNaoEncontradoError: Se nenhum comprador ativo for encontrado com o CNPJ fornecido.
            Exception: Para outros erros de banco de dados.
        """
        # Removemos qualquer máscara do CNPJ (pontos, barras, etc.)
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        # O uso de 'with' garante que o cursor será fechado automaticamente
        with self.connection_db.cursor() as cursor:
            # Query SQL para buscar o ID.
            query = "SELECT id_comprador FROM compradores WHERE cnpj = %s AND deletado_em IS NULL"
            cursor.execute(query, (cnpj_limpo,))
            result = cursor.fetchone() 
        
        if result:
            id_comprador = result[0]
            print(f"Comprador encontrado: CNPJ {cnpj} corresponde ao ID {id_comprador}.")
            return id_comprador
        else:
            new_id = Compradores(self.connection_db).create(cnpj)
            return new_id

    def _buscar_id_material(self, nome_material: str) -> int:
        """
        Busca o ID de um material ativo na tabela `materiais_base`,
        mesmo que o nome não seja exatamente igual (ex: "plástico bolha" → "Plástico").

        Args:
            nome_material (str): O nome do material a ser buscado.

        Returns:
            int: O ID do material encontrado.

        Raises:
            ValueError: Se nenhum material ativo for encontrado.
        """
        nome_limpo = nome_material.strip().lower()
        termo_sql = nome_limpo + '%'
        with self.connection_db.cursor(dictionary=True) as cursor:
            # 🔎 Busca por similaridade (bidirecional)
            query = """
                SELECT id_material_base, nome FROM materiais_base
                WHERE 
                nome COLLATE utf8mb4_general_ci LIKE %s
            """
            cursor.execute(query, (termo_sql,))
            result = cursor.fetchone()

        if result:
            id_material, nome_encontrado = result["id_material_base"], result["nome"]
            print(f"✅ Material encontrado: '{nome_material}' corresponde a '{nome_encontrado}' (ID {id_material}).")
            return id_material
        else:
            print(f" Nenhum material ativo encontrado para '{nome_material}'.")
            raise ValueError(f"Nenhum material ativo chamado '{nome_material}' foi encontrado no catálogo.")
    
        
    def _buscar_subtipo(self, nome_subtipo, nome_material):
        """
        Busca o ID de um material ativo na tabela `materiais_catalogo`.
        Args:
            nome_material (str): O nome exato do subtipo do material.
        Returns:
            int: O ID do material encontrado.
        Raises:
            MaterialNaoEncontradoError: Se nenhum material ativo for encontrado com o nome fornecido.
        """
        with self.connection_db.cursor() as cursor:
            # Buscamos pelo nome e garantimos que o material esteja 'ativo'.
            query = "SELECT id_material_catalogo FROM materiais_catalogo WHERE nome_especifico = %s"
            cursor.execute(query, (nome_subtipo,))
            result = cursor.fetchone()

        if result:
            id_subtipo = result[0]
            print(f"Material encontrado: '{nome_subtipo}' corresponde ao ID {id_subtipo}.")
            return id_subtipo
        else:
            id_material = self._buscar_id_material(nome_material)
            new_subtipo = Materiais(self.connection_db).cadastrar_subtipo(nome_subtipo, id_material)    
            return new_subtipo

    def _buscar_ids_feedback_tags(self, lista_tags: list[str]) -> list[int]:
        """
        Busca os IDs de uma lista de tags de feedback.

        Args:
            lista_tags (list[str]): Uma lista com os textos das tags.

        Returns:
            list[int]: Uma lista com os IDs correspondentes.
        """
        # Se a lista de comentários estiver vazia, não há nada a fazer.
        if not lista_tags:
            print("ℹ️ Nenhuma tag de feedback rápido fornecida.")
            return []

        with self.connection_db.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(lista_tags))
            query = f"SELECT id_feedback_tag, texto FROM feedback_tags WHERE texto IN ({placeholders})"
            
            cursor.execute(query, tuple(lista_tags))
            results = cursor.fetchall() 

        # Validação: Verificamos se o número de tags encontradas é o mesmo que o número de tags solicitadas.
        if len(results) != len(lista_tags):
            tags_encontradas = {result[1] for result in results}
            tags_faltantes = set(lista_tags) - tags_encontradas
            raise ValueError(f"As seguintes tags de feedback não foram encontradas ou estão inativas: {list(tags_faltantes)}")

        # Extrai apenas os IDs da lista de tuplas [(id1, texto1), (id2, texto2), ...]
        ids_encontrados = [result[0] for result in results]
        print(f"Tags de Feedback encontradas: {lista_tags} correspondem aos IDs {ids_encontrados}.")
        return ids_encontrados
    
    def _buscar_ids(self, dados_frontend: dict):
        """
        Método principal que orquestra o processamento dos dados da venda.
        Por enquanto, ele apenas executa o passo 1.
        """
        try:    
             
            cnpj_comprador = dados_frontend['vendedor']['cnpj']
            id_comprador = self._buscar_id_comprador(cnpj_comprador)
            nome_material = dados_frontend['material']['categoria']
            nome_subtipo = dados_frontend['material']['subtipo']
            id_material = self._buscar_id_material(nome_material)
            id_subtipo = self._buscar_subtipo(nome_subtipo, nome_material)
            cnpj_cooperativa = dados_frontend['cnpj']
            id_cooperativa = self._buscar_id_cooperativa(cnpj_cooperativa)
            ids_tags = self._buscar_ids_feedback_tags(dados_frontend['avaliacao']['comentarios_rapidos'])

            return {
                "id_comprador": id_comprador,
                "id_material": id_material,
                "ids_tags_feedback": ids_tags,
                "id_subtipo": id_subtipo,
                "id_cooperativa": id_cooperativa
            }

        except Exception as e:
            print(f"Erro de negócio: {e}")
            return None
        
    def registrar_nova_venda(self, dados_frontend):
        """
        Orquestra a criação completa de uma venda, seus itens e avaliação dentro de uma transação.

        Args:
            id_cooperativa (int): O ID da cooperativa que está realizando a venda.
            dados_frontend (dict): O dicionário de dados vindo do front-end.
        """
        print('dados frontedn', dados_frontend)  
        # Buscar e validar todos os IDs antes de iniciar a transação.
        ids = self._buscar_ids(dados_frontend)

        # Inicia o cursor que será usado em toda a transação.
        cursor = self.connection_db.cursor()

        try:          
            # INSERIR NA TABELA `vendas`
            query_venda = """
                INSERT INTO vendas (id_cooperativa, id_comprador, data_venda, valor_total)
                VALUES (%s, %s, %s, %s)
            """
            venda_data = (
                ids['id_cooperativa'],
                ids['id_comprador'],
                datetime.datetime.now(), # Ou a data vinda do front-end
                dados_frontend['total']
            )
            cursor.execute(query_venda, venda_data)
            id_venda = cursor.lastrowid # Pega o ID da venda que acabou de ser criada.
            print(f"ID da Venda: {id_venda}")

            # INSERIR NA TABELA `vendas_itens`
            query_item = """
                INSERT INTO vendas_itens (id_venda, id_material_base, id_material_catalogo, quantidade_kg, preco_por_kg)
                VALUES (%s, %s, %s, %s, %s)
            """
            print(ids)
            item_data = (
                id_venda,
                ids['id_material'],
                ids['id_subtipo'],      
                dados_frontend['quantidade'],
                dados_frontend['preco_por_kg']
            )
            cursor.execute(query_item, item_data)

            # 3. INSERIR NA TABELA `avaliacoes_compradores`
            query_avaliacao = """
                INSERT INTO avaliacoes_compradores 
                (id_venda, pontualidade_pagamento, logistica_entrega, qualidade_negociacao, comentario_livre)
                VALUES (%s, %s, %s, %s, %s)
            """
            nota = dados_frontend['avaliacao']['nota']
            avaliacao_data = (
                id_venda,
                nota, # Usando a mesma nota para as três colunas
                nota,
                nota,
                dados_frontend['avaliacao']['analise']
            )
            cursor.execute(query_avaliacao, avaliacao_data)
            id_avaliacao = cursor.lastrowid # Pega o ID da avaliação criada.
            print(f"ID da Avaliação: {id_avaliacao}")
            
            # 4. INSERIR NA TABELA `avaliacao_feedback_selecionado` (se houver tags)
            if ids['ids_tags_feedback']:
                query_tags = """
                    INSERT INTO avaliacao_feedback_selecionado (id_avaliacao, id_feedback_tag)
                    VALUES (%s, %s)
                """
                # Prepara uma lista de tuplas para inserção em lote
                tags_data = [(id_avaliacao, id_tag) for id_tag in ids['ids_tags_feedback']]
                cursor.executemany(query_tags, tags_data) # executemany é eficiente para múltiplas inserções.
                print("Tags de feedback selecionadas inseridas com sucesso.")

            # Se todas as operações foram bem-sucedidas, confirma a transação.
            self.connection_db.commit()
            print("\n SUCESSO! Transação concluída e dados salvos no banco.")
            return True

        except Exception as err:
            # Se qualquer erro ocorrer, desfaz todas as operações.
            print(f"\n ERRO DE BANCO DE DADOS! A transação será revertida. Erro: {err}")
            self.connection_db.rollback()
            return False
        finally:
            # Garante que o cursor seja fechado, independentemente de sucesso ou falha.
            cursor.close()

    def get_by_coop(self, id_cooperativa):
        """
        Busca as vendas de uma respectiva cooperativa

        param: id_cooperativa -> da respectiva cooperativa em que está sendo buscada
        
        return: [] -> contendo todas as vendas já feitas pela cooperativa
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT 
                    mb.nome,
                    mc.nome_especifico,
                    com.razao_social as nome_comprador,
                    coop.razao_social as nome_vendedor,
                    v.valor_total,
                    v.data_venda
                FROM vendas v
                JOIN cooperativas coop ON v.id_cooperativa = coop.id_cooperativa
                JOIN compradores com ON v.id_comprador = com.id_comprador
                JOIN vendas_itens vi ON v.id_venda = vi.id_venda
                JOIN materiais_base mb ON vi.id_material_base = mb.id_material_base
                JOIN materiais_catalogo mc ON vi.id_material_catalogo = mc.id_material_catalogo
                WHERE v.id_cooperativa = %s
                ORDER BY v.data_venda;
                """
                cursor.execute(query, (id_cooperativa,))
                results = cursor.fetchall()
                return results
            
        except Exception as e:
            print(e)
            
        finally:
            cursor.close()