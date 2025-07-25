from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LivroViewSet, EmprestimoViewSet, ReservaViewSet, TesteEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LembreteDevolucaoView, DashboardAdminView
from brivo.views import AvisoReservaExpirandoView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.urls import path
from .views import usuario_me_view


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'livros', LivroViewSet)
router.register(r'emprestimos', EmprestimoViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('teste-email/', TesteEmailView.as_view()),
    path('dashboard/', DashboardAdminView.as_view(), name='dashboard-admin'),
    path('usuarios/me/', usuario_me_view, name='usuario-me'),
    
    

]

urlpatterns += [
    path('lembrete-devolucao/', LembreteDevolucaoView.as_view()),
    path("avisar-reservas-expirando/", AvisoReservaExpirandoView.as_view()),
]

