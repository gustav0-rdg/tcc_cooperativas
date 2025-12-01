import { PaginaLogin } from './utils/paginaLoginGenerico.js';

function limparCNPJ (cnpj) 
{
    return cnpj.replace(/[^\d]/g, '');  // Remove não números
}

// Aguarda o conteúdo da página carregar
document.addEventListener('DOMContentLoaded', () => {
    
    var loginForm = document.getElementById('form-login');
    const cnpjInput = document.getElementById('cnpj');
    const senhaInput = document.getElementById('senha');
    const submitButton = loginForm.querySelector('button[type="submit"]');

    if (!loginForm) {
        console.error('Formulário de login não encontrado.');
        return;
    }

    const loginCooperativa = new PaginaLogin(loginForm);

    loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const cnpj = limparCNPJ(cnpjInput.value);
        const senha = senhaInput.value;

        await loginCooperativa.fazerLogin(cnpj, senha, 'CNPJ');
    });
});