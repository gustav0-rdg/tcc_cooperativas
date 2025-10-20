export const registrarNovoVendedor = async (dados) => {
    // Verifica se existem dados para enviar
    if (!dados) {
        console.error("Nenhum dado fornecido para registrar.");
        return false; // Retorna false se não houver dados
    }

    try {
        const response = await fetch('/post/dados-comprador', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // IMPORTANTE: Envie o objeto 'dados' completo, não apenas o taxId
            body: JSON.stringify(dados.taxId) 
        });

        // Verifica se a resposta do servidor foi um sucesso (status 2xx)
        if (!response.ok) {
            // Se não foi, lança um erro que será pego pelo catch
            throw new Error(`Erro do servidor: ${response.status}`);
        }

        const data = await response.json();
        console.log('Sucesso:', data);
        return true; // Retorna true em caso de sucesso

    } catch (error) {
        console.error('Erro ao registrar vendedor:', error);
        // Aqui você poderia adicionar o SweetAlert de erro
        Swal.fire({
            icon: 'error',
            title: 'Erro no Cadastro',
            text: 'Não foi possível registrar o novo vendedor. Tente novamente.',
        });
        return false; // Retorna false em caso de erro
    }
};