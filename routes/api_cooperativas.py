from flask import Blueprint, request, jsonify
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa
from controllers.cnpj_controller import CNPJ
from controllers.email_controller import Email
# imports para garantir a funcionalidade de uploads de documentos
import os
from werkzeug.utils import secure_filename

api_cooperativas = Blueprint(
    
    'api_cooperativas', 
    __name__, 

    url_prefix='/api/cooperativas'
    
)

CNAES_PERMITIDOS = [3811400, 3831901, 3831999, 3832700, 3812200]
NATUREZAS_JURIDICAS_PERMITIDAS = [2143, 3999] 
PASTA_UPLOAD = 'static/uploads/documentos'
EXTENSOES_PERMITIDAS = {'pdf', 'png', 'jpg', 'jpeg'}

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and \
           nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS # Verifica se a extensão do arquivo está na constante

@api_cooperativas.route('/cadastrar', methods=['POST'])
def cadastrar ():

    conn = None

    try:

        data_cadastro = request.form
        campos_obrigatorios = ['nome', 'email', 'senha', 'cnpj']

        # 400 - Campos obrigatórios incompletos

        if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
            return jsonify({ 'error': f'Dados de cadastro inválidos, todos os campos são obrigatórios: {campos_obrigatorios}' }), 400

        # 400 - Senha com menos de 8 caractéres

        if len(data_cadastro['senha']) < 8:
            return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
        
        #region Validação Arquivo ATA

        if 'documento' not in request.files:
             return jsonify({'error': 'O arquivo do documento ATA é obrigatório.'}), 400

        arquivo = request.files['documento']

        if arquivo.filename == '':
            return jsonify({'error': 'Nome do arquivo vazio.'}), 400

        if not arquivo.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Tipo de arquivo não permitido.'}), 400

        #endregion

        # 400 - CNPJ Inválido

        if CNPJ.validar(data_cadastro['cnpj']):
            return jsonify({ 'error': 'CNPJ inválido. Revise e tente novamente' }), 400

        dados_cnpj = CNPJ.consultar(data_cadastro['cnpj'])

        # 503 - Erro ao consultar CNPJ (CNPJá)

        if not dados_cnpj:
            return jsonify({'error': 'Não foi possível consultar o CNPJ. Tente novamente mais tarde.'}), 503
        
        #region Verificação de Natureza Jurídica

        natureza_cooperativa = dados_cnpj.get('company', {}).get('nature', {}).get('id')

        # 400 - Código de Natureza Jurídica Inválido

        if not natureza_cooperativa in NATUREZAS_JURIDICAS_PERMITIDAS:
            return jsonify({'error': 'O CNPJ informado não pertence a uma Cooperativa ou Associação.'}), 400
        
        #endregion

        #region Verificação de CNAE

        cnae_principal_id = dados_cnpj.get('mainActivity', {}).get('id')
        cnaes_secundarios_ids = [act.get('id') for act in dados_cnpj.get('sideActivities', [])]

        cnae_valido = False

        if cnae_principal_id in CNAES_PERMITIDOS:
            cnae_valido = True

        else:

            for cnae_sec_id in cnaes_secundarios_ids:

                if cnae_sec_id in CNAES_PERMITIDOS:
                    cnae_valido = True
                    break

        # 400 - CNAE Inválido

        if not cnae_valido:
            return jsonify({'error': 'O CNPJ informado não possui CNAE compatível com cooperativas de reciclagem.'}), 400

        #endregion

        id_status_atividade_cooperativa = dados_cnpj.get('status', {}).get('id')

        # IDS de Status:
        #
        # 1 = Nulo
        # 2 = Ativa
        # 3 = Suspensa
        # 4 = Inapta
        # 8 = Baixada

        # 400 - CNPJ Inativo

        if id_status_atividade_cooperativa != 2:
            return jsonify({'error': 'O CNPJ informado está inativo.'}), 400

        conn = Connection('local')

        conn.connection_db.start_transaction()
        print("Transação iniciada")

        id_usuario_criado = Usuarios(conn.connection_db).create(

            nome=data_cadastro['nome'],
            email=data_cadastro['email'],
            senha=data_cadastro['senha'],
            tipo='cooperativa'

        )

        match id_usuario_criado:

            # 409 - Email já cadastrado

            case None:
                return jsonify({'error': 'Este email já está cadastrado.'}), 409
            
            # Usuário da cooperativa criado

            case _ if isinstance(id_usuario_criado, int):

                addr = dados_cnpj.get('address', {})
                company = dados_cnpj.get('company', {})
                phones = dados_cnpj.get('phones', [{}]) # Telefones (pode haver mais de 1 no JSON)

                #region Upload Documento ATA

                filename_base = secure_filename(f"doc_coop_{id_usuario_criado}")
                extension = arquivo.filename.rsplit('.', 1)[1].lower()
                filename = f"{filename_base}.{extension}"
                
                # Cria a pasta de uploads se ela não existir
                os.makedirs(PASTA_UPLOAD, exist_ok=True)
                
                filepath = os.path.join(PASTA_UPLOAD, filename)
                arquivo.save(filepath)
                
                # Salva o caminho no banco de dados
                arquivo_url = f"uploads/documentos/{filename}"

                #endregion

                dados_criar_coop = {
                    "id_usuario": id_usuario_criado,
                    "cnpj": data_cadastro['cnpj'],
                    "razao_social": company.get('name', 'Razão Social não encontrada'),
                    "nome_fantasia": dados_cnpj.get('alias', 'Nome Fantasia não encontrado'),
                    "email": dados_cnpj.get('email', data_cadastro['email']),
                    "telefone": phones[0].get('number', 'Telefone não encontrado'), # Pega o primeiro telefone
                    "rua": addr.get('street', ''),
                    "numero": addr.get('number', ''),
                    "distrito": addr.get('district', ''),
                    "cidade": addr.get('city', ''),
                    "estado": addr.get('state', ''),
                    "cep": addr.get('zip', ''),
                    "arquivo_url": arquivo_url
                }

                id_cooperativa_criada = Cooperativa(conn.connection_db).create(**dados_criar_coop)

                match id_cooperativa_criada:

                    # 409 - CNPJ já cadastrado

                    case None:
                        conn.connection_db.rollback()
                        return jsonify({'error': 'Este CNPJ já está cadastrado.'}), 409

                    # 201 - Cooperativa criada pendente e aguardando aprovação

                    case _ if isinstance(id_cooperativa_criada, int):

                        conn.connection_db.commit() 
                        print("Transação concluída com sucesso")
                        
                        return jsonify({
                            'texto': 'Cadastro realizado com sucesso! Sua conta está pendente e está aguardando aprovação.',
                            'id_cooperativa': id_cooperativa_criada
                        }), 201

                    # 500 - Erro Interno

                    case False | _:
                        conn.connection_db.rollback()
                        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500

            # 500 - Erro Interno

            case False | _:
                return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    except Exception as e:
        print(f"Erro original que causou o rollback: {e}")
        if conn and conn.connection_db.is_connected():

            try:
                if conn.connection_db.in_transaction:
                    conn.connection_db.rollback()
                    print("Rollback efetuado devido a exceção.")

            except Exception as rollback_err:
                print(f"Erro durante o rollback: {rollback_err}")
        
        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    finally:
        if conn:
            conn.close()

@api_cooperativas.route('/get/<identificador>', methods=['POST'])
def get (identificador:int|str):

    if identificador.isdigit():
        identificador = int(identificador)

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        user = Usuarios(conn.connection_db).get(data_token['id_usuario'])
        if not user['tipo'] in ['cooperativa','gestor', 'root']:
        
            
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        elif user['tipo'] == 'cooperativa':
            
            # Pega os dados da cooperativa VINCULADA AO TOKEN
            dados_cooperativa_logada = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(user['id_usuario'])
            if not dados_cooperativa_logada:
                return jsonify({'error': 'Cooperativa associada a este usuário não encontrada.'}), 404

            # Compara se o 'identificador' da URL bate com algum dos IDs
            # da cooperativa que está logada.
            if (identificador != dados_cooperativa_logada['id_usuario']):
                # Se o ID da URL não bate com NENHUM, é uma tentativa de acesso indevido.
                return jsonify({'error': 'Acesso negado. Você só pode consultar os dados da sua própria cooperativa.'}), 403
        dados_cooperativa = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(identificador)

        match dados_cooperativa:

            # 200 - Cooperativa consultada com sucesso

            case _ if isinstance(dados_cooperativa, dict):
        
                return jsonify({ 'dados_cooperativa': dados_cooperativa }), 200

            # 500 - Erro ao consultar cooperativa

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/get-all', methods=['POST'])
def get_all ():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        dados_cooperativas = Cooperativa(conn.connection_db).get_all()

        match dados_cooperativas:

            # 200 - Todas as cooperativas foram consultadas com sucesso

            case _ if isinstance(dados_cooperativas, list):
        
                return jsonify({ 'dados_cooperativas': dados_cooperativas }), 200

            # 500 - Erro ao consultar cooperativas

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/alterar-aprovacao', methods=['POST'])
def alterar_aprovacao():

    data = request.get_json()
    id_cooperativa = data.get('id_cooperativa')
    aprovacao = data.get('aprovacao')


    if not id_cooperativa or aprovacao is None:
        return jsonify({'error': 'id_cooperativa e aprovacao são obrigatórios'}), 400


    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({'error': 'token é parâmetro obrigatório'}), 400


    conn = Connection('local')
    if not conn.connection_db:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    db = conn.connection_db
    try:
        token = token_header.split(' ')[1]
        data_token = Tokens(db).validar(token)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido'}), 401

        id_usuario_gestor = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario_gestor)

        if not usuario_info or usuario_info['tipo'] not in ['gestor', 'root']:
            conn.close()
            return jsonify({'error': 'Você não tem permissão para realizar tal ação'}), 403

        coop_ctrl = Cooperativa(db)
        cooperativa = coop_ctrl.get_by_id(int(id_cooperativa))

        if not cooperativa:
            conn.close()
            return jsonify({'error': 'Cooperativa não encontrada'}), 404


        id_usuario_cooperativa = cooperativa['id_usuario']


        # Garante que não há transação pendente na conexão antes de iniciar
        try:
            if db.in_transaction:
                db.rollback()
        except Exception:
            pass

        db.start_transaction()

        sucesso_coop = coop_ctrl.alterar_aprovacao(int(id_cooperativa), bool(aprovacao))
        sucesso_user = Usuarios(db).alterar_status(int(id_usuario_cooperativa), 'ativo' if aprovacao else 'inativo')


        if sucesso_coop and sucesso_user:
            # Commit primeiro para garantir que a alteração seja salva
            db.commit()
            
            # Envia email de aprovação ou reprovação (não bloqueia se falhar)
            try:
                usuario_coop = Usuarios(db).get(int(id_usuario_cooperativa))
                if usuario_coop and usuario_coop.get('email'):
                    if bool(aprovacao):
                        assunto = "Cadastro no Recoopera Aprovado"
                        corpo_html = Email.gerar_template_aprovacao(cooperativa.get('razao_social', 'Cooperativa'))
                        Email.enviar(usuario_coop['email'], assunto, corpo_html)
                    else:
                        # Email de reprovação sem motivo específico (quando usado através de /alterar-aprovacao)
                        assunto = "Cadastro no Recoopera Rejeitado"
                        motivo = "Aprovação negada"
                        justificativa = "Seu cadastro foi rejeitado. Entre em contato conosco para mais informações."
                        corpo_html = Email.gerar_template_rejeicao(
                            cooperativa.get('razao_social', 'Cooperativa'),
                            motivo,
                            justificativa
                        )
                        Email.enviar(usuario_coop['email'], assunto, corpo_html)
            except Exception as email_error:
                # Log do erro mas não bloqueia a resposta de sucesso
                print(f"Erro ao enviar email (não crítico): {email_error}")
            
            return jsonify({'texto': 'Status da cooperativa alterado com sucesso!'}), 200
        else:
            db.rollback()
            return jsonify({'error': 'Erro ao atualizar status (coop ou user).'}), 500

    except Exception as e:
        try:
            if db and db.in_transaction:
                db.rollback()
        except Exception:
            pass
        print(f"Erro em /alterar-aprovacao: {e}")
        return jsonify({'error': f'Erro no servidor: {e}'}), 500
    finally:
        conn.close()

@api_cooperativas.route('/vincular-cooperado', methods=['POST'])
def vincular_cooperado ():

    data_cooperado = request.get_json()

    if not data_cooperado or not all(key in data_cooperado for key in ['nome', 'email', 'senha', 'cpf', 'telefone', 'endereco', 'cidade', 'estado']):
        
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, senha, email, cpf, telefone, endereco, cidade e estado' }), 400
    
    if len(data_cooperado['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        # Token Inválido

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" inválido' }), 400

        data_adm_cooperativa = Usuarios(conn.connection_db).get(data_token['id_usuario'])

        # Autor da requisição inválido

        if not data_adm_cooperativa or data_adm_cooperativa['tipo'] != 'cooperativa':
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        data_cooperativa = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(data_adm_cooperativa['id_usuario'])
        print(data_cooperativa)
        id_cooperado = Cooperativa(conn.connection_db).vincular_cooperado(

            data_cooperativa['id_cooperativa'],

            data_cooperado['nome'],
            data_cooperado['email'],
            data_cooperado['senha'],
            
            data_cooperado['cpf'],
            data_cooperado['telefone'],
            data_cooperado['endereco'],
            data_cooperado['cidade'],
            data_cooperado['estado']

        )
        print(id_cooperado)
        match id_cooperado:

            # 409 - Email já cadastrado

            case None:
                return jsonify({ 'error': 'Email já cadastrado' }), 409

            # 200 - Usuário cooperado vinculado

            case _ if isinstance(id_cooperado, int):
                
                return jsonify({ 'texto': 'Cooperado vinculado' }), 200

            # 500 - Erro ao vincular usuário cooperado

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/enviar-documento', methods=['POST'])
def enviar_documento():
    
    conn = None
    try:

        if 'documento' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
        id_cooperativa = request.form.get('id_cooperativa')
        if not id_cooperativa:
            return jsonify({'error': 'ID da cooperativa não fornecido.'}), 400

        arquivo = request.files['documento']

        if arquivo.filename == '':
            return jsonify({'error': 'Nome do arquivo vazio.'}), 400

        if not arquivo_permitido(arquivo.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido.'}), 400
            
        conn = Connection('local')
        
        # Criação de um nome de arquivo seguro e único | EX: doc_coop_5.pdf
        filename_base = secure_filename(f"doc_coop_{id_cooperativa}")
        extension = arquivo.filename.rsplit('.', 1)[1].lower()
        filename = f"{filename_base}.{extension}"
        
        # Cria a pasta de uploads se ela não existir
        os.makedirs(PASTA_UPLOAD, exist_ok=True)
        
        filepath = os.path.join(PASTA_UPLOAD, filename)
        arquivo.save(filepath)
        
        # Salva o caminho no banco de dados
        arquivo_url = f"uploads/documentos/{filename}"
        
        id_documento = Cooperativa(conn.connection_db).adicionar_documento(
            id_cooperativa=int(id_cooperativa),
            arquivo_url=arquivo_url
        )

        if id_documento:
            conn.connection_db.commit()
            return jsonify({'texto': 'Documento enviado com sucesso! Aguarde a aprovação.'}), 201
        else:
            conn.connection_db.rollback()
            return jsonify({'error': 'Erro ao salvar documento no banco de dados.'}), 500

    except Exception as e:
        print(f"Erro em /enviar-documento: {e}")
        if conn:
            conn.connection_db.rollback()
        return jsonify({'error': 'Ocorreu um erro interno no servidor.'}), 500
    
    finally:
        if conn:
            conn.close()

@api_cooperativas.route('/rejeitar', methods=['POST'])
def rejeitar_cooperativa():

    token_header = request.headers.get('Authorization')
    data = request.get_json()
    id_cooperativa = data.get('id_cooperativa')
    email_cooperativa = data.get('email')
    motivo = data.get('motivo')
    justificativa = data.get('justificativa')


    if not all([token_header, id_cooperativa, email_cooperativa, motivo, justificativa]):
        return jsonify({'error': 'Dados incompletos'}), 400


    conn = Connection('local')
    if not conn.connection_db:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    db = conn.connection_db
    try:
        token = token_header.split(' ')[1]
        data_token = Tokens(db).validar(token)
        if not data_token:
            conn.close()
            return jsonify({'error': 'Token inválido'}), 401

        id_usuario_gestor = data_token['id_usuario']
        usuario_info = Usuarios(db).get(id_usuario_gestor)
        if not usuario_info or usuario_info['tipo'] not in ['gestor', 'root']:
            conn.close()
            return jsonify({'error': 'Acesso não autorizado'}), 403

        try:
            if db.in_transaction:
                db.rollback()
        except Exception:
            pass

        db.start_transaction()
        coop_ctrl = Cooperativa(db)
        sucesso_doc = coop_ctrl.rejeitar_documento(int(id_cooperativa), int(id_usuario_gestor), motivo, justificativa)


        cooperativa_data = coop_ctrl.get_by_id(int(id_cooperativa))
        if not cooperativa_data:
            db.rollback()
            conn.close()
            return jsonify({'error': 'Cooperativa não encontrada para rejeitar'}), 404

        id_usuario_cooperativa = cooperativa_data['id_usuario']
        sucesso_user = Usuarios(db).alterar_status(int(id_usuario_cooperativa), 'bloqueado')


        if not (sucesso_doc and sucesso_user):
            db.rollback()
            conn.close()
            return jsonify({'error': 'Erro ao atualizar o status no banco de dados.'}), 500

        # Commit primeiro para garantir que a alteração seja salva
        db.commit()

        # Envia email de rejeição com template HTML bonito (não bloqueia se falhar)
        try:
            assunto = "Cadastro no Recoopera Rejeitado"
            razao_social = cooperativa_data.get('razao_social', 'Cooperativa')
            corpo_html = Email.gerar_template_rejeicao(razao_social, motivo, justificativa)
            Email.enviar(email_cooperativa, assunto, corpo_html)
        except Exception as email_error:
            # Log do erro mas não bloqueia a resposta de sucesso
            print(f"Erro ao enviar email (não crítico): {email_error}")

        return jsonify({'message': 'Cooperativa rejeitada e e-mail enviado.'}), 200


    except Exception as e:
        try:
            if db and db.in_transaction:
                db.rollback()
        except Exception:
            pass
        print(f"Erro em /rejeitar: {e}")
        return jsonify({'error': f'Erro interno no servidor: {e}'}), 500
    finally:
        conn.close()