import { getSubtipos } from "../../api/getSubTipos.js";
import { material } from "../registrar_venda.js";

import { vendaAtual } from "../registrar_venda.js";
import { exibirVendedores } from "./exibirVendedores.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const compradorSection = document.querySelector('.registros__comprador');

let valoresCadastro = {
    nome_padrao: undefined,
    sinonimo: undefined,
}


export async function exibirSubtipos() {
    compradorSection.innerHTML = '';
    const subtipos = await getSubtipos(vendaAtual.material.id_categoria)

    console.log(subtipos, material.id_material_catalogo, material, vendaAtual.material.id_categoria)

    etapaSection.innerHTML = `
        <div class="etapa__progresso">
            <h1>Venda de ${vendaAtual.material.categoria}</h1>
            <small>Qual o subtipo do produto</small>
            <div class="progress-container">
                <div class="progress-bar"></div>
            </div>
            <span class="progress-label">Passo 1 de 4</span>
        </div>
        `;

    opcoesSection.innerHTML = '';

    // --- Lógica do botão de registrar novo subtipo ---
    const novoSubtipo = document.createElement('button');
    novoSubtipo.className = "registros__opcoes-btn";
    novoSubtipo.classList.add("opcoes-btn__novo-comprador");
    novoSubtipo.textContent = "Outros materiais";
    console.log(novoSubtipo, 'olha')

    const materiaisCategoriaAtual = subtipos.filter(
        item => item.id_material_base === vendaAtual.material.id_categoria
    );
    console.log('')

    const botoesSwal = materiaisCategoriaAtual.map(mat => `<input type="radio" id="${mat.id_material_catalogo}" class="registros__opcoes-btn swal__btn-material-existente"value="${mat.id_material_catalogo}">
        <label for="${mat.id_material_catalogo}">${mat.nome_especifico}</label> `).join(' ');

    novoSubtipo.addEventListener('click', async () => {
        Swal.fire({
            title: 'Algum destes materiais é o mesmo no qual você quer registrar?',
            html: `
                <div style="display: flex; flex-direction: column; gap: 12px; align-items: flex-start; text-align: left;">
                  <input type="text" placeholder="Digite o nome usado na sua região" id="novoNomeMaterial"
                    style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 6px;">
                  
                  <div id="listaMateriais" style="display: flex; flex-direction: column; gap: 8px; max-height: 200px; overflow-y: auto; padding-right: 4px;">
                    ${botoesSwal.replaceAll(
                'class="registros__opcoes-btn swal__btn-material-existente"',
                'name="materialOpcao" class="swal__btn-material-existente"'
            )}
                  </div>
                  
                  <div style="margin-top: 10px; border-top: 1px solid #ccc; padding-top: 10px;">
                    <input type="radio" name="materialOpcao" id="criar" value="criar">
                    <label for="criar" style="margin-left: 6px;">Registrar novo material</label>
                  </div>
                </div>
              `,
            showCancelButton: true,
            showConfirmButton: true,
            confirmButtonText: 'Confirmar',
            cancelButtonText: 'Cancelar',
            color: "var(--verde-escuro-medio)",
            background: "var(--verde-claro-medio)",
            confirmButtonColor: "#1E8449",
            cancelButtonColor: "#7DCEA0",
            preConfirm: async () => {
                const valor = document.getElementById('novoNomeMaterial').value.trim();
                const selecionado = document.querySelector('input[name="materialOpcao"]:checked');

                if (!valor) {
                    Swal.showValidationMessage('Digite o nome do material usado na sua região!');
                    return false;
                }

                if (!selecionado) {
                    Swal.showValidationMessage('Selecione uma das opções!');
                    return false;
                }

                // Se for "criar", chama função para cadastrar novo material
                if (selecionado.value === 'criar') {
                    await cadastrarNovoMaterial(valor, vendaAtual.material.id_categoria);
                } else {
                    // Caso contrário, cadastrar como sinônimo
                    valoresCadastro.nome_padrao = selecionado.value;
                    valoresCadastro.sinonimo = valor;

                    await cadastrarSinonimo(valoresCadastro);
                }

                return true;
            }
        });
    });
    console.log(novoSubtipo);
    console.log(compradorSection);
    compradorSection.appendChild(novoSubtipo)


    materiaisCategoriaAtual.forEach(item => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${item.nome_padrao}`);
        div.innerHTML = `
                <h1>${item.nome_especifico}</h1>
                <small>${vendaAtual.material.categoria}</small>
            `;
        console.log(div)
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o material
        div.addEventListener('click', () => {
            vendaAtual.material.subtipo = item.nome_especifico; // Atualiza o material no objeto vendaAtual

            exibirVendedores();
            console.log(vendaAtual); // Apenas para visualização
        });
    });


}



async function cadastrarSinonimo(valoresCadastro) {
    try {
        const resposta = await fetch('/post/cadastrar-sinonimo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(valoresCadastro)
        });

        const data = await resposta.json();

        if (resposta.ok) {
            await Swal.fire('✅ Sucesso!', data.message, 'success');
        } else {
            await Swal.fire('❌ Erro!', data.message, 'error');
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
    }
    finally {
        exibirSubtipos()
    }
}

async function cadastrarNovoMaterial(nomeMaterial, id_material_base) {
    try {
        const resposta = await fetch('/post/cadastrar-subtipo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome_especifico: nomeMaterial, id_material_base: id_material_base })
        });

        const data = await resposta.json();

        if (resposta.ok) {
            await Swal.fire('🎉 Material cadastrado!', data.message, 'success');
        } else {
            await Swal.fire('❌ Erro!', data.message, 'error');
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
    }
    finally {
        exibirSubtipos()
    }
}
