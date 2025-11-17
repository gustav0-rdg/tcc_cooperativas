import urllib.parse
import requests
import math

class Endereco:

    @staticmethod
    def get_coordenadas(endereco:str):

        """
        Consulta a API da Nominatim para conseguir
        as coordenadas (latitude e longitude) de
        um endereço
        """

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
        
    @staticmethod        
    def haversine(lat1, lon1, lat2, lon2):

        """
        A fórmula de Haversine é um cálculo matemático usado para determinar a 
        distância entre dois pontos na superfície da Terra usando latitude e longitude.
        Ela leva em conta a curvatura da Terra, garantindo que a distância seja 
        muito mais precisa do que uma simples conta em linha reta no plano.
        """

        # Converte as coordenadas de graus para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Diferenças entre as coordenadas
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Raio da Terra (em quilômetros)
        R = 6371.0

        # Distância em quilômetros
        return R * c