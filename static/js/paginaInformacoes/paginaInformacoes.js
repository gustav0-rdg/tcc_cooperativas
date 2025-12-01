import { getUsuarioInfo } from '../utils/loginGenerico.js';

// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarInformacoesCooperativa();
    configurarSPATabs();
});

/**
 * Carrega as informações da cooperativa, buscando-as da API se não estiverem no sessionStorage.
 */
async function carregarInformacoesCooperativa() {
    const token = localStorage.getItem('session_token');
    const loadingSpinner = document.getElementById('loading-spinner-info');
    const errorMessage = document.getElementById('error-message-info');
    const mainContent = document.getElementById('main-content-info');
    
    let user_data = JSON.parse(sessionStorage.getItem('usuario'));

    if (!token) {
        mostrarErro('Sessão inválida. Faça o login novamente.');
        return;
    }

    try {
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        mainContent.classList.add('d-none');

        // Se os dados do usuário não estiverem no sessionStorage, busca na API
        if (!user_data) {
            user_data = await getUsuarioInfo(token);
            sessionStorage.setItem('usuario', JSON.stringify(user_data)); // Armazena os dados frescos
        }
        
        // Preenche os elementos com os dados
        preencherInformacoes(user_data.dados_cooperativa);

        loadingSpinner.classList.add('d-none');
        mainContent.classList.remove('d-none');

    } catch (err) {
        console.error('Erro em carregarInformacoesCooperativa:', err);
        mostrarErro('Não foi possível carregar as informações da cooperativa.');
    }
}


/**
 * Preenche os elementos da página com os dados da cooperativa
 */
function preencherInformacoes(data) {
    // Sobre a Cooperativa
    document.getElementById('cooperativa-nome').textContent = data.nome_fantasia || 'Não informado';
    document.getElementById('cooperativa-cnpj').textContent = data.cnpj || 'Não informado';
    document.getElementById('cooperativa-endereco').textContent = data.endereco || 'Não informado';
    document.getElementById('cooperativa-cidade').textContent = data.cidade_estado || 'Não informado';

    // Contato
    document.getElementById('cooperativa-telefone').textContent = data.telefone_fixo || data.telefone  || 'Não informado';
    document.getElementById('cooperativa-email').textContent = data.email || 'Não informado';

    // WhatsApp
    const whatsappLink = document.getElementById('whatsapp-link');
    if (data.whatsapp) {
        whatsappLink.href = `https://wa.me/${data.whatsapp.replace(/\D/g, '')}`;
        whatsappLink.style.display = 'inline-flex';
    } else {
        whatsappLink.style.display = 'none';
    }

    // Website
    const siteLink = document.getElementById('site-link');
    if (data.site) {
        siteLink.href = data.site.startsWith('http') ? data.site : `https://${data.site}`;
        siteLink.style.display = 'inline-flex';
    } else {
        siteLink.style.display = 'none';
    }
}

/**
 * Mostra mensagem de erro
 */
function mostrarErro(mensagem) {
    const loadingSpinner = document.getElementById('loading-spinner-info');
    const errorMessage = document.getElementById('error-message-info');
    const errorDetail = document.getElementById('error-detail-info');

    if (loadingSpinner) loadingSpinner.classList.add('d-none');
    if (errorMessage) errorMessage.classList.remove('d-none');
    if (errorDetail) errorDetail.textContent = mensagem;
}

/**
 * Configura a navegação SPA entre as abas
 */
function configurarSPATabs() {
    const tabs = document.querySelectorAll('#spa-tabs button');
    const user_data = JSON.parse(sessionStorage.getItem('usuario'));

    
    tabs.forEach(tab => {
        const target = tab.getAttribute('data-bs-target');
        if (user_data.tipo === 'cooperado' && 
            target === '#cooperados') {


            tab.classList.add('disabled');
            tab.style.pointerEvents = 'none';
            tab.style.opacity = '0.5';
        }

        tab.addEventListener('shown.bs.tab', (event) => {
            const target = event.target.getAttribute('data-bs-target');
            if (user_data.tipo === 'cooperado') {
                // Impede o carregamento de cooperados e histórico se for 'cooperado'
                if (target === '#cooperados') {
                    event.preventDefault(); // Impede o evento
                    alert('Acesso restrito para cooperados.');
                    return;
                }
            }
            if (target === '#cooperados') {
                carregarCooperados();
            } else if (target === '#vendas') {
                carregarHistoricoVendas();
            }
        });
    });


    // Configurar botão de editar informações
    const editBtn = document.getElementById('edit-info-btn');
    if (user_data.tipo === 'cooperado') {
        if (editBtn) {
            editBtn.classList.add('d-none');
        }
    } else {
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                preencherModalEdicao();
            });
        }
    }

    // Configurar botão de salvar alterações
    const saveBtn = document.getElementById('save-changes-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', salvarAlteracoes);
    }
}

/**
 * Carrega os cooperados da cooperativa
 */
async function carregarCooperados() {
    const token = localStorage.getItem('session_token');
    const userData = JSON.parse(sessionStorage.getItem('usuario'));

    if (!token || !userData || !userData.dados_cooperativa) {
        Swal.fire('Erro', 'Sessão inválida ou dados da cooperativa não encontrados. Faça o login novamente.', 'error');
        return;
    }

    try {
        const idCooperativa = userData.dados_cooperativa.id_cooperativa;

        const cooperadosResponse = await fetch(`/api/cooperados/get/${idCooperativa}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            }
        });
        const cooperados = await cooperadosResponse.json();
        if (!cooperadosResponse.ok) throw new Error(cooperados.error);

        exibirCooperados(cooperados);

        // Configurar busca
        configurarBuscaCooperados(idCooperativa);

        // Configurar botão de vincular
        configurarVincularCooperado();

    } catch (err) {
        console.error('Erro ao carregar cooperados:', err);
        Swal.fire('Erro', 'Não foi possível carregar os cooperados.', 'error');
    }
}

/**
 * Exibe os cooperados na aba
 */
function exibirCooperados(listaCooperados) {
    const container = document.getElementById('cooperadoCards');
    container.innerHTML = '';

    if (!listaCooperados || listaCooperados.length === 0) {
        container.innerHTML = `<p>Nenhum cooperado encontrado.</p>`;
        return;
    }

    listaCooperados.forEach(cooperado => {
        const card = document.createElement('div');
        card.classList.add('card', 'cooperado-card-clickable', 'mb-3');
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${cooperado.nome}</h5>
                <p class="card-text"><strong>CPF:</strong> ${cooperado.cpf}</p>
                <p class="card-text"><strong>Data de vínculo:</strong> ${new Date(cooperado.data_vinculo).toLocaleString('pt-BR')}</p>
                <button class="btn btn-danger btn-sm remover-cooperado" data-id="${cooperado.id_cooperado}">Remover</button>
            </div>
        `;

        container.appendChild(card);
    });

    // Configurar eventos de remoção
    document.querySelectorAll('.remover-cooperado').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idCooperado = e.target.getAttribute('data-id');
            confirmarRemocaoCooperado(idCooperado);
        });
    });
}

/**
 * Configura a busca de cooperados
 */
function configurarBuscaCooperados(idCooperativa) {
    const searchInput = document.getElementById('searchInput');
    let debounceTimer;

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            const termo = searchInput.value.trim();
            const token = localStorage.getItem('session_token');

            try {
                let response;
                if (termo === '') {
                    response = await fetch(`/api/cooperados/get/${idCooperativa}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': token
                        }
                    });
                } else {
                    response = await fetch(`/api/cooperados/get/${idCooperativa}/${termo}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': token
                        }
                    });
                }

                const data = await response.json();
                if (!response.ok) throw new Error(data.error);

                exibirCooperados(data);
            } catch (err) {
                console.error('Erro na busca:', err);
            }
        }, 300);
    });
}

/**
 * Aplica máscara de CPF no input
 */
function aplicarMascaraCPF(input) {
    input.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            e.target.value = value;
        }
    });
}

/**
 * Configura o botão de vincular cooperado
 */
function configurarVincularCooperado() {
    const btnVinculo = document.querySelector('.vincular__cooperado');
    if (!btnVinculo) return;

    btnVinculo.addEventListener('click', () => {
        Swal.fire({
            title: '<span style="color: var(--verde-escuro)">Cadastrar Cooperado</span>',
            // O HTML agora usa a estrutura de Grid e as classes modern-input
            html: `
                <div class="swal-form-grid">
                    <div class="swal-form-group swal-full-width">
                        <label for="nome">Nome Completo</label>
                        <input id="nome" class="modern-input" placeholder="Insira o nome completo" required>
                    </div>

                    <div class="swal-form-group swal-full-width">
                        <label for="email">Email</label>
                        <input id="email" class="modern-input" placeholder="exemplo@email.com" type="email" required>
                    </div>
                    
                    <div class="swal-form-group swal-full-width">
                        <label for="cpf">CPF</label>
                        <input id="cpf" class="modern-input" placeholder="000.000.000-00" maxlength="14" required>
                    </div>

                    <div class="swal-form-group">
                        <label for="senha">Senha</label>
                        <input id="senha" class="modern-input" placeholder="Mínimo 8 caracteres" type="password" required>
                    </div>

                    <div class="swal-form-group">
                        <label for="confirmar-senha">Confirmar Senha</label>
                        <input id="confirmar-senha" class="modern-input" placeholder="Repita a senha" type="password" required>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Cadastrar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: 'var(--verde-principal)', // Botão usando a cor principal
            cancelButtonColor: 'var(--vermelho)',
            width: '600px', // Um pouco mais largo para acomodar as colunas
            padding: '2em',
            background: 'var(--branco)',
            
            didOpen: () => {
                // Aplicar máscara ao CPF
                const cpfInput = document.getElementById('cpf');
                if (typeof aplicarMascaraCPF === 'function') {
                     aplicarMascaraCPF(cpfInput);
                }
            },
            preConfirm: () => {
                const nome = document.getElementById('nome').value.trim();
                const cpf = document.getElementById('cpf').value.trim().replace(/\D/g, '');
                const email = document.getElementById('email').value.trim();
                const senha = document.getElementById('senha').value.trim();
                const confirmarSenha = document.getElementById('confirmar-senha').value.trim();

                if (!nome || !cpf || !senha || !confirmarSenha) {
                    Swal.showValidationMessage('Por favor, preencha todos os campos!');
                    return false;
                }

                if (cpf.length !== 11) {
                    Swal.showValidationMessage('CPF deve ter 11 dígitos!');
                    return false;
                }

                if (senha !== confirmarSenha) {
                    Swal.showValidationMessage('As senhas não coincidem!');
                    return false;
                }

                if (senha.length < 8) {
                    Swal.showValidationMessage('A senha deve ter no mínimo 8 caracteres!');
                    return false;
                }

                return { nome, cpf, senha, email };
            }
        }).then(async (result) => {
            if (!result.isConfirmed) return;

            Swal.fire({
                title: 'Enviando dados...',
                allowOutsideClick: false,
                didOpen: () => Swal.showLoading(),
                color: 'var(--verde-escuro)'
            });

            try {
                const token = localStorage.getItem('session_token');
                const response = await fetch('/api/cooperativas/vincular-cooperado', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token
                    },
                    body: JSON.stringify(result.value)
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error);

                Swal.fire({
                    title: 'Sucesso',
                    text: 'Cooperado cadastrado com sucesso!',
                    icon: 'success',
                    confirmButtonColor: 'var(--verde-principal)'
                });
                
                // Verifica se a função existe antes de chamar para evitar erros
                if (typeof carregarCooperados === 'function') {
                    carregarCooperados(); 
                }

            } catch (err) {
                Swal.fire({
                    title: 'Erro',
                    text: err.message || 'Erro ao cadastrar cooperado.',
                    icon: 'error',
                    confirmButtonColor: 'var(--vermelho)'
                });
            }
        });
    });
}

/**
 * Confirma remoção de cooperado
 */
function confirmarRemocaoCooperado(idCooperado) {
    Swal.fire({
        title: 'Confirmar Exclusão',
        text: 'Tem certeza que deseja remover este cooperado?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Remover',
        cancelButtonText: 'Cancelar'
    }).then(async (result) => {
        if (!result.isConfirmed) return;

        try {
            const token = localStorage.getItem('session_token');
            const response = await fetch(`/api/cooperados/delete/${idCooperado}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': token
                }
            });

            if (!response.ok) throw new Error('Erro ao remover cooperado');

            Swal.fire('Sucesso', 'Cooperado removido com sucesso!', 'success');
            carregarCooperados(); // Recarregar lista

        } catch (err) {
            Swal.fire('Erro', 'Não foi possível remover o cooperado.', 'error');
        }
    });
}

/**
 * Carrega o histórico de vendas da cooperativa
 */
async function carregarHistoricoVendas() {
    const token = localStorage.getItem('session_token');
    const loadingSpinner = document.getElementById('loading-spinner-vendas');
    const errorMessage = document.getElementById('error-message-vendas');
    const vendasContent = document.getElementById('vendas-content');

    if (!token) {
        mostrarErroVendas('Sessão inválida. Faça o login novamente.');
        return;
    }

    try {
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        vendasContent.classList.add('d-none');
        const userData = JSON.parse(sessionStorage.getItem('usuario'))
        const response = await fetch(`/get/vendas/${userData.dados_cooperativa.id_cooperativa}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            }
        });

        const vendas = await response.json();
        if (!response.ok) throw new Error(vendas.erro || 'Erro ao buscar vendas');

        exibirHistoricoVendas(vendas);

        loadingSpinner.classList.add('d-none');
        vendasContent.classList.remove('d-none');

    } catch (err) {
        console.error('Erro ao carregar histórico de vendas:', err);
        mostrarErroVendas('Não foi possível carregar o histórico de vendas.');
    }
}

/**
 * Exibe o histórico de vendas na tabela
 */
function exibirHistoricoVendas(vendas) {
    const tbody = document.getElementById('vendas-tbody');
    tbody.innerHTML = '';

    if (!vendas || vendas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhuma venda encontrada.</td></tr>';
        return;
    }

    vendas.forEach(venda => {
        const row = document.createElement('tr');

        const dataVenda = new Date(venda.data_venda).toLocaleDateString('pt-BR');
        const agora = new Date();
        const vendaDate = new Date(venda.data_venda);
        const diffHoras = (agora - vendaDate) / (1000 * 60 * 60);
        const podeEditar = diffHoras <= 24;

        row.innerHTML = `
            <td>${dataVenda}</td>
            <td>${venda.nome || 'N/A'}</td>
            <td>${venda.nome_especifico || 'N/A'}</td>
            <td>${venda.nome_comprador || 'N/A'}</td>
            <td>R$ ${parseFloat(venda.valor_total).toFixed(2)}</td>
        `;

        tbody.appendChild(row);
    });

    // Configurar eventos de edição
    document.querySelectorAll('.editar-venda').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const venda = JSON.parse(e.target.getAttribute('data-venda'));
            editarVenda(venda);
        });
    });
}

/**
 * Edita uma venda
 */
async function editarVenda(venda) {
    // Implementar modal de edição
    Swal.fire({
        title: 'Editar Venda',
        html: `
            <p><strong>Data:</strong> ${new Date(venda.data_venda).toLocaleDateString('pt-BR')}</p>
            <p><strong>Material:</strong> ${venda.nome} - ${venda.nome_especifico}</p>
            <p><strong>Comprador:</strong> ${venda.nome_comprador}</p>
            <input id="novo-valor" class="swal2-input" placeholder="Novo valor total" type="number" step="0.01" value="${venda.valor_total}">
        `,
        showCancelButton: true,
        confirmButtonText: 'Salvar',
        cancelButtonText: 'Cancelar',
        preConfirm: () => {
            const novoValor = parseFloat(document.getElementById('novo-valor').value);
            if (!novoValor || novoValor <= 0) {
                Swal.showValidationMessage('Valor inválido!');
                return false;
            }
            return novoValor;
        }
    }).then(async (result) => {
        if (!result.isConfirmed) return;

        try {
            const token = localStorage.getItem('session_token');
            const response = await fetch('/post/editar-venda', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token
                },
                body: JSON.stringify({
                    id_venda: venda.id_venda,
                    novo_valor: result.value
                })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Erro ao editar venda');

            Swal.fire('Sucesso', 'Venda editada com sucesso!', 'success');
            carregarHistoricoVendas(); // Recarregar tabela

        } catch (err) {
            Swal.fire('Erro', err.message || 'Erro ao editar venda.', 'error');
        }
    });
}

/**
 * Mostra erro na aba de vendas
 */
function mostrarErroVendas(mensagem) {
    const loadingSpinner = document.getElementById('loading-spinner-vendas');
    const errorMessage = document.getElementById('error-message-vendas');

    loadingSpinner.classList.add('d-none');
    errorMessage.classList.remove('d-none');
    errorMessage.querySelector('p').textContent = mensagem;
}

/**
 * Preenche o modal de edição com os dados atuais
 */
function preencherModalEdicao() {
    // Obter dados atuais da página
    const nome = document.getElementById('cooperativa-nome').textContent;
    const cnpj = document.getElementById('cooperativa-cnpj').textContent;
    const endereco = document.getElementById('cooperativa-endereco').textContent;
    const cidadeEstado = document.getElementById('cooperativa-cidade').textContent;
    const telefone = document.getElementById('cooperativa-telefone').textContent;
    const email = document.getElementById('cooperativa-email').textContent;

    // Parse endereco
    const partesEndereco = endereco.split(', ');
    const rua = partesEndereco[0] || '';
    const bairro = partesEndereco[1] || '';

    // Parse cidade/estado
    const partesCidadeEstado = cidadeEstado.split(' - ');
    const cidade = partesCidadeEstado[0] || '';
    const estado = partesCidadeEstado[1] || '';

    // Preencher campos do modal
    document.getElementById('edit-nome').value = nome !== 'Não informado' ? nome : '';
    document.getElementById('edit-cnpj').value = cnpj !== 'Não informado' ? cnpj : '';
    document.getElementById('edit-rua').value = rua;
    document.getElementById('edit-bairro').value = bairro;
    document.getElementById('edit-cidade').value = cidade;
    document.getElementById('edit-estado').value = estado;
    document.getElementById('edit-telefone').value = telefone !== 'Não informado' ? telefone : '';
    document.getElementById('edit-email').value = email !== 'Não informado' ? email : '';

    // Para WhatsApp e site, precisamos buscar os dados originais
    buscarDadosOriginais();
}

/**
 * Busca os dados originais da cooperativa para preencher WhatsApp e site
 */
async function buscarDadosOriginais() {
    const token = localStorage.getItem('session_token');
    if (!token) return;

    try {
        const response = await fetch('/get/cooperativa-info', {
            headers: {
                'Authorization': token
            }
        });

        const data = await response.json();
        if (!response.ok) return;

        document.getElementById('edit-whatsapp').value = data.whatsapp || '';
        document.getElementById('edit-site').value = data.site || '';

    } catch (err) {
        console.error('Erro ao buscar dados originais:', err);
    }
}

/**
 * Salva as alterações do modal
 */
async function salvarAlteracoes() {
    const nome = document.getElementById('edit-nome').value.trim();
    const rua = document.getElementById('edit-rua').value.trim();
    const bairro = document.getElementById('edit-bairro').value.trim();
    const cidade = document.getElementById('edit-cidade').value.trim();
    const estado = document.getElementById('edit-estado').value.trim();
    const telefone = document.getElementById('edit-telefone').value.trim();
    const whatsapp = document.getElementById('edit-whatsapp').value.trim();
    const email = document.getElementById('edit-email').value.trim();
    const site = document.getElementById('edit-site').value.trim();

    if (!nome || !rua || !bairro || !cidade || !estado) {
        Swal.fire('Erro', 'Por favor, preencha todos os campos obrigatórios!', 'error');
        return;
    }

    const cidadeEstado = `${cidade}, ${estado}`;

    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch('/post/salvar-informacoes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({
                nome,
                rua,
                bairro,
                cidade_estado: cidadeEstado,
                telefone_fixo: telefone,
                whatsapp,
                email,
                site
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Erro ao salvar informações');

        Swal.fire('Sucesso', 'Informações salvas com sucesso!', 'success');

        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
        modal.hide();

        // Limpar cache do header para forçar recarregamento dos dados
        sessionStorage.removeItem('usuario');

        // Recarregar informações
        carregarInformacoesCooperativa();

    } catch (err) {
        Swal.fire('Erro', err.message || 'Erro ao salvar informações.', 'error');
    }
}
