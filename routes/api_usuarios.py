from flask import Blueprint, request, jsonify, url_for
from controllers.usuarios_controller import Usuarios
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from controllers.email_controller import Email
from datetime import datetime, timedelta

api_usuarios = Blueprint(
    
    'api_usuarios', 
    __name__, 

    url_prefix='/api/usuarios'
    
)

@api_usuarios.route('/cadastrar', methods=['POST'])
def cadastrar ():

    token = request.headers.get('Authorization')

    data_cadastro = request.get_json()
    campos_obrigatorios =  ['nome', 'email', 'senha', 'tipo']

    # 400 - Campos obrigatórios incompletos

    if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, email e senha' }), 400

    # 400 - Senha com menos de 8 caractéres

    if len(data_cadastro['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
    
    conn = Connection('local')

    try:

        #region Cadastro de pessoas com permissões especiais

        if data_cadastro['tipo'] != 'cooperativa':

            if not token:
                return jsonify({ 'error': 'Para este tipo de ação é necessário token de autorização' }), 400
            
            data_token = Tokens(conn.connection_db).validar(token)
            if not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
                return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
            
        #endregion

        novo_usuario = Usuarios(conn.connection_db).create(

            data_cadastro['nome'],

            data_cadastro['email'],
            data_cadastro['senha'],

            data_cadastro['tipo']

        )

        match novo_usuario:

            # 200 - Usuário criado

            case _ if isinstance(novo_usuario, int):

                return jsonify({ 

                    'texto': 'Usuário cadastrado',
                    'id_usuario': novo_usuario

                }), 200

            # 500 - Erro ao criar usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/login', methods=['POST'])
def login_generico():

    conn = None

    try:
        data = request.get_json()
        print(data)
        identificador = data.get('identificador')
        senha = data.get('senha')

        if not identificador or not senha:
            return jsonify({'error': 'Identificador e senha são obrigatórios'}), 400
        
        conn = Connection('local')
        usuario_controller = Usuarios(conn.connection_db)
        
        token, status_msg = usuario_controller.autenticar(identificador, senha)
        
        conn.close() 

        if status_msg == "LOGIN_SUCESSO" and token:
            # Envia o token para o JavaScript
            return jsonify({'token': token}), 200
        else:
            # Falha na autenticação, traduz a mensagem
            erros = {
                "IDENTIFICADOR_NAO_ENCONTRADO": "Usuário não encontrado.",
                "SENHA_INVALIDA": "Senha inválida.",
                "USUARIO_PENDENTE": "Cadastro pendente de aprovação.",
                "USUARIO_INATIVO": "Este usuário está inativo.",
                "USUARIO_BLOQUEADO": "Este usuário foi bloqueado.",
                "COOPERATIVA_NAO_APROVADA": "Cadastro da cooperativa ainda não foi aprovado.",
                "COOPERADO_INATIVO": "Este cooperado está inativo.",
            }

            mensagem_erro = erros.get(status_msg, "Credenciais inválidas ou usuário não autorizado")
            return jsonify({'error': mensagem_erro}), 401

    except Exception as e:
        if conn: conn.close()
        print(f"Erro na rota /login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

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

        if not data_token or data_token['tipo'] != 'recuperacao_senha' or data_token['usado'] == False:
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        match Usuarios(conn.connection_db).trocar_senha(

            data_token['id_usuario'],
            nova_senha

        ):

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

@api_usuarios.route('/recuperacao-senha/<email>', methods=['GET'])
def solicitar_recuperacao_senha (email:str):

    conn = Connection('local')

    try:

        data_usuario = Usuarios(conn.connection_db).get(email)
        match data_usuario:

            # Usuário não encontrado ou usuário validado
            # Mesmo retorno para não gerar para não vazar informações

            case None | _ if isinstance(data_usuario, dict):

                if isinstance(data_usuario, dict):

                    token_alterar_senha = Tokens(conn.connection_db).create(

                        data_usuario['id_usuario'],
                        'recuperacao_senha',
                        
                        # Tempo de expiração em 2 horas
                        data_expiracao=datetime.now() + timedelta(hours=2)

                    )

                    match token_alterar_senha:

                        # Token Criado

                        case _ if isinstance(token_alterar_senha, str):

                            url_recuperacao = url_for(

                                'pages.pagina_redefinir_senha',

                                token=token_alterar_senha,
                                _external=True

                            )

                            corpo_html = Email.gerar_template_recuperacao_senha(

                                nome_usuario=data_usuario['nome'],
                                url_recuperacao=url_recuperacao

                            )

                            # 500 - Erro ao enviar e-mail

                            if not Email.enviar(

                                destinatario=email,
                                assunto='Recoopera - Redefinição de Senha',
                                formatacao_html=corpo_html

                            ):

                                return jsonify({ 'error': 'Erro ao enviar e-mail' }), 500
                            
                        # 500 - Erro ao criar token

                        case False | _:
                            return jsonify({ 'error': 'Erro ao criar token' }), 500    

                # 200 - Email de recuperação de senha enviado

                return jsonify({ 'texto': 'Se o email for válido, email enviado' }), 200      

            # 500 - Erro ao validar usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/delete', methods=['GET', 'POST'])
@api_usuarios.route('/delete/<id_usuario>', methods=['GET', 'POST'])
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

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:

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

@api_usuarios.route('/get', methods=['GET', 'POST'])
@api_usuarios.route('/get/<id_usuario>', methods=['GET', 'POST'])
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

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        print(id_usuario)

        data_usuario = Usuarios(conn.connection_db).get(id_usuario)
        match data_usuario:

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Informações do usuário consultadas

            case _ if isinstance(data_usuario, dict):
                return jsonify(data_usuario), 200

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

                if not (data_token['tipo'] == 'cadastro' or (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root'])):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403
                
            case 'inativo' | 'bloqueado':

                if not (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403

            case _:

                return jsonify({ 'error': '"novo-status" inválido' }), 400

        #region Alterando o status de terceiros

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:

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
        
@api_usuarios.route('/get-all-gestores', methods=['GET', 'POST'])
def get_all_gestores ():

    # 400 - Token Obrigatório

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

    conn = None
    try:

        conn = Connection('local')

        # 400 - Token Inválido

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        # 403 - Sem permissão

        if not Usuarios(conn.connection_db).get(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        data_gestores = Usuarios(conn.connection_db).get_all_gestores()
        match data_gestores:

            # 404 - Gestores não encontrados

            case None:
                return jsonify({ 'error': 'Gestores não encontrados' }), 404

            # 200 - Informações dos gestores consultadas

            case _ if isinstance(data_gestores, list):
                return jsonify(data_gestores), 200

            # 500 - Erro ao consultar gestores

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
            
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        if conn != None:
            conn.close()

@api_usuarios.route('/update', methods=['PUT'])
@api_usuarios.route('/update/<id_usuario>', methods=['PUT'])
def update_usuario(id_usuario: str = None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

    conn = None

    try:
        
        conn = Connection('local')
        
        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': 'Token de sessão inválido ou expirado' }), 401

        usuario_admin = Usuarios(conn.connection_db).get(data_token['id_usuario'])
        if not usuario_admin:
             return jsonify({ 'error': 'Usuário do token não encontrado' }), 404

        id_usuario_alvo = None
        if id_usuario:

            if not id_usuario.isdigit():
                 return jsonify({ 'error': '"id_usuario" da URL deve ser um Int válido' }), 400
            
            id_usuario_alvo = int(id_usuario)

        else:

            id_usuario_alvo = data_token['id_usuario']

        is_self_update = (id_usuario_alvo == data_token['id_usuario'])
        is_admin = (usuario_admin['tipo'] in ['gestor', 'root'])

        if not is_self_update and not is_admin:
            return jsonify({ 'error': 'Você não tem permissão para atualizar este usuário' }), 403

        data = request.get_json()
        if not data:
            return jsonify({ 'error': 'Payload da requisição está vazio' }), 400
        
        usuario_alvo_atual = Usuarios(conn.connection_db).get(id_usuario_alvo)
        if not usuario_alvo_atual:
             return jsonify({ 'error': 'Usuário alvo não encontrado para atualização' }), 404

        nome = data.get('nome', usuario_alvo_atual['nome'])
        email = data.get('email', usuario_alvo_atual['email'])
        
        senha = data.get('senha') 
        
        if not nome or not email:
            return jsonify({ 'error': 'Campos "nome" e "email" não podem ficar vazios' }), 400
        
        if senha and len(senha) < 8:
            return jsonify({ 'error': 'A nova senha deve ter no minímo 8 caractéres' }), 400

        senha_para_db = senha if senha else None
        
        update_usuario = Usuarios(conn.connection_db).update(id_usuario_alvo, nome, email, senha_para_db)
        match update_usuario:

            case None:
                return jsonify({ 'error': 'Usuário alvo não encontrado' }), 404
            
            case True:
                return jsonify({ 'texto': 'Usuário atualizado com sucesso' }), 200
            
            case 'EMAIL_EXISTS':
                 return jsonify({ 'error': 'Este email já está em uso por outra conta' }), 409
            
            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro ao atualizar o usuário' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        if conn:
            conn.close()