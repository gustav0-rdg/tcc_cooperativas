from data.connection_controller import Connection
from mysql.connector import MySQLConnection
import datetime
from controllers.avaliacoes_controller import Avaliacoes

class Vendas:
    def __init__(self, connection_db:MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Tokens: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

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
            raise ValueError(f"Nenhum comprador ativo encontrado para o CNPJ: {cnpj}")

    def _buscar_id_material(self, nome_material: str) -> int:
        """
        Busca o ID de um material ativo na tabela `materiais_catalogo`.

        Args:
            nome_material (str): O nome exato do material.

        Returns:
            int: O ID do material encontrado.

        Raises:
            MaterialNaoEncontradoError: Se nenhum material ativo for encontrado com o nome fornecido.
        """
        with self.connection_db.cursor() as cursor:
            # Buscamos pelo nome e garantimos que o material esteja 'ativo'.
            query = "SELECT id_material_base FROM materiais_base WHERE nome = %s"
            cursor.execute(query, (nome_material,))
            result = cursor.fetchone()

        if result:
            id_material = result[0]
            print(f"Material encontrado: '{nome_material}' corresponde ao ID {id_material}.")
            return id_material
        else:
            raise ValueError(f"Nenhum material ativo chamado '{nome_material}' foi encontrado no catálogo.")
        
    def _buscar_ids(self, dados_frontend: dict):
        """
        Busca e valida os IDs necessários para registrar a venda a partir dos dados do frontend.
        """
        try:
            # Valida e busca o ID do comprador pelo CNPJ
            cnpj_comprador = dados_frontend['vendedor']['cnpj']
            id_comprador = self._buscar_id_comprador(cnpj_comprador)

            # Valida e busca o ID da categoria do material
            nome_material_categoria = dados_frontend['material']['categoria']
            id_material_categoria = self._buscar_id_material(nome_material_categoria)

            # USA DIRETAMENTE O ID DO MATERIAL DO CATÁLOGO ENVIADO PELO FRONTEND
            id_subtipo = dados_frontend['material']['id_material_catalogo']
            if not isinstance(id_subtipo, int):
                raise ValueError("O 'id_material_catalogo' é inválido ou não foi fornecido.")
            
            print(f"Material (Subtipo) ID fornecido diretamente: {id_subtipo}.")
            
            return {
                "id_comprador": id_comprador,
                "id_material": id_material_categoria,
                "id_subtipo": id_subtipo
            }

        except Exception as e:
            print(f"Erro de negócio ao validar IDs: {e}")
            return None
        
    def registrar_nova_venda(self, id_cooperativa, dados_frontend):
        """
        Orquestra a criação completa de uma venda, seus itens e avaliação dentro de uma transação.
        """
        print('dados frontedn', dados_frontend)
        ids = self._buscar_ids(dados_frontend)
        if not ids:
            return False 

        cursor = self.connection_db.cursor()

        try:
            # 1. INSERIR NA TABELA `vendas`
            query_venda = """
                INSERT INTO vendas (id_cooperativa, id_comprador, data_venda, valor_total)
                VALUES (%s, %s, %s, %s)
            """
            venda_data = (
                id_cooperativa,
                ids['id_comprador'],
                datetime.datetime.now(),
                dados_frontend['total']
            )
            cursor.execute(query_venda, venda_data)
            id_venda = cursor.lastrowid
            print(f"ID da Venda: {id_venda}")

            # 2. INSERIR NA TABELA `vendas_itens`
            total_item = float(dados_frontend['quantidade']) * float(dados_frontend['preco_por_kg'])
            query_item = """
                INSERT INTO vendas_itens (id_venda, id_material_catalogo, quantidade_kg, preco_por_kg, total_item)
                VALUES (%s, %s, %s, %s, %s)
            """
            item_data = (
                id_venda,
                ids['id_subtipo'],
                dados_frontend['quantidade'],
                dados_frontend['preco_por_kg'],
                total_item
            )
            cursor.execute(query_item, item_data)
            print(f"Item da venda inserido para a venda ID: {id_venda}")

            # 3. INSERIR AVALIAÇÃO PENDENTE E FINALIZAR IMEDIATAMENTE
            avaliacoes_controller = Avaliacoes(self.connection_db)
            
            # Primeiro, insere a avaliação como "pendente" para obter um ID
            id_avaliacao_pendente = avaliacoes_controller.inserir_avaliacao_pendente(id_venda, id_cooperativa)
            if not id_avaliacao_pendente:
                raise Exception("Falha ao criar o registro de avaliação pendente.")
            print(f"Registro de avaliação pendente criado com ID: {id_avaliacao_pendente}")

            # Agora, finaliza a avaliação imediatamente usando os dados do frontend
            dados_avaliacao = dados_frontend.get('avaliacao')
            if dados_avaliacao:
                sucesso_finalizacao = avaliacoes_controller.finalizar_avaliacao_pendente(id_avaliacao_pendente, dados_avaliacao)
                if not sucesso_finalizacao:
                    raise Exception("Falha ao finalizar a avaliação da venda.")
                print(f"Avaliação para a venda {id_venda} finalizada imediatamente.")
            else:
                print("Nenhum dado de avaliação fornecido com a venda.")

            self.connection_db.commit()
            print("\n SUCESSO! Transação concluída e dados salvos no banco.")
            return {"sucesso": True, "id_avaliacao_pendente": None} # Não há mais pendência

        except Exception as err:
            print(f"\n ERRO DE BANCO DE DADOS! A transação será revertida. Erro: {err}")
            self.connection_db.rollback()
            return {"sucesso": False, "id_avaliacao_pendente": None}
        finally:
            cursor.close()

    def get_by_coop(self, id_cooperativa):
        """
        Busca as vendas de uma respectiva cooperativa usando a view v_vendas_detalhadas.

        param: id_cooperativa -> da respectiva cooperativa em que está sendo buscada
        
        return: [] -> contendo todas as vendas já feitas pela cooperativa
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT
                    material_categoria AS nome,
                    material_nome AS nome_especifico,
                    comprador_nome AS nome_comprador,
                    cooperativa_nome AS nome_vendedor,
                    valor_total,
                    data_venda
                FROM v_vendas_detalhadas
                WHERE id_cooperativa = %s
                ORDER BY data_venda;
                """
                cursor.execute(query, (id_cooperativa,))
                results = cursor.fetchall()
                return results
            
        except Exception as e:
            print(e)
            
        finally:
            cursor.close()