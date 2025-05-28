from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from .models import Livro, Usuario, Emprestimo
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer
from .permissions import EhDonoOuAdmin, EhAdmin

# ✅ Apenas administradores podem gerenciar usuários
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, EhAdmin]


# ✅ Qualquer usuário autenticado pode visualizar livros (GET)
# ✅ Somente administradores podem criar, editar ou deletar livros
class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return [IsAuthenticated()]
        return [IsAuthenticated(), EhAdmin()]  # POST, PUT, PATCH, DELETE


# ✅ Regras de visualização/edição para empréstimos
class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def get_queryset(self):
        user = self.request.user
        # Admins e professores veem todos os empréstimos
        if user.tipo in ['admin', 'professor']:
            return Emprestimo.objects.all()
        # Alunos só veem os próprios
        return Emprestimo.objects.filter(usuario=user)

    def perform_create(self, serializer):
        # Define o usuário autenticado como dono do empréstimo
        emprestimo = serializer.save(usuario=self.request.user)
        # Marca o livro como indisponível
        emprestimo.livro.disponivel = False
        emprestimo.livro.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        devolvido_antes = instance.devolvido
        emprestimo = serializer.save()

        # Se o campo 'devolvido' foi marcado agora, registra a devolução
        if not devolvido_antes and emprestimo.devolvido:
            emprestimo.marcar_devolucao()
