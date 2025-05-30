from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Livro, Usuario, Emprestimo, Reserva
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer, ReservaSerializer
from .permissions import EhDonoOuAdmin, EhAdmin
from rest_framework.views import APIView

from .utils import enviar_email


from rest_framework.views import APIView
from .utils import enviar_email

class TesteEmailView(APIView):
    def get(self, request):
        enviar_email(
            destinatario='contaescola338@gmail.com',  # <-- coloque aqui o e-mail que vai receber o teste
            assunto='Teste de E-mail',
            mensagem='Este é um teste do sistema da biblioteca.'
        )
        return Response({'mensagem': 'E-mail enviado com sucesso'})


class TesteEmailView(APIView):
    def get(self, request):
        enviar_email(
            destinatario='destinatario@gmail.com',
            assunto='Teste de E-mail',
            mensagem='Este é um teste de envio de e-mail no Django.'
        )
        return Response({'mensagem': 'E-mail enviado com sucesso'})


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
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), EhAdmin()]


# ✅ Regras de visualização/edição para empréstimos
class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.tipo in ['admin', 'professor']:
            return Emprestimo.objects.all()
        return Emprestimo.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        devolvido_antes = instance.devolvido
        emprestimo = serializer.save()

        if not devolvido_antes and emprestimo.devolvido:
            emprestimo.marcar_devolucao()


# ✅ Criar reservas se livro estiver indisponível e usuário ainda não reservou
class CriarReservaAPIView(generics.CreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        livro_id = request.data.get("livro")

        try:
            livro = Livro.objects.get(id=livro_id)
        except Livro.DoesNotExist:
            return Response({"erro": "Livro não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if livro.disponivel:
            return Response(
                {"erro": "O livro está disponível. Você pode fazer o empréstimo em vez de reservar."},
                status=400
            )

        ja_reservado = Reserva.objects.filter(
            livro=livro,
            aluno=request.user,
            status__in=['na_fila', 'aguardando_confirmacao', 'notificado']
        ).exists()
        if ja_reservado:
            return Response({"erro": "Você já possui uma reserva ativa para este livro."}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(aluno=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ✅ ViewSet para reservas com endpoint de confirmação
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'admin':
            return Reserva.objects.all()
        return Reserva.objects.filter(aluno=user)

    @action(detail=True, methods=['post'], url_path='confirmar')
    def confirmar_reserva(self, request, pk=None):
        reserva = self.get_object()

        if reserva.aluno != request.user:
            return Response({'erro': 'Reserva não pertence a este usuário.'}, status=403)

        if reserva.status != 'aguardando_confirmacao':
            return Response({'erro': 'Reserva não está aguardando confirmação.'}, status=400)

        if not reserva.livro.disponivel:
            return Response({'erro': 'Livro não está mais disponível.'}, status=400)

        # Criar empréstimo
        emprestimo = Emprestimo.objects.create(
            livro=reserva.livro,
            usuario=reserva.aluno
        )

        # Atualizar reserva
        reserva.status = 'concluido'
        reserva.save()

        return Response({'mensagem': 'Reserva confirmada e empréstimo criado com sucesso.'}, status=200)
