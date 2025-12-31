import ast
import re
from django.test import TestCase

# Create your tests here.
import pytest
from rest_framework.test import APIClient
from viewset_users.models import CancionFavorita, CantanteFavorito, Usuario

pytestmark = pytest.mark.django_db

############################################################################################
############################################################################################

#                                       USUARIOS

############################################################################################
############################################################################################

#-------------------------------------------------------------------------------------------
#                           TEST_GET_USUARIOS_DEVUELVE_USUARIOS_Y_DEVUELVE_200:
# Se comprueba que devuelva la información de los usuarios del sistema.
#-------------------------------------------------------------------------------------------
def test_get_usuarios_devuelve_usuarios_y_devuelve_200():
    # Se crean usuarios
    Usuario.objects.create(nombre="Paula")
    Usuario.objects.create(nombre="Jasmine")
    client = APIClient()

    # Se hace una petición "GET" para acceder a su información
    respuesta = client.get("/viewset/users/")

    # Se verifica... 
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert "users" in data # Contiene la clave "users" 
    assert isinstance(data["users"], list) # Es una lista
    assert len(data["users"]) == 2 # El tamaño de la lista sea "2"

#-------------------------------------------------------------------------------------------
#                           TEST_POST_USUARIOS_CREA_USUARIOS_Y_DEVUELVE_IDS:
# Se comprueba que se añadan usuarios y devuelva correctamenete la información.
#-------------------------------------------------------------------------------------------
def test_post_usuarios_crea_usuarios_y_devuelve_ids():
    # Se definen los usuarios en el body
    client = APIClient()
    payload = {
        "users": [
            {"nombre": "Pepe"},
            {"nombre": "Ana"},
        ]
    }

    # Se hace una petición "POST" para añadir los usuarios
    respuesta = client.post("/viewset/users/", payload, format="json")

    # Se verifica...
    assert respuesta.status_code == 201
    data = respuesta.json()
    assert data["message"] == "Usuarios añadidos correctamente" # Mensaje de confirmación
    assert "ids" in data  # Contiene la clave "ids"  
    assert len(data["ids"]) == 2 # Hay dos campos "ids"
    assert Usuario.objects.count() == 2 # Hay 2 usuarios

#-------------------------------------------------------------------------------------------
#                           TEST_POST_USUARIOS_SIN_USUARIOSS_Y_DEVUELVE_400:
# Se comprueba que no se añada un usuario sin pasar nada por el body.
#-------------------------------------------------------------------------------------------
def test_post_usuarios_sin_usuarios_y_devuelve_400():
    # No se manda ningún usuario por el Body
    client = APIClient()
    payload = {}  # no mandamos "users"

    # Se hace una petición "POST" con ningún usuario
    respuesta = client.post("/viewset/users/", payload, format="json")

    # Se verifica
    assert respuesta.status_code == 400

#-------------------------------------------------------------------------------------------
# TEST_PUT_USUARIO_CON_AUTORIZACION_ACTUALIZA_Y_DEVUELVE_200
# Se comprueba que el endpoint PUT /users/<id>/ actualiza el usuario si tiene
# autenticación ("1234").
#-------------------------------------------------------------------------------------------
def test_put_usuario_con_autorizacion_actualiza_y_devuelve_200():
    # Se crea un usuario
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    payload = {"nombre": "Juanita"}

    # Se realiza una petición "PUT" para modificar los datos de un usuario, incluyendo la autenticación.
    respuesta = client.put(
        f"/viewset/users/{usuario.id}/",
        payload,
        format="json",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert data["message"] == f"Usuarios '{usuario.id}' actualizado correctamente" # Mensaje de confirmación

    usuario.refresh_from_db()
    assert usuario.nombre == "Juanita"


#-------------------------------------------------------------------------------------------
# TEST_PUT_USUARIO_SIN_AUTORIZACION_DEVUELVE_401
# Se comprueba que no se puede modificar a un usuario si no se tiene autenticación ("1234")
#-------------------------------------------------------------------------------------------
def test_put_usuario_sin_autorizacion_devuelve_401():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    payload = {"nombre": "Juanita"}

    # Se realiza petición "PUT" sin tener autorización.
    respuesta = client.put(
        f"/viewset/users/{usuario.id}/",
        payload,
        format="json"
    )

    assert respuesta.status_code == 401
    data = respuesta.json()
    assert data["message"] == "Sin autorización" # Mensaje de error.

    # El usuario no ha sido modificado.
    usuario.refresh_from_db()
    assert usuario.nombre == "Lola"


#-------------------------------------------------------------------------------------------
#               TEST_DELETE_USUARIO_POR_QUERY_BORRA_Y_DEVUELVE_200
# Se comprueba que se elimina un usuario correctamente.
#-------------------------------------------------------------------------------------------
def test_delete_usuario_por_query_borra_y_devuelve_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    # Se realiza petición "DELETE" pasando "id" como "query param".
    respuesta = client.delete(f"/viewset/users/delete-by-query/?id={usuario.id}")

    # Se verifica...
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert data["message"] == f"Usuario '{usuario.id}' eliminado correctamente" # Mensaje de confirmación-

    assert Usuario.objects.filter(id=usuario.id).exists() is False # El usuario no existe.


#-------------------------------------------------------------------------------------------
#                       TEST_DELETE_USUARIO_SIN_ID_DEVUELVE_400
# Se comprueba que no se elimina a un usuario si no se le pasa un "id".
#-------------------------------------------------------------------------------------------
def test_delete_usuario_sin_id_devuelve_400():
    client = APIClient()

    # Se realiza una petición "DELETE" sin pasar "id" como "query param"
    respuesta = client.delete("/viewset/users/delete-by-query/")

    # Se verifica...
    assert respuesta.status_code == 400
    data = respuesta.json()
    assert data["message"] == "Falta el parámetro 'id'" # Mensaje de error.




############################################################################################
############################################################################################

#                                   CANTANTES FAVORITOS

############################################################################################
############################################################################################

#-------------------------------------------------------------------------------------------
#               TEST_GET_CANTANTES_FAVORITOS_DEVUELVE_LISTA_Y_200
# Se comprueba que se devuelve la lista de cantantes favoritos de un usuario.
#-------------------------------------------------------------------------------------------
def test_get_cantantes_favoritos_devuelve_lista_y_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")

    # Se añaden dos cantantes favoritos para el usuario.
    CantanteFavorito.objects.create(usuario=usuario, nombre="Adele")
    CantanteFavorito.objects.create(usuario=usuario, nombre="Melendi")

    client = APIClient()

    # Se realiza una petición "GET" para obtener el listado de cantantes favoritos del usuario.
    respuesta = client.get(f"/viewset/users/{usuario.id}/cantantes_favoritos/")

    # Se verifica...
    assert respuesta.status_code == 200, respuesta.content
    data = respuesta.json()
    assert "cantantes_favoritos" in data # Se comprueba que está "cantantes_favoritos".
    assert isinstance(data["cantantes_favoritos"], str) # Se comprueba que la lista tenga como clave.
    cant_fav = data["cantantes_favoritos"]

    # Como devuelve una cadena: "Los cantantes favoritos del usuario 'x' (nombre) son '['...', '...'] "
    # Hay que extraer los cantantes para comprobar si son los que realmente deberían ser.
    # Por tanto, primero se busca el primer bloque "[...]"" dentro de la cadena de texto
    m = re.search(r"\[.*\]", cant_fav)
    assert m is not None, f"No se encontró lista en el texto: {cant_fav}"

    lista = ast.literal_eval(m.group(0))  # Convierte "['Adele', 'Melendi']" -> ['Adele','Melendi']
    assert isinstance(lista, list)
    assert len(lista) == 2
    assert "Adele" in lista # Comprueba que "Adele" esté en la lista de cantantes favoritos.
    assert "Melendi" in lista  # Comprueba que "Melendi" esté en la lista de cantantes favoritos.
#-------------------------------------------------------------------------------------------
#           TEST_GET_CANTANTES_FAVORITOS_DEVUELVE_LISTA_VACIA
# Se comprueba que un usuario sin cantantes favoritos devuelve una lista vacía.
#-------------------------------------------------------------------------------------------
def test_get_cantantes_favoritos_sin_datos_devuelve_lista_vacia():

    # Se crea un usuario
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    # Se realiza petición "GET" para obtener el listado de cantantes favoritos del usuario.
    respuesta = client.get(f"/viewset/users/{usuario.id}/cantantes_favoritos/")

    # Se verifica...
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert "cantantes_favoritos" in data # Se comprueba que está "cantantes_favoritos".
    assert data["cantantes_favoritos"] == [] # No hay ningún cantante favorito.
 

#-------------------------------------------------------------------------------------------
#          TEST_POST_CANTANTES_FAVORITOS_ANYADIR_CON_AUTORIZACION_Y_DEVUELVE_201
# Se comprueba que se añaden cantantes favoritos a un usuario.
#-------------------------------------------------------------------------------------------
def test_post_cantantes_favoritos_anyadir_con_autorizacion_y_devuelve_201():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    # Body
    payload = {"cantantes_favoritos": ["Adele", "Melendi"]}

    # Se realiza petición "POST" añadiendo la información para el usuario, incluyendo la autenticación.
    respuesta = client.post(
        f"/viewset/users/{usuario.id}/cantantes_favoritos/anyadir/",
        payload,
        format="json",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 201, respuesta.content
    assert CantanteFavorito.objects.filter(usuario=usuario).count() == 2 # Hay dos cantantes favoritos para el usuario.


#-------------------------------------------------------------------------------------------
#          TEST_MODIFICA_CANTANTES_FAVORITO_REEMPLAZA_LISTA_Y_DEVUELVE_200:
# Se modifica la información de los cantantes favoritos de un usuario.
#-------------------------------------------------------------------------------------------
def test_put_cantantes_favoritos_reemplaza_lista_y_devuelve_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    
    # Se añade un cantante favorito para el usuario.
    CantanteFavorito.objects.create(usuario=usuario, nombre="Ed Sheeran")
    client = APIClient()

    # Body
    payload = {"cantantes_favoritos": ["Shakira", "Melendi"]}

    # Se realiza petición "PUT" para modificar los cantantes favoritos de un usuario.
    respuesta = client.put(
        f"/viewset/users/{usuario.id}/cantantes_favoritos/modificar/",
        payload,
        format="json",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 200, respuesta.content
    nombres = list(CantanteFavorito.objects.filter(usuario=usuario).values_list("nombre", flat=True))
    assert sorted(nombres) == ["Melendi", "Shakira"]


#-------------------------------------------------------------------------------------------
#          TEST_DELETE_CANTANTE_FAVORITO_ELIMINA_Y_DEVUELVE_200:
# Se eliminan cantantes favoritos de un usuario.
#-------------------------------------------------------------------------------------------
def test_delete_cantante_favorito_elimina_y_devuelve_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")

    # Se añaden dos cantantes favoritos para el usuario.
    CantanteFavorito.objects.create(usuario=usuario, nombre="Ed Sheeran")
    CantanteFavorito.objects.create(usuario=usuario, nombre="Melendi")
    client = APIClient()

    # Se realiza petición "DELETE" para eliminar el cantante "Ed Sheeran" de sus cantantes favoritos.
    respuesta = client.delete(
        f"/viewset/users/{usuario.id}/cantantes_favoritos/eliminar/?cantante=Ed Sheeran",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 200
    assert not CantanteFavorito.objects.filter(usuario=usuario, nombre="Ed Sheeran").exists() # "Ed Sheeran" no es su cantante favorito.
    assert CantanteFavorito.objects.filter(usuario=usuario, nombre="Melendi").exists()# "Melendi" es su cantante favorito.
    assert CantanteFavorito.objects.count() == 1 # Solo existe un cantante favorito.


############################################################################################
############################################################################################

#                                   CANCIONES FAVORITAS

############################################################################################
############################################################################################
#-------------------------------------------------------------------------------------------
#               TEST_GET_CANCIONES_FAVORITAS_DEVUELVE_LISTA_Y_200
# Se comprueba que se devuelve la lista de canciones favoritas de un usuario.
#-------------------------------------------------------------------------------------------
def test_get_canciones_favoritas_devuelve_lista_y_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")

    # Se añaden dos canciones favoritas para el usuario.
    CancionFavorita.objects.create(usuario=usuario, nombre="Tocado y Hundido")
    CancionFavorita.objects.create(usuario=usuario, nombre="La bachata")

    client = APIClient()

    # Se realiza una petición "GET" para obtener el listado de canciones favoritas del usuario.
    respuesta = client.get(f"/viewset/users/{usuario.id}/canciones_favoritas/")

    # Se verifica...
    assert respuesta.status_code == 200, respuesta.content
    data = respuesta.json()
    assert "canciones_favoritas" in data # Se comprueba que está "canciones_favoritas".
    assert isinstance(data["canciones_favoritas"], str) # Se comprueba que la lista tenga como clave.
    cant_fav = data["canciones_favoritas"]

    # Como devuelve una cadena: "Las cacniones favoritas del usuario 'x' (nombre) son '['...', '...'] "
    # Hay que extraer las canciones para comprobar si son los que realmente deberían ser.
    # Por tanto, primero se busca el primer bloque "[...]"" dentro de la cadena de texto
    m = re.search(r"\[.*\]", cant_fav)
    assert m is not None, f"No se encontró lista en el texto: {cant_fav}"

    lista = ast.literal_eval(m.group(0))  # Convierte "['La bachata', 'Tocado y Hundido']" -> ['La bachata','Tocado y Hundido']
    assert isinstance(lista, list)
    assert len(lista) == 2
    assert "La bachata" in lista # Comprueba que "La bachata" esté en la lista de cantantes favoritos.
    assert "Tocado y Hundido" in lista  # Comprueba que "Tocado y Hundido" esté en la lista de cantantes favoritos.
#-------------------------------------------------------------------------------------------
#           TEST_GET_CANCIONES_FAVORITOS_DEVUELVE_LISTA_VACIA
# Se comprueba que un usuario sin canciones favoritas devuelve una lista vacía.
#-------------------------------------------------------------------------------------------
def test_get_canciones_favoritas_sin_datos_devuelve_lista_vacia():

    # Se crea un usuario
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    # Se realiza petición "GET" para obtener el listado de canciones favoritas del usuario.
    respuesta = client.get(f"/viewset/users/{usuario.id}/canciones_favoritas/")

    # Se verifica...
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert "canciones_favoritas" in data # Se comprueba que está "canciones_favoritas".
    assert data["canciones_favoritas"] == [] # No hay ninguna canción favorita.
 

#-------------------------------------------------------------------------------------------
#          TEST_POST_CANCIONES_FAVORITAS_ANYADIR_CON_AUTORIZACION_Y_DEVUELVE_201
# Se comprueba que se añaden canciones favoritas a un usuario.
#-------------------------------------------------------------------------------------------
def test_post_canciones_favoritas_anyadir_con_autorizacion_y_devuelve_201():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    client = APIClient()

    # Body
    payload = {"canciones_favoritas": ["La bachata", "Tocado y Hundido"]}

    # Se realiza petición "POST" añadiendo la información para el usuario, incluyendo la autenticación.
    respuesta = client.post(
        f"/viewset/users/{usuario.id}/canciones_favoritas/anyadir/",
        payload,
        format="json",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 201, respuesta.content
    assert CancionFavorita.objects.filter(usuario=usuario).count() == 2 # Hay dos canciones favoritas para el usuario.


#-------------------------------------------------------------------------------------------
#          TEST_MODIFICA_CANCIONES_FAVORITAS_REEMPLAZA_LISTA_Y_DEVUELVE_200:
# Se modifica la información de las canciones favoritas de un usuario.
#-------------------------------------------------------------------------------------------
def test_put_canciones_favoritas_reemplaza_lista_y_devuelve_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")
    
    # Se añade una canción favorita para el usuario.
    CancionFavorita.objects.create(usuario=usuario, nombre="Tocado y Hundido")
    client = APIClient()

    # Body
    payload = {"canciones_favoritas": ["La llorona", "La bachata"]}

    # Se realiza petición "PUT" para modificar las canciones favoritas de un usuario.
    respuesta = client.put(
        f"/viewset/users/{usuario.id}/canciones_favoritas/modificar/",
        payload,
        format="json",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 200, respuesta.content
    nombres = list(CancionFavorita.objects.filter(usuario=usuario).values_list("nombre", flat=True))
    assert sorted(nombres) == ["La bachata", "La llorona"] # Están las canciones "La bachata" y "La llorona" en su lista de canciones favoritas.


#-------------------------------------------------------------------------------------------
#          TEST_DELETE_CANCION_FAVORITA_ELIMINA_Y_DEVUELVE_200:
# Se elimina canción favorita de un usuario.
#-------------------------------------------------------------------------------------------
def test_delete_cancion_favorita_elimina_y_devuelve_200():
    # Se crea un usuario.
    usuario = Usuario.objects.create(nombre="Lola")

    # Se añaden dos canciones favoritas para el usuario.
    CancionFavorita.objects.create(usuario=usuario, nombre="La bachata")
    CancionFavorita.objects.create(usuario=usuario, nombre="La llorona")
    client = APIClient()

    # Se realiza petición "DELETE" para eliminar la canción "La bachata" de sus canciones favoritas.
    respuesta = client.delete(
        f"/viewset/users/{usuario.id}/canciones_favoritas/eliminar/?cancion=La bachata",
        HTTP_AUTHORIZATION="1234"
    )

    # Se verifica...
    assert respuesta.status_code == 200
    assert not CancionFavorita.objects.filter(usuario=usuario, nombre="La bachata").exists() # "La bachata" no es su canción favorita.
    assert CancionFavorita.objects.filter(usuario=usuario, nombre="La llorona").exists() # "La llorona" es su canción favorita.
    assert CancionFavorita.objects.count() == 1 # Solo existe una canción favorita.
