import { PaginaLogin } from './utils/paginaLoginGenerico.js';

function limparCPF (cpf) 
{
    return cpf.replace(/[^\d]/g, '');  // Remove tudo que não for número
}

document.addEventListener('DOMContentLoaded', () => {
    
    var loginForm = document.getElementById('form-login');
    const cpfInput = document.getElementById('cpf');
    const senhaInput = document.getElementById('senha');
    const submitButton = loginForm.querySelector('button[type="submit"]');
    const btnEsqueceuSenha = document.getElementById('esqueceuSenha');

    if (!loginForm) 
    {
        console.error('Formulário de login não encontrado.');
        return;
    }

    const paginaLoginCooperado = new PaginaLogin(loginForm);

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

    loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        // Valores dos campos
        const cpf = limparCPF(cpfInput.value);
        const senha = senhaInput.value;

        paginaLoginCooperado.fazerLogin(cpf, senha, 'CPF');

    });
});
