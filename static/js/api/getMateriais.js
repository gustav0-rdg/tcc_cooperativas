/**
 * Busca a lista de materiais do catálogo na API.
 * A função é assíncrona e utiliza a API Fetch do navegador.
 * * @returns {Promise<Array>} Uma promessa que resolve para uma lista de objetos de materiais.
 * Retorna uma lista vazia em caso de erro.
 */
export async function getMateriais() {
    try {
        const token = localStorage.getItem('session_token');
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch("/get/materiais", { headers });

        if (!response.ok) {
            console.error("Erro do servidor:", response.status, response.statusText);
            return [];
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Falha ao buscar materiais:", error);
        return [];
    }
}