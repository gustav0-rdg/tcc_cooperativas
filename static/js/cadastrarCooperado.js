// Dev by Vito

// Obtendo os elementos
const cpfInput = document.getElementById('cpf');
const nomeInput = document.getElementById('nome');
const telefoneInput = document.getElementById('telefone');
const dataNascimento = document.getElementById('data_nascimento');
const form = document.getElementById('form');



// CPF
cpfInput.addEventListener('input', function(e) {

    // remove o que nao é numero
    let value = e.target.value.replace(/\D/g, '');
    
    // ele limita o input a apenas 12 caracteres
    value = value.slice(0, 11);
    
    // mascara
    if (value.length > 9)
    {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } 
    else if (value.length > 6) 
    {
        value = value.replace(/(\d{3})(\d{3})(\d{3})/, '$1.$2.$3');
    } 
    else if (value.length > 3) 
    {
        value = value.replace(/(\d{3})(\d{3})/, '$1.$2');
    }
    
    e.target.value = value;
});

// Telefone
telefoneInput.addEventListener('input', function(e) {

    // remove o que não é numero
    let value = e.target.value.replace(/\D/g, '');

    // Limita a 11 dígitos (DDD + 9 dígitos)
    value = value.slice(0, 11);

    if (value.length > 10) { 
    value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } 

    else if (value.length > 6) { 
        value = value.replace(/(\d{2})(\d{4})(\d{1,4})/, '($1) $2-$3');
    } 

    else if (value.length > 2) { 
        value = value.replace(/(\d{2})(\d+)/, '($1) $2');
    }

    else if (value.length > 0) {
        value = value.replace(/(\d+)/, '($1');
    }

    e.target.value = value;
});

// Validar CPF
function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    
    if (cpf.length !== 11) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validação do primeiro dígito verificador
    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let resto = 11 - (soma % 11);
    let digitoVerificador1 = resto >= 10 ? 0 : resto;
    
    if (digitoVerificador1 !== parseInt(cpf.charAt(9))) 
        return false;
    
    // Validação do segundo dígito verificador
    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(cpf.charAt(i)) * (11 - i);
    }
    resto = 11 - (soma % 11);
    let digitoVerificador2 = resto >= 10 ? 0 : resto;
    
    return digitoVerificador2 === parseInt(cpf.charAt(10));
}

// Validação formulario
form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const cpfValue = cpfInput.value;
    const cpfNumeros = cpfValue.replace(/\D/g, '');
    
    // Valida CPF incompleto
    if (cpfNumeros.length !== 11) {
        Swal.fire({
            icon: 'error',
            title: 'CPF Incompleto',
            text: 'Por favor, digite os 11 dígitos do CPF!',
            confirmButtonColor: '#d33'
        });
        return;
    }
    
    // Valida CPF inválido
    if (!validarCPF(cpfNumeros)) {
        Swal.fire({
            icon: 'error',
            title: 'CPF Inválido',
            text: 'O CPF digitado não é válido. Verifique os números!',
            confirmButtonColor: '#d33'
        });

        return;
    }
    
    // Se tudo funfar ele manda o forms
    Swal.fire({
        icon: 'success',
        title: 'Cadastro realizado!',
        text: `CPF ${cpfValue} cadastrado com sucesso!`,
        confirmButtonColor: '#28a745'
    }).then((result) => {

        if (result.isConfirmed) {
            // Enviar o formulario para o banco de dados ( NAO SEI SE VAI FUNCIONAR ESSE KRL mas é)
            form.submit();
        }
    });
});