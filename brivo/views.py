from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import Livro, Usuario, Emprestimo, Reserva
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer, ReservaSerializer
from .permissions import EhDonoOuAdmin, EhAdmin
from .utils import enviar_email, enviar_lembretes_de_devolucao, notificar_primeiro_da_fila ,enviar_avisos_reserva_expirando
from rest_framework import status
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Livro
from .serializers import LivroSerializer
from .utils import registrar_acao
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

# ARRUMAR ACIMA PODE TER ALGUMS DUPLICADOS

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Livro
from .serializers import LivroSerializer
from .permissions import EhAdmin
from .utils import registrar_acao

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.ativos()
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated]  # default

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['titulo', 'autor', 'genero']
    search_fields = ['titulo', 'autor', 'genero', 'descricao']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), EhAdmin()]

    def get_queryset(self):
        return Livro.objects.ativos()

    def perform_create(self, serializer):
        livro = serializer.save()
        registrar_acao(self.request.user, livro, 'CRIACAO', descricao='Livro criado.')

    def perform_update(self, serializer):
        livro = serializer.save()
        registrar_acao(self.request.user, livro, 'EDICAO', descricao='Livro editado.')

    def destroy(self, request, *args, **kwargs):
        livro = self.get_object()
        livro.ativo = False
        livro.save()
        registrar_acao(request.user, livro, 'DESATIVACAO', descricao='Livro desativado.')
        return Response({'mensagem': 'Livro desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

# brivo/views.py (adicione no final)

class AvisoReservaExpirandoView(APIView):
    def get(self, request):
        enviar_avisos_reserva_expirando()
        return Response({"mensagem": "Avisos de reserva prestes a expirar enviados com sucesso."})


# ---------------------------
# ✅ Usuários (admin-only)
# ---------------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, EhAdmin]

    def perform_create(self, serializer):
        usuario = serializer.save()
        registrar_acao(self.request.user, usuario, 'CRIACAO', descricao='Usuário criado.')

    def perform_update(self, serializer):
        usuario = serializer.save()
        registrar_acao(self.request.user, usuario, 'EDICAO', descricao='Usuário editado.')

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        usuario.ativo = False
        usuario.save()
        registrar_acao(request.user, usuario, 'DESATIVACAO', descricao='Usuário desativado.')
        return Response({'mensagem': 'Usuário desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)


# class UsuarioViewSet(viewsets.ModelViewSet):
#     queryset = Usuario.objects.all()
#     serializer_class = UsuarioSerializer
#     permission_classes = [IsAuthenticated, EhAdmin]

#     def destroy(self, request, *args, **kwargs):
#         usuario = self.get_object()
#         usuario.ativo = False
#         usuario.save()
#         return Response({'mensagem': 'Usuário desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

#     def perform_create(self, serializer):
#         usuario = serializer.save()
#         registrar_acao(self.request.user, usuario, 'CRIACAO', descricao='Usuário criado.')

#     def perform_update(self, serializer):
#         usuario = serializer.save()
#         registrar_acao(self.request.user, usuario, 'EDICAO', descricao='Usuário editado.')

#     def destroy(self, request, *args, **kwargs):
#         usuario = self.get_object()
#         usuario.ativo = False
#         usuario.save()
#         registrar_acao(request.user, usuario, 'DESATIVACAO', descricao='Usuário desativado.')
#         return Response({'mensagem': 'Usuário desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

# LINHA ACIMA VER SE VAI PRECISAR DE ALGO , FIQUEI NA DUVIDA SE ESTAVA DUPLICADO E ETC

# ---------------------------
# ✅ Livros (admin pode alterar, outros só visualizam)
# ---------------------------

# class LivroViewSet(viewsets.ModelViewSet):
#     queryset = Livro.objects.ativos()
#     serializer_class = LivroSerializer

#     def get_permissions(self):
#         if self.request.method in SAFE_METHODS:
#             return [IsAuthenticated()]
#         return [IsAuthenticated(), EhAdmin()]

#     def get_queryset(self):
#         return Livro.objects.ativos()

#     def perform_create(self, serializer):
#         livro = serializer.save()
#         registrar_acao(self.request.user, livro, 'CRIACAO', descricao='Livro criado.')

#     def perform_update(self, serializer):
#         livro = serializer.save()
#         registrar_acao(self.request.user, livro, 'EDICAO', descricao='Livro editado.')

#     def destroy(self, request, *args, **kwargs):
#         livro = self.get_object()
#         livro.ativo = False
#         livro.save()
#         registrar_acao(request.user, livro, 'DESATIVACAO', descricao='Livro desativado.')
#         return Response({'mensagem': 'Livro desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)



# ---------------------------
# PEDIR FERNANDO PARA AJUDAR ACIMA , DUPLIQUEI A LINHA 43 A 48 , E ARRUMA E ORGANIZAR
# ---------------------------

# ---------------------------
# ✅ Empréstimos
# ---------------------------

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
            


# ---------------------------
# ✅ Devolução de Empréstimo (dispara notificação da fila)
# ---------------------------

class DevolverEmprestimoView(APIView):
    def post(self, request, pk):
        try:
            emprestimo = Emprestimo.objects.get(pk=pk)
            if emprestimo.devolvido:
                return Response({"erro": "Esse empréstimo já foi devolvido."}, status=status.HTTP_400_BAD_REQUEST)

            emprestimo.devolvido = True
            emprestimo.save()

            # 🔔 Notificar o próximo da fila
            notificar_primeiro_da_fila(emprestimo.livro)

            return Response({"mensagem": "Livro devolvido com sucesso e fila notificada."})

        except Emprestimo.DoesNotExist:
            return Response({"erro": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------
# ✅ Reservas
# ---------------------------

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


# ---------------------------
# ✅ Notificações e lembretes por e-mail
# ---------------------------

class LembreteDevolucaoView(APIView):
    def get(self, request):
        enviar_lembretes_de_devolucao()
        return Response({"mensagem": "Lembretes de devolução enviados com sucesso."})


class TesteEmailView(APIView):
    def get(self, request):
        enviar_email(
            destinatario='contaescola338@gmail.com',  # Ou qualquer outro e-mail de teste
            assunto='Teste de E-mail',
            mensagem='Este é um teste do sistema da biblioteca.'
        )
        return Response({'mensagem': 'E-mail enviado com sucesso'})
    
#passo 7.2


