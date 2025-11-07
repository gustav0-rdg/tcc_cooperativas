import { getCepInfos } from "./getCep.js";

const btnVinculo = document.querySelector('.vincular__cooperado');

btnVinculo.addEventListener('click', () => {
  Swal.fire({
    title: 'Dados do Cooperado',
    html:
      '<input id="nome" class="swal2-input" placeholder="Nome">' +
      '<input id="email" class="swal2-input" placeholder="Email" type="email">' +
      '<input id="senha" class="swal2-input" placeholder="Senha" type="password">' +
      '<input id="cpf" class="swal2-input" placeholder="CPF">' +
      '<input id="telefone" class="swal2-input" placeholder="Telefone">' +
      '<input id="cep" class="swal2-input" placeholder="CEP">',
    focusConfirm: false,
    confirmButtonText: 'Enviar',
    preConfirm: () => ({
      nome: document.getElementById('nome').value,
      email: document.getElementById('email').value,
      senha: document.getElementById('senha').value,
      cpf: document.getElementById('cpf').value,
      telefone: document.getElementById('telefone').value,
      cep: document.getElementById('cep').value,
    })
  }).then(async ({ isConfirmed, value }) => {
    if (!isConfirmed) return;

    try {
      const cep_infos = await getCepInfos(value.cep);
      const endereco = `${cep_infos.logradouro}, ${cep_infos.bairro}`;
      const cidade = cep_infos.localidade;
      const estado = cep_infos.uf;
      await post_cooperado({...value, endereco, cidade, estado })
      Swal.fire('Sucesso!', 'Os dados foram enviados!', 'success');
    } catch (err) {
      Swal.fire('Ops!', err.message, 'error');
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