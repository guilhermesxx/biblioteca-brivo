from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LivroViewSet, EmprestimoViewSet, ReservaViewSet, TesteEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LembreteDevolucaoView

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
]

urlpatterns += [
    path('lembrete-devolucao/', LembreteDevolucaoView.as_view()),
]

