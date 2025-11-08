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

async function getCooperados(id_usuarios){

}


document.addEventListener('DOMContentLoaded', async function(){
    const user = await getUsuario();
    console.log(user)
    const coop = await getCooperados(user.id_usuario);
    console.log(coop)
})