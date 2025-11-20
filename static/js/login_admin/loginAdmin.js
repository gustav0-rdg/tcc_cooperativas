import { PaginaLogin } from '../utils/paginaLoginGenerico.js    ';

document.addEventListener("DOMContentLoaded", () => {

    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    const formLogin = document.getElementById("form-login");
    const loginAdmin = new PaginaLogin(formLogin);

    if (!formLogin || !emailInput || !senhaInput) 
    {
        console.error("Erro crítico: Elementos do formulário de login (form, email, senha) não encontrados no HTML!");
        return; 
    }

    formLogin.addEventListener("submit", async (event) => { 

        event.preventDefault(); 

        const email = emailInput.value;
        const senha = senhaInput.value;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) 
        {
            loginAdmin.mostrarErro('Por favor, insira um email válido antes de continuar.');
            emailInput.focus();
            return;
        }

        loginAdmin.fazerLogin(email, senha, 'e-mail');
    });
});