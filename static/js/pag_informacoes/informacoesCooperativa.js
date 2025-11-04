import { getVendas } from "../api/getVendas.js";

const session_token = localStorage.getItem('session_token');

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
        
      `/api/cooperativas/get/${id }`, 
      
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

document.addEventListener('DOMContentLoaded', async function () {
    
    const usuario = await getUsuario();
    const cooperativa = await getCooperativa(usuario.id_usuario);
    visualizarDados(cooperativa);
    console.log(cooperativa);
});


const btnVisualizarVendas = document.querySelector('.btn-vendas');

btnVisualizarVendas.addEventListener('click', async () => {
  const usuario = await getUsuario();
  const cooperativa = await getCooperativa(usuario.id_usuario);
  const vendas = await getVendas(cooperativa.dados_cooperativa.id_cooperativa); // Assume que você tem essa função que retorna os dados de vendas
  console.log(vendas);
  
  // Montar HTML para exibir os dados no formato desejado
  const vendaDetails = vendas.map(venda => {
    return `
      <div class="venda-card" style="font-family: Arial, sans-serif;">
        <h3 style="color: #A0D978;">Venda: ${venda.nome}</h3>
        <p><strong>Data da Venda:</strong> ${new Date(venda.data_venda).toLocaleDateString()} ${new Date(venda.data_venda).toLocaleTimeString()}</p>
        <p><strong>Comprador:</strong> ${venda.nome_comprador}</p>
        <p><strong>Especificação:</strong> ${venda.nome_especifico}</p>
        <p><strong>Vendedor:</strong> ${venda.nome_vendedor}</p>
        <p><strong>Valor Total:</strong> R$ ${parseFloat(venda.valor_total).toFixed(2)}</p>
      </div>
    `;
  }).join('');
  
  // Usar SweetAlert2 para exibir os dados com as cores e formato adequado
  Swal.fire({
    title: 'Detalhes da Venda',
    html: vendaDetails,  // Exibindo os detalhes das vendas
    icon: 'info',
    confirmButtonText: 'Fechar',
    confirmButtonColor: '#6A8B63',  // Cor do botão confirm
    background: '#F6FBF2', // Cor de fundo
    customClass: {
      popup: 'swal-popup',
      title: 'swal-title',
      content: 'swal-content',
    },
    showCloseButton: true,
  });
});




const visualizarDados = (dados) => {
  const cooperativa = dados.dados_cooperativa;

  // Nome e CNPJ
  const nomeElem = document.querySelector('.cooperativa-nome');
  const cnpjElem = document.querySelector('.cooperativa-cnpj');
  nomeElem.textContent = `${cooperativa.razao_social}`;
  cnpjElem.innerHTML = `<span class="cooperativa-cnpj-bold">CNPJ:</span> ${cooperativa.cnpj}`;

  // Endereço + Localização
  const enderecoElem = document.querySelector('.endereco');
  const cidadeElem = document.querySelector('.cidade');

  enderecoElem.innerHTML = `
    <span class="material-icons">place</span>
    ${cooperativa.endereco}
  `;
  cidadeElem.innerHTML = `<strong>${cooperativa.cidade}, ${cooperativa.estado}</strong>`;

  // Telefones e contatos (substitui apenas os valores)
  const telefoneLinks = document.querySelectorAll('.btn-contato');
  if (telefoneLinks.length >= 2) {
    // Botão "Ligar"
    telefoneLinks[0].setAttribute('href', `tel:${cooperativa.telefone.replace(/\D/g, '')}`);
    telefoneLinks[0].querySelector('span:last-child').textContent = cooperativa.telefone;

    // Botão WhatsApp
    telefoneLinks[1].setAttribute('href', `https://wa.me/55${cooperativa.telefone.replace(/\D/g, '')}`);
    telefoneLinks[1].querySelector('span:last-child').textContent = cooperativa.telefone;
  }

  // Email (se quiser adicionar em outro botão/link)
  const contatoCard = document.querySelector('.contato-card');
  if (contatoCard && !contatoCard.querySelector('.email-info')) {
    const emailElem = document.createElement('p');
    emailElem.classList.add('email-info');
    emailElem.innerHTML = `<strong>Email:</strong> ${cooperativa.email}`;
    contatoCard.appendChild(emailElem);
  }
};