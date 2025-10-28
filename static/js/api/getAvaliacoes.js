export async function getFeedbackTags(cnpj) {
   try {
        const response = await fetch(`/get/feedback-tags/${cnpj}`);
        if (!response.ok) {
            console.error("Erro do servidor:", response.status, response.statusText);
            return []; 
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Falha ao buscar feedbacks:", error);
        return [];
    }     
}

export async function getComentarios(cnpj) {
   try {
        const response = await fetch(`/get/comentarios-livres/${cnpj}`);
        if (!response.ok) {
            console.error("Erro do servidor:", response.status, response.statusText);
            return []; 
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Falha ao buscar feedbacks:", error);
        return [];
    }     
}