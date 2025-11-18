/**
 * Busca a lista de materiais do catálogo na API.
 * A função é assíncrona e utiliza a API Fetch do navegador.
 * * @returns {Promise<Array>} Uma promessa que resolve para uma lista de objetos de materiais.
 * Retorna uma lista vazia em caso de erro.
 */
export async function getMateriais() {
    try {
        // Faz a requisição para a rota que criamos no backend
        const response = await fetch("/get/materiais");
        console.log(response);
        // Verifica se a resposta do servidor foi um sucesso (status 200-299)
        if (!response.ok) {
            console.error("Erro do servidor:", response.status, response.statusText);
            return []; // Retorna uma lista vazia para não quebrar a interface
        }

        // Converte a resposta em JSON
        const data = await response.json();
        console.log('alo', data)
        return data;

    } catch (error) {
        // Captura erros de rede (ex: servidor offline) ou outros problemas
        console.error("Falha ao buscar materiais:", error);
        
        // Retorna uma lista vazia para que a interface continue funcionando
        return [];
    }
}