document.addEventListener("DOMContentLoaded", () => {

    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    const form = document.getElementById("form-login-admin");

    if (!form || !emailInput || !senhaInput) {
        console.error("Erro crítico: Elementos do formulário de login (form, email, senha) não encontrados no HTML!");
        return; 
    }

    let emailAlertShown = false;
    let senhaAlertShown = false;

    emailInput.addEventListener("blur", () => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (emailInput.value.length > 0 && !emailRegex.test(emailInput.value)) {
            if (!emailAlertShown) {
                Swal.fire({
                    icon: "warning", 
                    title: "Formato de Email Inválido",
                    text: "Por favor, verifique o email digitado.",
                    timer: 2500, 
                    showConfirmButton: false
                }).then(() => {
                });
                emailAlertShown = true;
            }
        } else {
            emailAlertShown = false; 
        }
    });

    senhaInput.addEventListener("blur", () => {
        if (senhaInput.value.length > 0 && senhaInput.value.length < 8) {
            if (!senhaAlertShown) {
                Swal.fire({
                    icon: "warning",
                    title: "Senha Curta",
                    text: "A senha deve ter no mínimo 8 caracteres.",
                    timer: 2500,
                    showConfirmButton: false
                }).then(() => {
                });
                senhaAlertShown = true;
            }
        } else {
            senhaAlertShown = false; 
        }
    });

    form.addEventListener("submit", async (event) => { 

        event.preventDefault(); 

        const email = emailInput.value;
        const senha = senhaInput.value;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            Swal.fire({
                icon: "error",
                title: "Email Inválido",
                text: "Por favor, insira um email válido antes de continuar.",
            });
            emailInput.focus();
            return;
        }

        if (senha.length < 8) {
            Swal.fire({
                icon: "error",
                title: "Senha Inválida",
                text: "A senha deve ter no mínimo 8 caracteres.",
            });
            senhaInput.focus();
            return; 
        }

        try {
            Swal.fire({
                title: 'Aguarde...',
                text: 'Verificando suas credenciais.',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            const response = await fetch('/api/usuarios/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    identificador: email, 
                    senha: senha
                })
            });

            const data = await response.json();

            Swal.close();

            if (!response.ok) {
                throw new Error(data.error || `Erro ${response.status} do servidor`);
            }
            
            localStorage.setItem('session_token', data.token);
            document.cookie = `session_token=${data.token}; path=/; max-age=2592000`; // 30 dias

            Swal.fire({
                title: 'Sucesso!',
                text: 'Login realizado. Redirecionando...',
                icon: 'success',
                timer: 1500, 
                showConfirmButton: false,
                allowOutsideClick: false 
            });

            setTimeout(() => {
                window.location.href = '/pagina-inicial/gestor';
            }, 1500); 

        } catch (error) {
            Swal.close(); 
            Swal.fire({
                title: 'Erro no Login!',
                text: error.message, 
                icon: 'error',
                confirmButtonColor: '#d33' 
            });
        }
    });
});