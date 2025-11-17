// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarInformacoesCooperativa();
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

        // Preenche os elementos com os dados
        preencherInformacoes(data);

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
    document.getElementById('cooperativa-endereco').textContent = `${data.rua || ''}, ${data.bairro || ''}`.trim() || 'Não informado';
    document.getElementById('cooperativa-cidade').textContent = data.cidade_estado || 'Não informado';

    // Contato
    document.getElementById('cooperativa-telefone').textContent = data.telefone_fixo || 'Não informado';
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
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorDetail = document.getElementById('error-detail');

    loadingSpinner.classList.add('d-none');
    errorMessage.classList.remove('d-none');
    errorDetail.textContent = mensagem;
}
