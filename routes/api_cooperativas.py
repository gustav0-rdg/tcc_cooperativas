from flask import Blueprint, request
from controllers.tokens_controller import Tokens

api_cooperativas = Blueprint(
    
    'api_cooperativas', 
    __name__, 

    url_prefix='/api/cooperativas'
    
)