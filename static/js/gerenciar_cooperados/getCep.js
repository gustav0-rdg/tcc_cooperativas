export async function getCepInfos(cep) {
  const cleanCep = String(cep || '').replace(/\D/g, '');
  if (cleanCep.length !== 8) {
    throw new Error('CEP deve ter 8 dígitos.');
  }

  const url = `https://viacep.com.br/ws/${encodeURIComponent(cleanCep)}/json/`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Falha na requisição ao ViaCEP. Tente novamente.');
  }

  const data = await response.json();

  // ViaCEP retorna 200 com { erro: true } quando o CEP não existe
  if (data.erro) {
    throw new Error('CEP não encontrado. Verifique e tente novamente.');
  }

  return data;
}
