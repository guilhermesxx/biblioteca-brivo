from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Removidas importações redundantes de TokenObtainPairView e CustomTokenObtainPairSerializer
from .views import (
    UsuarioViewSet, LivroViewSet, EmprestimoViewSet, ReservaViewSet, 
    TesteEmailView, LembreteDevolucaoView, DashboardAdminView, 
    AvisoReservaExpirandoView, usuario_me_view, AlertaSistemaViewSet,
    PublicAlertaSistemaListView,
    RelatoriosPedagogicosView, # NOVO: Importe a nova view
    # 📧 NOVAS VIEWS DE EMAIL
    EnviarEmailManualView, EnviarEmailGrupoView, EnviarEmailsPredefinidosView, ListarTiposEmailView
)


router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'livros', LivroViewSet)
router.register(r'emprestimos', EmprestimoViewSet)
router.register(r'reservas', ReservaViewSet) # Este router já lida com a criação, listagem, etc.
router.register(r'alertas-sistema', AlertaSistemaViewSet) # NOVO: Registro do ViewSet de Alertas do Sistema

urlpatterns = [
    path('', include(router.urls)),
    path('teste-email/', TesteEmailView.as_view()),
    path('dashboard/', DashboardAdminView.as_view(), name='dashboard-admin'),
    path('usuarios/me/', usuario_me_view, name='usuario-me'),
    path('alertas/publicos/', PublicAlertaSistemaListView.as_view(), name='alertas_publicos'),
    path('relatorios/pedagogicos/', RelatoriosPedagogicosView.as_view(), name='relatorios-pedagogicos'),
    # 📧 NOVAS ROTAS PARA SISTEMA DE EMAILS
    path('emails/enviar-manual/', EnviarEmailManualView.as_view(), name='enviar-email-manual'),
    path('emails/enviar-grupo/', EnviarEmailGrupoView.as_view(), name='enviar-email-grupo'),
    path('emails/predefinidos/', EnviarEmailsPredefinidosView.as_view(), name='emails-predefinidos'),
    path('emails/tipos/', ListarTiposEmailView.as_view(), name='listar-tipos-email'),
]

urlpatterns += [
    path('lembrete-devolucao/', LembreteDevolucaoView.as_view()),
    path("avisar-reservas-expirando/", AvisoReservaExpirandoView.as_view()),
]
