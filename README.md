# API SPOTIFY - DJANGO
# ----------------------------------------

----------
OBJETIVOS
----------
Desarrollar una API que permita gestionar los usuarios y sus gustos musicales (cantantes y canciones favoritas),
los cuales están almacenados en una base de datos.

Además, se puede consultar más información acerca de sus gustos musicales en Spotify.

Este proyecto se ha implementando utilizando Django.

-----------
INSTALACIÓN
-----------

1. Crear un entorno virtual (recomendado)

python -m venv venv


2. Activarlo

venv\Scripts\activate


3. Instalar dependencias

pip install -r requirements.txt

4. Migraciones

cd backend (Dirigirse a la carpeta backend)

python manage.py makemigrations

python manage.py migrate


5. Ejecutarlo

python manage.py runserver

-----------
ENDPOINTS
-----------

USUARIOS
---------
- POST /viewset/users/
Crea uno o varios usuarios.

    Body:

        {
            "users": [
                    {"nombre": "Pepa"}, 
                    {"nombre": "Luis"}
            ]
                    
        }

- GET /viewset/users/

Obtiene la lista de todos los usuarios.

- PUT /viewset/users/{id}

Modifica el nombre del usuario existente. Se requiere de autorización para realizar la modificación del usuario.
    
    Body:
        { "nombre" : "Jaimito"}

- DELETE /viewset/users/{id}
Elimina un usuario por ID.



CANTANTES FAVORITOS
-------

- POST /viewset/users/{id}/cantantes_favoritos/anyadir/

Añade uno o varios cantantes favoritos al usuario.
Se requiere de autorización para añadir cantantes favoritos a un usuario.

    Body:

        { 
            "cantantes_favoritos": ["Luis Miguel", "Ed Sheeran"]
        }

- GET /viewset/users/{id}/cantantes_favoritos

Obtiene la lista de cantantes favoritos del usuario.

- PUT /viewset/users/{id}/cantantes_favoritos/modificar/

Reemplaza completamente la lista de cantantes favoritos del usuario.
Se requiere de autorización para realizar la modificación de los cantantes favoritos de un usuario.

    Body:

        { 
            "cantantes_favoritos": ["Bruno Mars", "Melendi", "Shakira"]
        }

- DELETE /viewset/users/{id}/cantantes_favoritos/eliminar/?cantante=

Elimina un cantante favorito concreto del usuario.

Se requiere de autorización para realizar la eliminación de los cantantes favoritos de un usuario.

CANCIONES FAVORITAS
-------

- POST /viewset/users/{id}/canciones_favoritas/anyadir/

Añade uno o varias canciones favoritas al usuario.
Se requiere de autorización para añadir canciones favoritas a un usuario.

    Body:

        { 
            "canciones_favoritas": ["Tocado y Hundido", "All you need is love"]
        }

- GET /viewset/users/{id}/canciones_favoritas/

Obtiene la lista de canciones favoritas del usuario.

- PUT /viewset/users/{id}/canciones_favoritas/modificar/

Reemplaza completamente la lista de canciones favoritas del usuario.
Se requiere de autorización para realizar la modificación de las canciones favoritas de un usuario.

    Body:

        { 
            "canciones_favoritas": ["Shape of You", "Perfect"]
        }
        
- DELETE /viewset/users/{id}/cantantes_favoritos/eliminar/?cancion=

Elimina una canción favorita concreta del usuario.

Se requiere de autorización para realizar la eliminación de las canciones favoritas de un usuario.

INTEGRACIÓN CON SPOTIFY
-------

- GET /viewset/users/{id}/artistas_spotify/

Obtiene información de Spotify acerca de los cantantes favoritos del usuario.

La llamada a la API de Spotify se realiza con “search_artist()”.

- GET /viewset/users/{id}/canciones_spotify/

Obtiene información de Spotify acerca de las canciones favoritas del usuario.

La llamada a la API de Spotify se realiza con “search_artist()”. 