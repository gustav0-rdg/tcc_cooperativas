const session_token = localStorage.getItem('session_token')


async function getUsuario (){
    const response = await fetch (
        
        `/api/usuarios/get`, 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );
    
    const data_request = await response?.json();
    
    if (!response.ok)
    {
        throw new Error (
    
            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'
    
        );
    }
    
    return data_request;
}

async function getCooperativa(id){
    const response = await fetch (
            
        `/api/cooperativas/get/${id}`, 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data_request = await response?.json();

    if (!response.ok)
    {
        throw new Error (

            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_request;
}

async function getCooperados(id_usuario){
    const response = await fetch(
        `/api/cooperados/get/${id_usuario}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data_request = await response?.json()

    if (!response.ok){
        throw new Error (

            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_request
}

async function searchCooperado(id_cooperativa, nome) {
    const response = await fetch(`
        /api/cooperados/get/${id_cooperativa}/${nome}
        `,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': session_token
                }
            }
        );
    const data_request = await response?.json()

    if (!response.ok){
        throw new Error (

            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_request
}
let coop;

document.addEventListener('DOMContentLoaded', async function(){
    const user = await getUsuario();
    coop = await getCooperativa(user.id_usuario);
    const cooperados = await getCooperados(coop.dados_cooperativa.id_cooperativa);
    exibirCooperados(cooperados);
})


function exibirCooperados(listaCooperados) {
    const container = document.querySelector("#cooperadoCards");
    container.innerHTML = ""; // limpa cards anteriores
  
    if (!listaCooperados || listaCooperados.length === 0) {
      container.innerHTML = `<p>Nenhum cooperado encontrado.</p>`;
      return;
    }
  
    listaCooperados.forEach(cooperado => {
      const card = document.createElement("div");
      card.classList.add("card", "cooperado-card-clickable");
  
      card.innerHTML = `
        <h5>${cooperado.nome}</h5>
        <p><strong>CPF:</strong> ${cooperado.cpf}</p>
        <p><strong>Telefone:</strong> ${cooperado.telefone}</p>
        <p><strong>Endereço:</strong> ${cooperado.endereco}</p>
        <p><strong>Cidade/UF:</strong> ${cooperado.cidade} - ${cooperado.estado}</p>
        <p><strong>Data de vínculo:</strong> ${new Date(cooperado.data_vinculo).toLocaleString("pt-BR")}</p>
        <button class="btn-danger">Remover</button>
      `;
  
      // Exemplo: ação de clique no card
      card.addEventListener("click", () => {
        console.log(`Card do cooperado ${cooperado.nome} clicado!`);
      });
  
      container.appendChild(card);
    });
  }


  const searchInput = document.querySelector('#searchInput');

searchInput.addEventListener('input', async function(e) {
    const termoBusca = e.target.value;

    if (termoBusca === '') {
        // Se o campo está vazio, busca todos os cooperados
        const cooperados = await getCooperados(coop.dados_cooperativa.id_cooperativa);
        exibirCooperados(cooperados);
    } else {
        // Se o campo tem texto, faz a pesquisa
        const cooperadosEncontrados = await searchCooperado(coop.dados_cooperativa.id_cooperativa, termoBusca);
        exibirCooperados(cooperadosEncontrados);
    }
});