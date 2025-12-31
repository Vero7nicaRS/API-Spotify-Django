from django.http import Http404
from rest_framework import viewsets
from .models import Usuario, CancionFavorita, CantanteFavorito
from rest_framework.decorators import action
from .serializer import CancionesFavoritasSerializer, CantantesFavoritosSerializer, ListaUsuariosSerializer, UsuarioSerializer
from rest_framework import status 
from rest_framework.response import Response
from spotify.spotify_request import search_artist, search_track_song



# Create your views here.

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('nombre') #Obtener la informacion 
    serializer_class = UsuarioSerializer 
    lookup_field = 'pk'
#                                       UsuarioViewSet
# ----------------------------------------------------------------------------------------------
#                                   GET (obtener todos los usuarios)
# endpoint: /users/
# ---------------------------------------------------------------------------------------------- 
# Método GET --> Obtenemos los usuarios iniciales.
# Lo que se devolvía en Flask
# {
#  "users": [
#              {    "id": 6, 
#                   "nombre": "Paula"
#               },
#              {
#                   "id": 7, 
#                   "nombre": "Jasmine"
#               }
#           ]
# }
    def list(self, request, *args, **kwargs):
        usuarios = self.get_queryset()
        serializer = self.get_serializer(usuarios, many=True)

        # Devuelvo {"users": {id:... , nombre: ...}, {id:..., nombre:... }}
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)



# ----------------------------------------------------------------------------------------------
#                                               POST
#
# endpoint: /users/ ------->   http://127.0.0.1:8000/viewset/users/
# Método POST --> añadir usuarios
# ---------------------------------------------------------------------------------------------- 
    # POST 
    def create(self, request, *args, **kwargs):
        # Se obtiene los datos del JSON
        lista_usuarios = ListaUsuariosSerializer(data = request.data)
        if not lista_usuarios.is_valid():
            return Response(
                lista_usuarios.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        inserted_ids = []
        # Se insertan los usuarios.
        # Aquí no se comprueba que se recibe el campo "nombre" porque ya se hace en el SERIALIZER.
        for user in lista_usuarios.validated_data["users"]:
            obj_usuario = Usuario.objects.create(nombre=user["nombre"])
            inserted_ids.append(obj_usuario.id)

        return Response(
            {
                "message": "Usuarios añadidos correctamente",
                "ids": inserted_ids
            },
            status=status.HTTP_201_CREATED
        )
    

# ----------------------------------------------------------------------------------------------
#                                               PUT
#
# endpoint: /users/<tipo:nombre> ------->   http://127.0.0.1:8000/viewset/users/<tipo:nombre>
# Método PUT --> modificar usuarios
# se le indica <tipo: nombre>
# ----------------------------------------------------------------------------------------------
    # PUT 
    def update(self, request, pk=None):
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
       # Se obtiene los datos del JSON
       # get_object pasa por parámetro de manera automática "PK"
       # Antes, se comprueba que exista el usuario
        try:
            usuario = self.get_object()  # usa pk de la URL automáticamente
        except Http404:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )


        # Si existe, se actualiza el usuario
        # Para ello, se crea un serialicer nuevo para que si es a información es válida, 
        # la guarde en la base de datos.
        # partial = FALSE porque vamos a reemplazar todo
        serializer = UsuarioSerializer(usuario, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": f"Usuarios '{pk}' actualizado correctamente",
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------------------------------------------
#                                               DELETE
#
# endpoint: /users/<tipo:nombre> ------->   http://127.0.0.1:8000/viewset/users/?id=<id>
# Método DELETE --> eliminar usuarios
# ----------------------------------------------------------------------------------------------    
    # DELETE
    @action(detail=False, methods=["delete"], url_path="delete-by-query")
    def delete_by_query(self,request):
        user_id = request.query_params.get("id") # rquest.query_params.get() --> Sirve para los Query Params
        if not user_id:
            return Response(
                            {"message": "Falta el parámetro 'id'"}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )
        try:
            usuario = Usuario.objects.get(pk=int(user_id))
        except (Usuario.DoesNotExist, ValueError):
            return Response(
                             {"message": "Usuario no encontrado"},
                             status=status.HTTP_404_NOT_FOUND
                           )

        usuario.delete()
        return Response(
                        {"message": f"Usuario '{user_id}' eliminado correctamente"},
                        status=status.HTTP_200_OK) 
    

# ##############################################################################################
#                                      Cantantes favoritos
# ##############################################################################################
# ----------------------------------------------------------------------------------------------
#                                           GET
# endpoint: /users/<id>/cantantes_favoritos
# ---------------------------------------------------------------------------------------------- 
    # Método GET --> obtener cantantes favoritos de un usuario
    # /users/<int:id>/cantantes_favoritos'
    @action(detail=True, methods=["get"], url_path="cantantes_favoritos")
    def get_cantantes_favoritos(self, request, pk=None):

        # 1. Se comprueba que existe el usuario:
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )
        # 2. Se recorren todas las filas del usuario para ver su cantante favorito
        cantantes_favoritos = []
        for cantante_fav in CantanteFavorito.objects.filter(usuario=usuario):
            cantantes_favoritos.append(cantante_fav.nombre)
        
        # 3. El cantante existe pero no tiene ningún cantante favorito
        if not cantantes_favoritos:
            return Response(
                {
                    "message": f"El usuario '{pk}' ({usuario.nombre}) no tiene ningún cantante favorito",
                    "cantantes_favoritos": []
                },
                status=status.HTTP_200_OK
            )
        
        # 4. El cantante existe y tiene cantantes favoritos
        return Response(
            {
                "cantantes_favoritos": (
                    f"Los cantantes favoritos del usuario '{pk}' ({usuario.nombre}) "
                    f"son '{cantantes_favoritos}'"
                )
            },
        status=status.HTTP_200_OK
    )

# ----------------------------------------------------------------------------------------------
#                                   POST 
# endpoint: /users/<id>/cantantes_favoritos/anyadir
# ---------------------------------------------------------------------------------------------- 
    @action(detail=True, methods=["post"], url_path="cantantes_favoritos/anyadir")
    def post_cantantes_favoritos(self, request, pk=None):
        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        # 1. Se obtiene los datos del JSON.
        new_cantantes_favoritas = CantantesFavoritosSerializer(data=request.data)
        if not new_cantantes_favoritas.is_valid():
            return Response(new_cantantes_favoritas.errors, status = status.HTTP_400_BAD_REQUEST)

        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )
        # 3. Se obtiene los datos del JSON.
        new_cantantes_favoritas = new_cantantes_favoritas.validated_data["cantantes_favoritos"]

        existentes = set()
        # 4. Obtener cantantes favoritos ya existentes para ese usuario para no repetir cantantes en el futuro.
        for c in CantanteFavorito.objects.filter(usuario=usuario):
            existentes.add(c.nombre) # --> ["Robbie Williams", "Melendi"]
    
        cantantes_agregados = []
        cantantes_existentes = []

        # 5. Recorrer los nuevos cantantes y decidir si insertar o marcar como repetidos
        for cantante in new_cantantes_favoritas:
            if cantante in existentes: # ¿El cantante ya está en sus cantantes favoritos?
                cantantes_existentes.append(cantante)
            else:
                CantanteFavorito.objects.create(usuario=usuario, nombre=cantante)  # Añade el cantante a su lista de cantantes favoritos.
                cantantes_agregados.append(cantante)
                existentes.add(cantante) # Actualizamos los cantantes existentes con los que se han agregado.

        # 6. Obtener la lista final de cantantes favoritos
        lista_final = []
        for fila in CantanteFavorito.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        if cantantes_agregados:
            return Response(
                {
                    "message": f"Añadir cantante al usuario '{pk}'",
                    "cantantes_agregados": cantantes_agregados,
                    "cantantes_existentes": cantantes_existentes,
                    "cantantes_favoritos": lista_final
                },
                status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "message": f"Añadir cantante al usuario '{pk}'",
                    "cantantes_agregados": cantantes_agregados,
                    "cantantes_existentes": cantantes_existentes,
                    "cantantes_favoritos": lista_final
                },
                status.HTTP_200_OK
            )
        
# ----------------------------------------------------------------------------------------------
#                                   PUT 
# endpoint: /users/<id>/cantantes_favoritos/modificar
# ---------------------------------------------------------------------------------------------- 
    @action(detail=True, methods=["put"], url_path="cantantes_favoritos/modificar")
    def put_cantantes_favoritos(self, request, pk=None):

        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        
        # 1. Se obtiene los datos del JSON.
        mod_cantantes_favoritos = CantantesFavoritosSerializer(data=request.data)
        if not mod_cantantes_favoritos.is_valid():
            return Response(mod_cantantes_favoritos.errors, status = status.HTTP_400_BAD_REQUEST)
        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND)

        # 4. Se eliminan los cantantes favoritos del usuario para reemplazarlos por la nueva lista.
        CantanteFavorito.objects.filter(usuario=usuario).delete()

        # 5. Se añaden los nuevos cantantes favoritos.
        for cantante in mod_cantantes_favoritos.validated_data["cantantes_favoritos"]:
            CantanteFavorito.objects.create(usuario=usuario, nombre=cantante)

        # 6. Se obtiene la lista con los cantantes favoritos.
        lista_final = []
        for fila in CantanteFavorito.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        return Response(
            {
                "message": f"La lista de cantantes del usuario '{pk}' ha sido actualizada",
                "cantantes_favoritos": lista_final
            },
            status=status.HTTP_200_OK
        )

# ----------------------------------------------------------------------------------------------
#                                   DELETE 
# endpoint: /users/<id>/cantantes_favoritos/eliminar
# ----------------------------------------------------------------------------------------------  

    @action(detail=True, methods=["delete"], url_path="cantantes_favoritos/eliminar")
    def delete_cantante_favorito(self, request, pk=None):
        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        # 1. Se obtiene los desde la URL (?...=....)
        nombre_cantante = request.query_params.get("cantante")
        if not nombre_cantante:
            return Response(
                            {"message": "Falta el parámetro 'cantante' en la URL"}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )

        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )

        # 3. Se eliminan los cantantes favoritos del usuario para reemplazarlos por la nueva lista.
        cantantes_fav = CantanteFavorito.objects.filter(usuario=usuario, nombre=nombre_cantante)
        if not cantantes_fav.exists():
            return Response(
                {"message": f"El usuario '{pk}' no tiene al cantante '{nombre_cantante}' entre sus favoritos"},
                status=status.HTTP_404_NOT_FOUND
            )

        cantantes_fav.delete()

        lista_final = []
        for fila in CantanteFavorito.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        return Response(
            {
                "message": f"El cantante '{nombre_cantante}' del usuario '{pk}' ha sido eliminado",
                "cantantes_favoritos": lista_final
            },
            status=status.HTTP_200_OK
        )


# ##############################################################################################
#                                      Canciones favoritas
# ##############################################################################################
# ----------------------------------------------------------------------------------------------
#                                           GET
# endpoint: /users/<id>/canciones_favoritas
# ---------------------------------------------------------------------------------------------- 
    # Método GET --> obtener canciones favoritas de un usuario
    # /users/<int:id>/canciones_favoritas'
    @action(detail=True, methods=["get"], url_path="canciones_favoritas")
    def get_canciones_favoritas(self, request, pk=None):

        # 1. Se comprueba que existe el usuario:
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )
        # 2. Se recorren todas las filas del usuario para ver su canción favorita
        canciones_favoritas = []
        for cancion_fav in CancionFavorita.objects.filter(usuario=usuario):
            canciones_favoritas.append(cancion_fav.nombre)
        
        # 3. La canción existe pero no tiene ninguna canción favorita el usuario
        if not canciones_favoritas:
            return Response(
                {
                    "message": f"El usuario '{pk}' ({usuario.nombre}) no tiene ninguna canción favorita",
                    "canciones_favoritas": []
                },
                status=status.HTTP_200_OK
            )
        
        # 4. La canción existe existe y tiene canciones favoritas
        return Response(
            {
                "canciones_favoritas": (
                    f"Las canciones favoritas del usuario '{pk}' ({usuario.nombre}) "
                    f"son '{canciones_favoritas}'"
                )
            },
        status=status.HTTP_200_OK
    )

# ----------------------------------------------------------------------------------------------
#                                   POST 
# endpoint: /users/<id>/canciones_favoritas
# ---------------------------------------------------------------------------------------------- 
    @action(detail=True, methods=["post"], url_path="canciones_favoritas/anyadir")
    def post_canciones_favoritas(self, request, pk=None):
        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        # 1. Se obtiene los datos del JSON.
        new_canciones_favoritas = CancionesFavoritasSerializer(data=request.data)
        if not new_canciones_favoritas.is_valid():
            return Response(new_canciones_favoritas.errors, status = status.HTTP_400_BAD_REQUEST)

        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )
        # 3. Se obtiene los datos del JSON.
        new_canciones_favoritas = new_canciones_favoritas.validated_data["canciones_favoritas"]

        existentes = set()
        # 4. Obtener canciones favoritos ya existentes para ese usuario para no repetir canciones en el futuro.
        for fila in CancionFavorita.objects.filter(usuario=usuario):
            existentes.add(fila.nombre) # --> ["Leave the Door Open", "Tocado y Hundido"]
    
        canciones_agregadas = []
        canciones_existentes = []

        # 5. Recorrer las nuevas canciones y añadirla en caso de no estar repetida.
        for cancion in new_canciones_favoritas:
            if cancion in existentes: #  # ¿La canción ya está en sus canciones favoritas?
                canciones_existentes.append(cancion)
            else:
                CancionFavorita.objects.create(usuario=usuario, nombre=cancion)  # Añade la canción favorita a su lista de cantantes favoritos.
                canciones_agregadas.append(cancion)
                existentes.add(cancion) # Actualizamos las canciones existentes con los que se han agregado.

        # 6. Obtener la lista final de canciones favoritas
        lista_final = []
        for fila in CancionFavorita.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        if canciones_agregadas:
            return Response(
                {
                    "message": f"Añadir canción al usuario '{pk}'",
                    "canciones_agregadas": canciones_agregadas,
                    "canciones_existentes": canciones_existentes,
                    "canciones_favoritas": lista_final
                },
                status= status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "message": f"Añadir canción al usuario '{pk}'",
                    "canciones_agregadas": canciones_agregadas,
                    "canciones_existentes": canciones_existentes,
                    "canciones_favoritas": lista_final
                },
                status=status.HTTP_200_OK
            )
        

# ----------------------------------------------------------------------------------------------
#                                   PUT 
# endpoint: /users/<id>/canciones_favoritas
# ---------------------------------------------------------------------------------------------- 
    @action(detail=True, methods=["put"], url_path="canciones_favoritas/modificar")
    def put_canciones_favoritas(self, request, pk=None):

        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        
        # 1. Se obtiene los datos del JSON.
        mod_canciones_favoritas = CancionesFavoritasSerializer(data=request.data)
        if not mod_canciones_favoritas.is_valid():
            return Response(mod_canciones_favoritas.errors, status = status.HTTP_400_BAD_REQUEST)
        
        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND)

        # 4. Se eliminan las canciones favoritas del usuario para reemplazarlos por la nueva lista.
        CancionFavorita.objects.filter(usuario=usuario).delete()

        # 5. Se añaden las nuevas canciones favoritas.
        for cancion in mod_canciones_favoritas.validated_data["canciones_favoritas"]:
            CancionFavorita.objects.create(usuario=usuario, nombre=cancion)

        # 6. Se obtiene la lista con las canciones favoritas.
        lista_final = []
        for fila in CancionFavorita.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        return Response(
            {
                "message": f"La lista de canciones del usuario '{pk}' ha sido actualizada",
                "canciones_favoritas": lista_final
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["delete"], url_path="canciones_favoritas/eliminar")
    def delete_cancion_favorita(self, request, pk=None):
        # Comprobar si el usuario es válido (HEADER)
        authorization = request.headers.get('Authorization')
        if authorization != "1234":
            return Response(
                            {"message": "Sin autorización"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                            )
        # 1. Se obtiene los desde la URL (?...=....)
        nombre_cancion = request.query_params.get("cancion")
        if not nombre_cancion:
            return Response(
                            {"message": "Falta el parámetro 'cancion' en la URL"}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )

        # 2. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )

        # 3. Se eliminan las canciones favoritas del usuario para reemplazarlos por la nueva lista.
        canciones_fav = CancionFavorita.objects.filter(usuario=usuario, nombre=nombre_cancion)
        if not canciones_fav.exists():
            return Response(
                {"message": f"El usuario '{pk}' no tiene la canción '{nombre_cancion}' entre sus favoritos"},
                status=status.HTTP_404_NOT_FOUND
            )

        canciones_fav.delete()

        lista_final = []
        for fila in CancionFavorita.objects.filter(usuario=usuario):
            lista_final.append(fila.nombre)

        return Response(
            {
                "message": f"La canción '{nombre_cancion}' del usuario '{pk}' ha sido eliminada",
                "canciones_favoritas": lista_final
            },
            status=status.HTTP_200_OK
        )



# ##############################################################################################
#                                      Artistas Spotify
# ##############################################################################################
# ----------------------------------------- ENDPOINT USUARIO + CANTANTES FAVORITOS + SPOTIFY -----------------------------------------
# Obtiene información de los artistas de un usuario dado sus cantantes favoritos
# ------------------------------------------------------------------------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="artistas_spotify")
    def get_info_artistas_spotify(self, request, pk=None):

        # 1. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )

        # 3. Obtener cantantes favoritos ya existentes para el usuario y recorrerlas una a una para buscar
        cantantes_usuario = []
        for fila in CantanteFavorito.objects.filter(usuario=usuario):
            cantantes_usuario.append(fila.nombre)

        cantantes_usuario = list(set(cantantes_usuario))

        resultado_spotify = []
        cantantes_favoritos = []

        # 4. Recorremos cada cantante favorito del usuario para encontrar información acerca de ellos.
        for cantante in cantantes_usuario:

            # Devuelve el diccionario de artistas y obten el array de "items"
            json_artistas = search_artist(cantante)

          
            if not json_artistas: # Si es None no continua
                continue
            
              # 5. Obtenemos información del artista
            contenido_artista = json_artistas.get("artists", {}).get("items", [])
            if contenido_artista:
                # Devuelve el primer elemento de Spotify
                artista = contenido_artista[0]
                info_artista = {
                    "gusto_original": cantante,
                    "nombre": artista.get("name"),
                    "id": artista.get("id"),
                    "popularidad": artista.get("popularity"),
                    "seguidores": artista.get("followers", {}).get("total"),
                    "generos": artista.get("genres", []),
                    "spotify_url": artista.get("external_urls", {}).get("spotify"),
                }
                resultado_spotify.append(info_artista)
                cantantes_favoritos.append(info_artista["nombre"])


        if not resultado_spotify:
            mensaje = f"No se han encontrado artistas en Spotify para los gustos del usuario '{pk}'"
        else:
            mensaje = f"Usuario '{pk}' ha encontrado información en Spotify acerca de cantantes favoritos."

        return Response(
            {
                "message": mensaje,
                "cantantes_favoritos": cantantes_favoritos, # Muestra los cantantes favoritos del usuario.
                "resultado_spotify": resultado_spotify, # Devuelve la información obtenida de Spotify
            },
            status=status.HTTP_200_OK
        )

# ------------------------------------------------------------------------------------------------------------------------------------
# Obtiene información de las canciones de un usuario dado sus canciones favoritas
# ------------------------------------------------------------------------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="canciones_spotify")
    def get_info_canciones_spotify(self, request, pk=None):

        # 1. Comprobar que el usuario existe
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                            {"message": f"Usuario '{pk}' no encontrado"}, 
                            status=status.HTTP_404_NOT_FOUND
                            )

        # 2. Obtener canciones favoritos ya existentes para el usuario y recorrerlas una a una para buscar
        # información.
        canciones_usuario = []
        for fila in CancionFavorita.objects.filter(usuario=usuario):
            canciones_usuario.append(fila.nombre)

        canciones_usuario = list(set(canciones_usuario))

        resultado_spotify = []
        canciones_favoritas = []

        # 3. Recorremos cada canción favorita del usuario para encontrar información acerca de la ella.
        for cancion in canciones_usuario:
            # Devuelve el diccionario de canciones y obten el array de "items"
            json_canciones = search_track_song(cancion)

            # 4. Obtenemos información de la canción
            contenido_cancion = json_canciones.get("tracks", {}).get("items", [])

            if not contenido_cancion: # Si es None no continua
                continue
            if contenido_cancion:
                canc = contenido_cancion[0]

                cantantes_nombres = []
                for art in canc.get("artists", []):
                    cantantes_nombres.append(art.get("name"))

                info_cancion = {
                    "nombre": cancion,
                    "nombre_album": canc.get("album", {}).get("name"),
                    "tipo_album": canc.get("album", {}).get("album_type"),
                    "cantantes": cantantes_nombres,
                    "id": canc.get("id"),
                    "popularidad": canc.get("popularity"),
                    "numero_cancion": canc.get("track_number"),
                    "duracion": canc.get("duration_ms"),
                    "fecha_lanzamiento": canc.get("album", {}).get("release_date"),
                    "spotify_url": canc.get("external_urls", {}).get("spotify"),
                }

                resultado_spotify.append(info_cancion)
                canciones_favoritas.append(info_cancion["nombre"])

        
        if not resultado_spotify:
            mensaje = f"No se han encontrado canciones en Spotify para los gustos del usuario '{pk}'"
        else:
            mensaje = f"Usuario '{pk}' ha encontrado información en Spotify acerca de canciones favoritas."

        return Response(
            {
                "message": mensaje,
                "canciones_favoritas": canciones_favoritas,
                "resultado_spotify": resultado_spotify,
            },
            status=status.HTTP_200_OK
        )
