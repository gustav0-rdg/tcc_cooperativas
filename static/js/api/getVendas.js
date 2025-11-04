export async function getVendas(id_cooperativa) {
    try {
        const response = await fetch(`/get/vendas/${id_cooperativa}`);
        // Verifica se a resposta do servidor foi um sucesso (status 200-299)
        if (!response.ok) {
            console.error("Erro do servidor:", response.status, response.statusText);
            return []; // Retorna uma lista vazia para não quebrar a interface
        }

        const data = await response.json();
        return data;

    } catch (error) {
        // Captura erros de rede (ex: servidor offline) ou outros problemas
        console.error("Falha ao buscar feedbacks:", error);
        
        // Retorna uma lista vazia para que o resto não quebre
        return [];
    }
}
