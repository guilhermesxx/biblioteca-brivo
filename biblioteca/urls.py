from django.contrib import admin
from django.urls import path, include
from brivo.views import CustomTokenObtainPairView  # Sua view customizada
from rest_framework_simplejwt.views import TokenRefreshView # Importa TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('brivo.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # CORREÇÃO: Usar TokenRefreshView para o refresh do token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
