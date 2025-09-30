from flask import redirect, Blueprint, request
from controllers.cooperativa_controller import Cooperativa

api_get = Blueprint(
    
    'api_get', 
    
    __name__,
    url_prefix='/post'
    
)

@api_get.routes('/autenticar/<codigo_validacao>')
def autenticar_cooperativa (codigo_validacao):

    if Cooperativa.autenticar(codigo_validacao):

        return 200
    
    else:

        return 500