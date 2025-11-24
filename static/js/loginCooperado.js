import { PaginaLogin } from './utils/paginaLoginGenerico.js';

function limparCPF(cpf) {
    return cpf.replace(/[^\d]/g, ''); // Remove tudo que não for número
}

function aplicarMascaraCPF(cpf) {
    return cpf
        .replace(/\D/g, '') // Remove tudo que não for número
        .replace(/(\d{3})(\d)/, '$1.$2') // Adiciona o primeiro ponto
        .replace(/(\d{3})\.(\d{3})(\d)/, '$1.$2.$3') // Adiciona o segundo ponto
        .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d{2})/, '$1.$2.$3-$4') // Adiciona o traço
        .slice(0, 14); // Limita o tamanho máximo
}

document.addEventListener('DOMContentLoaded', () => {
    var loginForm = document.getElementById('form-login');
    const cpfInput = document.getElementById('cpf');
    const senhaInput = document.getElementById('senha');
    const submitButton = loginForm.querySelector('button[type="submit"]');
    const btnEsqueceuSenha = document.getElementById('esqueceuSenha');

    if (!loginForm) {
        console.error('Formulário de login não encontrado.');
        return;
    }

    const paginaLoginCooperado = new PaginaLogin(loginForm);

    // Aplica a máscara ao CPF enquanto o usuário digita
    cpfInput.addEventListener('input', (e) => {
        e.target.value = aplicarMascaraCPF(e.target.value);
    });

    btnEsqueceuSenha.addEventListener('click', function () {
        Swal.fire({
            html: `
                <p class="mt-3">Solicite a troca da sua senha ao responsável por sua cooperativa, após isso tente novamente.</p>
            `,
            confirmButtonColor: 'var(--verde-escuro)',
            confirmButtonText: `
                <div class="d-flex align-items-center gap-2">
                    Entendido <span class="material-symbols-outlined">thumb_up</span>
                </div>
            `,
        });
    });

    // Adiciona o listener de evento "submit" ao formulário
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Pega os valores dos campos
        const cpf = limparCPF(cpfInput.value);
        const senha = senhaInput.value;

        paginaLoginCooperado.fazerLogin(cpf, senha, 'CPF');
    });
});
