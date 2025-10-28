
// Validão do formulario
document.addEventListener("DOMContentLoaded", () => {

    // Pega os campos do formulário
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    const form = document.getElementById("form-login-admin");

    // Variáveis para controlar os alertas
    let emailAlertShown = false;
    let senhaAlertShown = false;

    // Validação simples para o campo de email
    emailInput.addEventListener("blur", () => {

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(emailInput.value)) {

            if (!emailAlertShown) {

                Swal.fire({

                    icon: "error",
                    
                    title: "Email ou senha inválido",

                }).then(() => {

                    // Retorna o foco ao campo de email
                    emailInput.focus(); 

                });

                emailAlertShown = true;

            }

        } else {

            emailAlertShown = false; 

        }

    });

    // Validação da senha (mínimo de 8 caracteres)
    senhaInput.addEventListener("blur", () => {

        if (senhaInput.value.length < 8) {

            if (!senhaAlertShown) {

                Swal.fire({

                    icon: "error",

                    text: "A senha deve ter no mínimo 8 caracteres.",

                }).then(() => {

                    senhaInput.focus(); 

                });

                senhaAlertShown = true; 

            }
        } else {

            senhaAlertShown = false; 

        }

    });

    // Validação no envio do formulário
    form.addEventListener("submit", (event) => {
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        // Verifica se o email é válido
        if (!emailRegex.test(emailInput.value)) {

            event.preventDefault();

            Swal.fire({

                icon: "error",

                title: "Erro",

                text: "Por favor, insira um email válido.",

            });

            emailInput.focus();

            return;
        }

        // Verifica se a senha tem pelo menos 8 caracteres
        if (senhaInput.value.length < 8) {

            event.preventDefault(); 

            Swal.fire({

                icon: "error",

                title: "Erro",

                text: "A senha deve ter no mínimo 8 caracteres.",

            });

            senhaInput.focus();

            return;

        }

    });
    
});