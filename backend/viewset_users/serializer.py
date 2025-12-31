from rest_framework import serializers
from .models import Usuario

#                                   VALIDACIONES
# SERIALIZER: Se encarga de validar que los datos que se pasado por el JSON (body) ---> Postman
#             sean los correctos. Para que así, VIEW solamente tenga que implementar la funcionalidad
#             y no hacer comprobaciones.
# validate_<NOMBRE_DEL_CAMPO_A_VALIDAR>


# UsuarioSerializer: comprueba UN usuario
#   { 
#     "id": 34,
#     "nombre": "Pepe" 
#   }  
# 
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta: # Definimos las característicxas del serializer.
        # Definiendo primeramente el modelo y luego los campos del serializer.
        model = Usuario 
        fields = ['id','nombre']
        read_only_fields = ['id'] # Campos que el usuario NO puede modificar

    
    # También, permite en el SERIALIZER checkear que los campos sean los correctos.
    def validate_nombre(self, value): # Se asegura que el campo "nombre" tenga valor
        if(not value or not value.strip()):
            raise serializers.ValidationError("El campo 'nombre' es obligatorio.")
        return value 

# ListaUsuariosSerializer: comprueba un CONJUNTO de usuarios
# {
#   "users": [
#          { "nombre": "Pepe" },
#          { "nombre": "Laura" }
#   ]
# }
class ListaUsuariosSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_users(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Se debe enviar una lista 'users' con usuarios")
        for usuario in value:
            if not usuario.get("nombre"):
                raise serializers.ValidationError("Cada usuario debe tener 'nombre'")
        return value


# Body JSON { "cantantes_favoritos": ["Adele", "Melendi"]}
class CantantesFavoritosSerializer(serializers.Serializer):
    cantantes_favoritos = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )
    def validate_cantantes_favoritos(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError(
                "Se debe enviar una lista 'cantantes_favoritos' con cantantes"
            )
        return value
# Body JSON { "canciones_favoritas": ["Tocado y Hundido"]}
class CancionesFavoritasSerializer(serializers.Serializer):
    canciones_favoritas = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )
    def validate_canciones_favoritas(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError(
                "Se debe enviar una lista 'canciones_favoritas' con canciones"
            )
        return value
        