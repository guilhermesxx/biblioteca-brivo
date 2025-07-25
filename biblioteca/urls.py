from django.contrib import admin
from django.urls import path, include
from brivo.views import CustomTokenObtainPairView  # Sua view customizada
from django.conf import settings
from django.conf.urls.static import static
from brivo.views import CriarReservaAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('brivo.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # necessário!
    path('api/token/refresh/', CustomTokenObtainPairView.as_view(), name='token_refresh'),
    path('api/reservas/', CriarReservaAPIView.as_view(), name='criar-reserva'),
]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

