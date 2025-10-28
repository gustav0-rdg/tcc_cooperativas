const session_token = localStorage.getItem('session_token')

async function consultarCooperativas ()
{
    const response = await fetch (
        
        '/api/cooperativas/get-all', 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    console.log(response)

    const response_json = await response.json();

    console.log(response_json)

}

document.addEventListener('DOMContentLoaded', function () {

    consultarCooperativas();

}); 