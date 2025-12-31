from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self): # Printar los usuarios
        return self.username
    
    class Meta: # Crear una subclase para permitir añadir más información.
        # Podemos añadir subcomportamientos 
        # Cuando me devuelva la información el modelo, los últimos nombres añadidos, aparezcan al principio
        ordering = ['nombre']

class CantanteFavorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    class Meta:
        unique_together = ("usuario", "nombre")
        
    def __str__(self): # Printar los cantantes favoritos
        return f"{self.usuario_id} - {self.nombre}"

class CancionFavorita(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    class Meta:
        unique_together = ("usuario", "nombre")

    def __str__(self): # Printar las canciones favoritas
        return f"{self.usuario_id} - {self.nombre}"

#Serializers obtener información más sencilla del modelo.
