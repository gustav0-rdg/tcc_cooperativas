export function validarCNPJ(cnpj) {
    const cnpjLimpo = cnpj.replace(/[^\d]/g, '');
  
    if (cnpjLimpo.length !== 14) {
      return false;
    }
  
    if (/^(\d)\1+$/.test(cnpjLimpo)) {
      return false;
    }
  
    let tamanho = cnpjLimpo.length - 2;
    let numeros = cnpjLimpo.substring(0, tamanho);
    let digitos = cnpjLimpo.substring(tamanho);
    let soma = 0;
    let pos = tamanho - 7;
  
    for (let i = tamanho; i >= 1; i--) {
      soma += parseInt(numeros.charAt(tamanho - i), 10) * pos--;
      if (pos < 2) {
        pos = 9;
      }
    }
  
    let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  
    if (resultado !== parseInt(digitos.charAt(0), 10)) {
      return false;
    }
  
    tamanho = tamanho + 1;
    numeros = cnpjLimpo.substring(0, tamanho);
    soma = 0;
    pos = tamanho - 7;
  
    for (let i = tamanho; i >= 1; i--) {
      soma += parseInt(numeros.charAt(tamanho - i), 10) * pos--;
      if (pos < 2) {
        pos = 9;
      }
    }
    
    resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  
    if (resultado !== parseInt(digitos.charAt(1), 10)) {
      return false;
    }
  
    return true;
  }