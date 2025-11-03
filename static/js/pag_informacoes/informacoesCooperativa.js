import { getVendas } from "../api/getVendas.js";

// const session_token = localStorage.getItem('session_token');

// async function getUsuario (){
//     const response = await fetch (
        
//         '/api/usuarios', 
        
//         {
//             method: 'POST',
//             headers: { 
//                 'Content-Type': 'application/json',
//                 'Authorization': session_token
//             }
//         }
//     );
    
//     const data_request = await response?.json();
    
//     if (!response.ok)
//     {
//         throw new Error (
    
//             'error' in data_request
//             ?
//             data_request.error
//             :
//             'Erro Interno. Tente novamente mais tarde.'
    
//         );
//     }
    
//     return data_request;
// }

// document.addEventListener('DOMContentLoaded', async function () {
    
//     usuario = await getUsuario();

// });


const btnVisualizarVendas = document.querySelector('.btn-vendas');

btnVisualizarVendas.addEventListener('click', async () => {
  const vendas = await getVendas(); // Assume que você tem essa função que retorna os dados de vendas
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
