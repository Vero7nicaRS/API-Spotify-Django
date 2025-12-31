from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet

router = DefaultRouter() 
router.register(r'users', UsuarioViewSet, basename='user') # Registrar en el router los endpoints que queremos

urlpatterns = router.urls