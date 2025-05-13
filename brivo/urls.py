from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LivroViewSet, EmprestimoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'livros', LivroViewSet)
router.register(r'emprestimos', EmprestimoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
