import urllib.parse
import requests

class Endereco:

    @staticmethod
    def get_coordenadas(endereco:str):

        headers = {
            'User-Agent': 'ReCoopera/1.0 (sistema.recoopera@gmail.com)'
        }

        url_base = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': endereco,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1
        }

        try:

            response = requests.get(url_base, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data:

                resultado = data[0]
                lat = float(resultado.get('lat', 0))
                lon = float(resultado.get('lon', 0))
            
                return (lat, lon)
            
            else:

                # Endereço não encontrado
                return None

        except requests.exceptions.RequestException as e:

            print(f"Erro ao chamar a API da Nominatim: {e}")
            return None