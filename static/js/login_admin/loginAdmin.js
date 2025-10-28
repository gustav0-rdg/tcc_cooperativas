document.addEventListener("DOMContentLoaded", () => {

    // Pega os campos do forms
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");

    // Variável para controlar se o alerta já foi exibido
    let emailAlertShown = false;

    // Validação simples para o campo de email
    emailInput.addEventListener("blur", () => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(emailInput.value)) {

            if (!emailAlertShown) {

                Swal.fire({

                    icon: "error",
                    title: "Email inválido",

                }).then(() => {

                    // Foca no campo para o usuario preencher
                    emailInput.focus();

                });

                emailAlertShown = true; 
            }
        } 
        else {

            emailAlertShown = false;

        }
    });

    // Máscara para a senha (mínimo de 8 caracteres)
    senhaInput.addEventListener("input", () => {

        if (senhaInput.value.length < 8) {
            Swal.fire({
                icon: "error",
                text: "A senha deve ter no mínimo 8 caracteres.",
            });
        }
        
    });

});