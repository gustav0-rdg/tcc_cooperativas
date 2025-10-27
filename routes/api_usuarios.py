from flask import Blueprint, request, jsonify
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa
from controllers.cnpj_controller import CNPJ
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from datetime import datetime, timedelta

api_usuarios = Blueprint(
    
    'api_usuarios', 
    __name__, 

    url_prefix='/api/usuarios'
    
)

# CNAEs permitidos
CNAES_PERMITIDOS = [3811400, 3831901, 3831999, 3832700, 3812200]
NATUREZA_JURIDICA_COOPERATIVA = 2143 # Código para Cooperativa

@api_usuarios.route('/cadastrar', methods=['POST'])
def cadastrar ():
    conn = None

    try:
        data_cadastro = request.get_json()
        campos_obrigatorios = ['nome', 'email', 'senha', 'cnpj']

        # Validação dos dados
        if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
            return jsonify({'error': f'Dados de cadastros inválidos. Campos obrigatórios: {", ".join(campos_obrigatorios)}'}),400

        if len(data_cadastro['senha']) < 8:
            return jsonify({'error': 'A senha deve ter no mínimo 8 caracteres'}), 400
        
        cnpj_limpo = ''.join(filter(str.isdigit, data_cadastro['cnpj']))
        if len(cnpj_limpo) != 14:
            ({'error': 'CNPJ inválido. Deve conter 14 dígitos'}), 400

        # Validação de negócio
        print(f"Consultando CNPJ: {cnpj_limpo}")
        dados_cnpj = CNPJ.consultar(cnpj_limpo)

        if not dados_cnpj:
            print("Erro: API CNPJ não retornou dados")
            return jsonify({'error': 'Não foi possível validar o CNPJ. Tente novamente mais tarde.'}), 503 # Código de serviço indisponível
        
        # Verificação de natureza
        natureza_id = dados_cnpj.get('company', {}).get('nature', {}).get('id')
        if natureza_id != NATUREZA_JURIDICA_COOPERATIVA:
            print(f"Natureza jurídica inválida: {natureza_id}")
            return jsonify({'error': 'O CNPJ informado não pertence a uma Cooperativa (Natureza Jurídica incorreta).'}), 400
        
        # Verificação de CNAE
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

        if not cnae_valido:
            print(f"CNAE inválido. Principal: {cnae_principal_id}, Secundários: {cnaes_secundarios_ids}")
            return jsonify({'error': 'O CNPJ informado não possui CNAE compatível com cooperativas de reciclagem.'}), 400

        print("CNPJ validado com sucesso!")

        # Banco de dados
        conn = Connection('online')
        db = conn.connection_db
        usuarios_ctrl = Usuarios(db)
        cooperativa_ctrl = Cooperativa(db)

        id_usuario_criado = None
        id_cooperativa_criada = None

        db.start_transaction()
        print("Transação iniciada")

        id_usuario_criado = usuarios_ctrl.create(
            nome=data_cadastro['nome'],
            email=data_cadastro['email'],
            senha=data_cadastro['senha'],
            tipo='cooperativa' # Status já é dado como 'pendente' default
        )
        
        if not id_usuario_criado:
            # Verifica a natureza do erro
            cursor_check = db.cursor()
            cursor_check.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (data_cadastro['email'],))
            if cursor_check.fetchone():
                cursor_check.close()
                db.rollback()
                print("Rollback: Email duplicado.")
                return jsonify({'error': 'Este email já está cadastrado.'}), 409 # Conflict
            else:
                cursor_check.close()
                db.rollback()
                print("Rollback: Erro desconhecido ao criar usuário.")
                raise Exception("Falha ao criar usuário por motivo desconhecido") # Cai no except geral

        print(f"Usuário criado: {id_usuario_criado}")

        addr = dados_cnpj.get('address', {})
        endereco_completo = f"{addr.get('street', '')}, {addr.get('number', '')} {addr.get('details', '')} - {addr.get('district', '')}"

        id_cooperativa_criada = cooperativa_ctrl.create(
            id_usuario=id_usuario_criado,
            cnpj=cnpj_limpo,
            razao_social=dados_cnpj.get('company', {}).get('name', 'Razão Social não encontrada'),
            endereco=endereco_completo.strip(" ,-"),
            cidade=addr.get('city'),
            estado=addr.get('state')
            # Latitude e longitude (não essencial por agora)
        )

        if not id_cooperativa_criada:
            db.rollback()
            print("Rollback: Erro ao criar cooperativa (verificar logs do controller).")
             # Poderia ser CNPJ duplicado ou outro erro
            cursor_check = db.cursor()
            cursor_check.execute("SELECT id_cooperativa FROM cooperativas WHERE cnpj = %s", (cnpj_limpo,))
            if cursor_check.fetchone():
                 cursor_check.close()
                 return jsonify({'error': 'Este CNPJ já está cadastrado.'}), 409
            else:
                 cursor_check.close()
                 raise Exception("Falha ao criar cooperativa por motivo desconhecido") # Cai no except geral

        print(f"Cooperativa criada: {id_cooperativa_criada}")

        db.commit()
        print("Commit realizado.")
        return jsonify({'message': 'Cadastro realizado com sucesso! Sua conta está pendente e está aguardando aprovação.'}), 201
    
    except Exception as e:
        print(f"Erro GERAL na rota /cadastrar: {e}")
        if conn and conn.connection_db.is_connected():
            try:
                # Tenta fazer rollback
                if conn.connection_db.in_transaction():
                    print("Realizando rollback devido a erro...")
                    conn.connection_db.rollback()
            except Exception as rollback_err:
                print(f"Erro durante o rollback: {rollback_err}")

        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    finally:
        if conn:
            conn.close()
            print("Conexão fechada")

@api_usuarios.route('/login/<tipo_usuario>', methods=['POST'])
def login (tipo_usuario):

    """
    Rota unificada para login. Aceita 'cooperativa', 'cooperado', 'gestor', 'root'.
    Espera JSON com 'identificador' (email ou cpf) e 'senha'.
    """

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Requisição sem corpo JSON'}), 400

    identificador = data.get('identificador')
    senha = data.get('senha')
    tipos_validos = ['cooperativa', 'cooperado', 'gestor', 'root']

    # Validações básicas
    if tipo_usuario not in tipos_validos:
         return jsonify({'error': f'Tipo de usuário inválido: {tipo_usuario}'}), 400
    if not identificador or not senha:
        return jsonify({'error': 'Identificador (email/CPF) e senha são obrigatórios'}), 400

    conn = None
    try:
        conn = Connection('online')
        db = conn.connection_db
        usuarios_ctrl = Usuarios(db)
        tokens_ctrl = Tokens(db)

        id_usuario_autenticado = usuarios_ctrl.autenticar(identificador, senha)

        if id_usuario_autenticado is None: # Usuário não encontrado ou senha incorreta
            print(f"Falha na autenticação para: {identificador}")
            return jsonify({'error': 'Identificador ou senha inválidos'}), 401
        elif id_usuario_autenticado is False: # Erro no banco durante autenticação
             print(f"Erro no banco ao autenticar: {identificador}")
             return jsonify({'error': 'Erro ao verificar credenciais'}), 500

        usuario_info = usuarios_ctrl.get_by_id(id_usuario_autenticado)
        if not usuario_info:
            print(f"Erro: Usuário autenticado ({id_usuario_autenticado}) não encontrado ao buscar dados.")
            return jsonify({'error': 'Erro interno ao buscar dados do usuário'}), 500

        if usuario_info['tipo'] != tipo_usuario:
            print(f"Falha no login: Tipo incorreto. Esperado: {tipo_usuario}, Recebido: {usuario_info['tipo']}")
            return jsonify({'error': f'Login não permitido para este tipo de conta ({tipo_usuario}).'}), 403

        if usuario_info['status'] != 'ativo':
             print(f"Falha no login: Status não ativo ({usuario_info['status']}) para usuário {id_usuario_autenticado}")
             mensagem_erro = f"Sua conta está {usuario_info['status']}. Entre em contato com o suporte."
             if usuario_info['status'] == 'pendente':
                  mensagem_erro = "Sua conta ainda está pendente de aprovação."
             return jsonify({'error': mensagem_erro}), 403

        # Gerar Token de Sessão
        data_expiracao = datetime.now() + timedelta(days=30) # Token válido por 30 dias
        token = tokens_ctrl.create(id_usuario_autenticado, 'sessao', data_expiracao)

        if not token:
             print(f"Erro ao gerar token de sessão para usuário {id_usuario_autenticado}")
             return jsonify({'error': 'Erro ao iniciar sessão'}), 500

        print(f"Login bem-sucedido para {identificador} (Usuário ID: {id_usuario_autenticado}, Tipo: {tipo_usuario}). Token gerado.")

        # Retornar Token
        return jsonify({'token': token}), 200

    except Exception as e:
        print(f"Erro GERAL na rota /login/{tipo_usuario}: {e}")

        if conn and conn.connection_db and conn.connection_db.is_connected() and conn.connection_db.in_transaction:
            try: conn.connection_db.rollback()
            except Exception as rb_err: print(f"Erro durante rollback no login: {rb_err}")
        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o login.'}), 500

    finally:
        if conn:
            conn.close()
            print("Conexão fechada (login).")
    
# @api_usuarios.route('/logout', methods=['POST'])
# @require_login # Decorador que valida o token e injeta dados do usuário
# def logout(usuario_logado): # Recebe dados do usuário do decorador
    conn = None
    try:
        token_header = request.headers.get('Authorization')
        token_valor = token_header.split(" ")[1] if token_header and " " in token_header else None

        if not token_valor:
            return jsonify({'error': 'Token não fornecido'}), 401

        conn = Connection('online')
        db = conn.connection_db
        tokens_ctrl = Tokens(db)


        sucesso = tokens_ctrl.invalidar_token(token_valor)

        if sucesso:
            print(f"Logout bem-sucedido para usuário {usuario_logado['id_usuario']}")
            return jsonify({'message': 'Logout realizado com sucesso'}), 200
        else:
            print(f"Erro ao invalidar token durante logout para usuário {usuario_logado['id_usuario']}")
            return jsonify({'error': 'Erro ao finalizar sessão'}), 500

    except Exception as e:
        print(f"Erro GERAL na rota /logout: {e}")
        return jsonify({'error': 'Erro interno no servidor durante logout'}), 500
    finally:
        if conn:
            conn.close()
            print("Conexão fechada (logout).")

@api_usuarios.route('/alterar-senha', methods=['POST'])
def alterar_senha ():

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({ 'texto': '"token" é parâmetro obrigatório' }), 400

    data = request.get_json()
    nova_senha = data.get('nova-senha')

    if not nova_senha:
        return jsonify({ 'texto': '"nova-senha" é parâmetro obrigatório' }), 400
    
    if len(nova_senha) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'recuperacao_senha':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        match Usuarios(conn.connection_db).trocar_senha(data_token['id_usuario']):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Senha do usuário alterada

            case True:

                Tokens(conn.connection_db).set_state(data_token['id_token'])
                return jsonify({ 'texto': 'Senha alterada com sucesso' }), 200

            # 500 - Erro ao alterar a senha do usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/delete', methods=['POST'])
@api_usuarios.route('/delete/<id_usuario>', methods=['POST'])
def delete (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Excluindo a conta de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
            
        #endregion
        
        match Usuarios(conn.connection_db).delete(id_usuario):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Usuário Excluído

            case True:
                return jsonify({ 'texto': 'Usuário excluído' }), 200

            # 500 - Erro ao excluir usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/get', methods=['POST'])
@api_usuarios.route('/get/<id_usuario>', methods=['POST'])
def get_info (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Consultando info de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        data_usuario = Usuarios(conn.connection_db).get_by_id(id_usuario)
        match data_usuario:

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Informações do usuário consultadas

            case _ if isinstance(data_usuario, dict):
                return jsonify({ 'data': data_usuario }), 200

            # 500 - Erro ao consultar as informações usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/alterar-status', methods=['POST'])
@api_usuarios.route('/alterar-status/<id_usuario>', methods=['POST'])
def alterar_status (id_usuario:int=None):

    data = request.get_json()

    novo_status = data.get('novo-status')
    if not novo_status:
        return jsonify({ 'error': '"novo-status" é um parâmetro obrigatório' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token:
            return jsonify({ 'error': 'Token inválido' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        match novo_status:

            case 'ativo':

                if not (data_token['tipo'] == 'cadastro' or (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa')):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403
                
            case 'inativo' | 'bloqueado':

                if not (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa'):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403

            case _:

                return jsonify({ 'error': '"novo-status" inválido' }), 400

        #region Alterando o status de terceiros

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        match Usuarios(conn.connection_db).alterar_status(id_usuario, novo_status):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Status do usuário alterado

            case True:
                return jsonify({ 'texto': 'Status do usuário alterado' }), 200

            # 500 - Erro ao alterar o status

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()
