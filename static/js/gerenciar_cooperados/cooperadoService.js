// Dados do cooperado

const cooperadoService = {

    // Helper interno para pegar os dados
    _getCooperados: function () {
        return JSON.parse(localStorage.getItem('cooperados')) || [];
    },

    // Helper interno para salvar os dados
    _saveCooperados: function (cooperados) {
        localStorage.setItem('cooperados', JSON.stringify(cooperados));
    },

    // Pega todos os cooperados
    getAll: function () {
        return this._getCooperados();
    },

    // Pega um cooperado pelo CPF
    getByCpf: function (cpf) {
        const cooperados = this._getCooperados();
        return cooperados.find(c => c.cpf === cpf);
    },

    // Verifica se um CPF já existe
    cpfExists: function (cpf) {
        const cooperados = this._getCooperados();
        return cooperados.some(c => c.cpf === cpf);
    },

    // Salva um cooperado (novo ou existente)
    save: function (cooperado) {
        let cooperados = this._getCooperados();

        const existingIndex = cooperados.findIndex(c => c.cpf === cooperado.cpf);

        if (existingIndex > -1) {
            // Atualiza o existente
            cooperados[existingIndex] = { ...cooperados[existingIndex], ...cooperado };
        } else {
            // Adiciona novo
            cooperados.push(cooperado);
        }

        this._saveCooperados(cooperados);
    },

    // Deleta um cooperado pelo CPF
    delete: function (cpf) {
        let cooperados = this._getCooperados();
        cooperados = cooperados.filter(cooperado => cooperado.cpf !== cpf);
        this._saveCooperados(cooperados);
    }
};