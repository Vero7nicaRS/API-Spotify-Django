import os
import time 
import requests
import json
from dotenv import load_dotenv 
# Se cargan variables del .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# -------------------------------------------------------------------------------------
#                                      OBJETIVOS
#                                     -----------
# 1º Solicitar un Token a Spotify para poder realizar búsquedas con dicho token.
# 2º Comprobar si se puede reutilizar el Token o no.
# 3º Usar Token para buscar canciones (tracks)
# 4º Usar Token para buscar cantantes (artist)
# -------------------------------------------------------------------------------------

_HAY_TOKEN_ACTUAL_ = {
     "access_token": None,
     "expires_at": 0,
}
# 1) Solicitar un Token a Spotify para poder realizar búsquedas con dicho token.
def get_token(force_refresh: bool = False):

     # Devuelve un token válido.
     # - Si hay un token existente, se reutiliza.
     # - Si el token está caducado, se solicita un nuevo token.
     #
     ahora = int(time.time()) # Devuelve el tiempo actual (segundos)
     if(not force_refresh and 
        _HAY_TOKEN_ACTUAL_["access_token"] is not None and 
        ahora < _HAY_TOKEN_ACTUAL_["expires_at"]):
          return _HAY_TOKEN_ACTUAL_["access_token"]

     url = "https://accounts.spotify.com/api/token"
     data = {"grant_type": "client_credentials"}
     auth = (CLIENT_ID, CLIENT_SECRET)
     try:
          response = requests.post(url=url,data=data,auth=auth, timeout=10)
          # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json() # Serializa el objeto a formato JSON
     #     print(f"Loaded data: {json_data}")

          access_token = json_data["access_token"]
          expires_in = int(json_data.get("expires_in", 3600))

          ahora = int(time.time()) # Devuelve el tiempo actual (segundos)
          # Se guarda el TOKEN en memoria.
          _HAY_TOKEN_ACTUAL_["access_token"] = access_token 
          _HAY_TOKEN_ACTUAL_["expires_at"] = ahora + expires_in - 30 
          return access_token
     
     except requests.exceptions.RequestException:
          print("No se ha podido conectar con Spotify")
          return None

#2) Usar Token para buscar canciones (tracks)
#  Se encarga de buscar canciones en Spotify por el nombre de la canción
def search_track_song(query):
     token = get_token()
     if not token:
          return None 
     url = "https://api.spotify.com/v1/search"
     params = {
          "q"       : query,
          "type"    : "track",
          "limit"   : 1 # Devuelve solo 1 resultados de la búsqueda
     }
     header = {
          "Authorization": f"Bearer {token}"
     }

     try:
          response = requests.get(url,params=params, headers=header, timeout=10)
          
          # Se renueva el token
          if response.status_code == 401:
               token = get_token(force_refresh=True)
               if not token :
                    return None
               header["Authorization"] = f"Bearer {token}"
               response = requests.get(url,params=params, headers=header, timeout=10)

     # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json()
     #    print(f"Loaded data: {json_data}")

     # Poner que la visualización sea más agradable a la vista: ese diccionario se convierta a JSON 
          data_pretty = json.dumps(json_data, indent=4) # Serializa el objeto a formato JSON
          print(f"Pretty Printed Data: {data_pretty}")
          return json_data
     except requests.exceptions.RequestException:
          print("No se ha podido conectar con Spotify")
          return None




#2) Usar Token para buscar canciones (tracks)
#  Se encarga de buscar canciones en Spotify por el nombre de la canción
def search_artist(query):
     token = get_token()
     if not token:
          return None 
     url = "https://api.spotify.com/v1/search"
     params = {
          "q"       : query,
          "type"    : "artist",
          "limit"   : 1 # Devuelve solo 1 resultados de la búsqueda
     }
     header = {
          "Authorization": f"Bearer {token}"
     }
     try:
          response = requests.get(url,params=params, headers=header, timeout=10)

          # Se renueva el token
          if response.status_code == 401:
               token = get_token(force_refresh=True)
               if not token :
                    return None
               header["Authorization"] = f"Bearer {token}"
               response = requests.get(url,params=params, headers=header, timeout=10)
               
     # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json()
     #    print(f"Loaded data: {json_data}")

     # Poner que la visualización sea más agradable a la vista: ese diccionario se convierta a JSON 
          data_pretty = json.dumps(json_data, indent=4) # Serializa el objeto a formato JSON
          print(f"Pretty Printed Data: {data_pretty}")
          return json_data
     except requests.exceptions.RequestException:
          print("No se ha podido conectar con Spotify")
          return None





if __name__ == "__main__":
    search_track_song("La bachata")
#    search_artist("Adele")