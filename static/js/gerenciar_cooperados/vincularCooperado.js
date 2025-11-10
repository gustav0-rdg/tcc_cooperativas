import { getCepInfos } from "./getCep.js";

const btnVinculo = document.querySelector('.vincular__cooperado');

btnVinculo.addEventListener('click', () => {
  Swal.fire({
    title: 'Cadastrar Cooperado',
    html: `
      <div style="display: flex; flex-direction: column; gap: 10px; text-align: left;">
        <input id="nome" class="swal2-input" placeholder="Nome completo">
        <input id="email" class="swal2-input" placeholder="Email" type="email">
        <input id="senha" class="swal2-input" placeholder="Senha" type="password">
        <input id="cpf" class="swal2-input" placeholder="CPF">
        <input id="telefone" class="swal2-input" placeholder="Telefone">
        <input id="cep" class="swal2-input" placeholder="CEP">
      </div>
    `,
    icon: 'info',
    showCancelButton: true,
    confirmButtonText: 'Cadastrar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#2e7d32',
    cancelButtonColor: '#d33',
    background: '#f9f9f9',
    customClass: {
      title: 'swal-title',
      confirmButton: 'swal-confirm-button',
      cancelButton: 'swal-cancel-button'
    },
    focusConfirm: false,
    preConfirm: () => {
      const nome = document.getElementById('nome').value.trim();
      const email = document.getElementById('email').value.trim();
      const senha = document.getElementById('senha').value.trim();
      const cpf = document.getElementById('cpf').value.trim();
      const telefone = document.getElementById('telefone').value.trim();
      const cep = document.getElementById('cep').value.trim();

      if (!nome || !email || !senha || !cpf || !telefone || !cep) {
        Swal.showValidationMessage('⚠️ Por favor, preencha todos os campos!');
        return false;
      }

      return { nome, email, senha, cpf, telefone, cep };
    }
  }).then(async ({ isConfirmed, value }) => {
    if (!isConfirmed) return;

    Swal.fire({
      title: 'Enviando dados...',
      text: 'Aguarde um momento enquanto processamos as informações.',
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading()
    });

    try {
      const cep_infos = await getCepInfos(value.cep);
      const endereco = `${cep_infos.logradouro}, ${cep_infos.bairro}`;
      const cidade = cep_infos.localidade;
      const estado = cep_infos.uf;

      await post_cooperado({ ...value, endereco, cidade, estado });

      Swal.fire({
        icon: 'success',
        title: 'Cooperado cadastrado!',
        text: 'O cooperado foi vinculado com sucesso à cooperativa.',
        confirmButtonColor: '#2e7d32'
      });
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Erro ao cadastrar',
        text: err.message || 'Não foi possível concluir o cadastro.',
        confirmButtonColor: '#d33'
      });
    }
  });
});


const SESSION_TOKEN = localStorage.getItem('session_token')

async function post_cooperado(dados) {
    const response = await fetch(`/api/cooperativas/vincular-cooperado`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': SESSION_TOKEN
                },
                body: JSON.stringify(dados),
            }

        )
    const data_request = await response?.json();
    if (!response.ok){
        throw new Error(
            'error' in data_request
            ?
            data_request.error : 'Erro interno.'
        )
    }
    return data_request
}