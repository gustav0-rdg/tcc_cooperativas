export async function  postCooperado(cooperado) {
    try{
        const response = await fetch('/api/cooperativas/vincular-cooperado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `${localStorage.getItem('session_token')}`
            },
            body: JSON.stringify(cooperado)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch{
        throw new Error('Erro ao vincular cooperado.');
    }
}