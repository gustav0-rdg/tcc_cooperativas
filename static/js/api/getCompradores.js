export async function getCompradores() {
    const response = await fetch(
        `/get/compradores`,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    )
    const data = await response.json()
    return data
}

const session_token = localStorage.getItem('session_token')
// Função para buscar os compradores pelo NOME do material
export async function getCompradoresPorMaterial(nome_material, subtipo) {
    try {
        const response = await fetch(
            `/get/comprador/${nome_material}/${subtipo}`,
            {
                method: 'GET',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': session_token
                }
            }
        );            
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Falha na requisição fetch:", error);
        return [];
    }
}
