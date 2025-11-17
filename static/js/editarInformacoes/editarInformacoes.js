// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarInformacoesCooperativa();
    configurarEventos();
});

/**
 * Carrega as informações da cooperativa via API
 */
async function carregarInformacoesCooperativa() {
    const token = localStorage.getItem('session_token');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const mainContent = document.getElementById('main-content');

    if (!token) {
        mostrarErro('Sessão inválida. Faça o login novamente.');
        return;
    }

    try {
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        mainContent.classList.add('d-none');

        const response = await fetch('/get/cooperativa-info', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao buscar dados da cooperativa.');
        }

        // Preenche os campos do formulário
        preencherFormulario(data);

        loadingSpinner.classList.add('d-none');
        mainContent.classList.remove('d-none');

    } catch (err) {
        console.error('Erro em carregarInformacoesCooperativa:', err);
        mostrarErro('Não foi possível carregar as informações da cooperativa.');
    }
}

/**
 * Preenche o formulário com os dados da cooperativa
 */
function preencherFormulario(data) {
    document.getElementById('nome').value = data.nome_fantasia || '';
    document.getElementById('cnpj').value = data.cnpj || '';
    document.getElementById('rua').value = data.rua || '';
    document.getElementById('bairro').value = data.bairro || '';
    document.getElementById('cidade_estado').value = data.cidade_estado || '';
    document.getElementById('telefone_fixo').value = data.telefone_fixo || '';
    document.getElementById('whatsapp').value = data.whatsapp || '';
    document.getElementById('email').value = data.email || '';
    document.getElementById('site').value = data.site || '';
}

/**
 * Configura os eventos dos botões
 */
function configurarEventos() {
    document.getElementById('btn-save').addEventListener('click', salvarInformacoes);
    document.getElementById('btn-cancel').addEventListener('click', () => {
        window.location.href = '/pagina-informacoes';
    });
}

/**
 * Salva as informações da cooperativa
 */
async function salvarInformacoes() {
    const token = localStorage.getItem('session_token');

    if (!token) {
        Swal.fire('Erro!', 'Sessão inválida. Faça o login novamente.', 'error');
        return;
    }

    // Coleta os dados do formulário
    const dados = {
        nome: document.getElementById('nome').value.trim(),
        cnpj: document.getElementById('cnpj').value.trim(),
        rua: document.getElementById('rua').value.trim(),
        bairro: document.getElementById('bairro').value.trim(),
        cidade_estado: document.getElementById('cidade_estado').value.trim(),
        telefone_fixo: document.getElementById('telefone_fixo').value.trim(),
        whatsapp: document.getElementById('whatsapp').value.trim(),
        email: document.getElementById('email').value.trim(),
        site: document.getElementById('site').value.trim()
    };

    // Validação básica
    if (!dados.nome || !dados.cnpj || !dados.rua || !dados.bairro || !dados.cidade_estado || !dados.whatsapp) {
        Swal.fire('Atenção!', 'Por favor, preencha todos os campos obrigatórios.', 'warning');
        return;
    }

    // Validação de CNPJ
    if (!validarCNPJ(dados.cnpj)) {
        Swal.fire('Erro!', 'CNPJ inválido. Verifique o formato.', 'error');
        return;
    }

    try {
        const response = await fetch('/salvar_informacoes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(dados)
        });

        const result = await response.json();

        if (response.ok) {
            Swal.fire('Sucesso!', 'Informações salvas com sucesso!', 'success')
                .then(() => {
                    window.location.href = '/pagina-informacoes';
                });
        } else {
            throw new Error(result.erro || 'Erro ao salvar informações.');
        }

    } catch (err) {
        console.error('Erro em salvarInformacoes:', err);
        Swal.fire('Erro!', 'Não foi possível salvar as informações. Tente novamente.', 'error');
    }
}

/**
 * Validação básica de CNPJ
 */
function validarCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');
    if (cnpj.length !== 14) return false;

    // Verificação básica (pode ser aprimorada)
    return true;
}

/**
 * Mostra mensagem de erro
 */
function mostrarErro(mensagem) {
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorDetail = document.getElementById('error-detail');

    loadingSpinner.classList.add('d-none');
    errorMessage.classList.remove('d-none');
    errorDetail.textContent = mensagem;
}
