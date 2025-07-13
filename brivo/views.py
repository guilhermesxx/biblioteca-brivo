# brivo/views.py

from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

# Importações de modelos e serializers
from .models import Livro, Usuario, Emprestimo, Reserva
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer, ReservaSerializer
from .permissions import EhDonoOuAdmin, EhAdmin # Assumindo que estas permissões estão definidas
from .utils import (
    enviar_email, 
    enviar_lembretes_de_devolucao, 
    notificar_primeiro_da_fila, 
    enviar_avisos_reserva_expirando,
    registrar_acao # Importar a função registrar_acao
)

# Importação do Simple JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer # Importa seu serializer customizado

# -----------------------------------------------------------------------------
# Views de Autenticação e Usuário
# -----------------------------------------------------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obtenção de token JWT.
    Usa CustomTokenObtainPairSerializer para adicionar a lógica de verificação
    do campo 'tipo' e incluir dados do usuário no token.
    """
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_me_view(request):
    """
    Retorna os dados do usuário autenticado.
    Este endpoint pode ser útil para o frontend obter os detalhes do usuário logado.
    """
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar usuários.
    Permissões ajustadas:
    - Admin: pode criar, listar, atualizar e desativar qualquer usuário.
    - Aluno/Professor: pode visualizar e atualizar seu próprio perfil.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    # A permissão é definida dinamicamente no método get_permissions abaixo

    def get_permissions(self):
        """
        Define as permissões com base na ação (list, retrieve, create, update, destroy).
        """
        # Para 'create' (criar novo usuário), permita acesso sem autenticação.
        # A validação do tipo de usuário (admin, professor, aluno) será feita no serializer.
        if self.action == 'create':
            return [permissions.AllowAny()] # Permite que qualquer um (autenticado ou não) crie um usuário.
        
        # Para 'list' (listar todos os usuários), apenas administradores autenticados têm permissão.
        elif self.action == 'list':
            return [IsAuthenticated(), EhAdmin()]
        
        # Para 'retrieve' (obter detalhes de um usuário específico),
        # 'update' (atualizar um usuário) e 'partial_update' (atualizar parcialmente um usuário),
        # o usuário autenticado pode acessar seu próprio perfil, ou um administrador pode acessar qualquer perfil.
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # EhDonoOuAdmin deve verificar se o request.user é o dono do objeto OU se é um admin.
            # Isso permite que um usuário edite/veja seu próprio perfil e que admins editem/vejam qualquer perfil.
            return [IsAuthenticated(), EhDonoOuAdmin()] 
        
        # Para 'destroy' (desativar/excluir um usuário),
        # apenas administradores autenticados têm permissão.
        elif self.action == 'destroy':
            return [IsAuthenticated(), EhAdmin()]
        
        # Permissão padrão para outras ações, caso existam.
        return [IsAuthenticated()] 

    def perform_create(self, serializer):
        """
        Salva um novo usuário e registra a ação.
        """
        usuario = serializer.save()
        # Passa o usuário logado se existir, caso contrário, passa None.
        # Isso evita erros se um usuário anônimo tentar criar uma conta.
        user_for_log = self.request.user if self.request.user.is_authenticated else None
        registrar_acao(user_for_log, usuario, 'CRIACAO', descricao='Usuário criado.')

    def perform_update(self, serializer):
        """
        Atualiza um usuário existente e registra a ação.
        """
        usuario = serializer.save()
        registrar_acao(self.request.user, usuario, 'EDICAO', descricao='Usuário editado.')

    def destroy(self, request, *args, **kwargs):
        """
        Desativa (soft delete) um usuário e registra a ação.
        """
        usuario = self.get_object()
        usuario.ativo = False # Realiza um soft delete
        usuario.save()
        registrar_acao(request.user, usuario, 'DESATIVACAO', descricao='Usuário desativado.')
        return Response({'mensagem': 'Usuário desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

# -----------------------------------------------------------------------------
# Views de Livros
# -----------------------------------------------------------------------------

class LivroViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar livros.
    Admin pode criar, editar, desativar. Outros usuários podem apenas visualizar livros ativos.
    """
    queryset = Livro.objects.all() # Queryset base para admins
    serializer_class = LivroSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['titulo', 'autor', 'genero']
    search_fields = ['titulo', 'autor', 'genero', 'descricao']

    def get_permissions(self):
        """
        Define as permissões para as ações de livros.
        """
        # Para métodos seguros (GET, HEAD, OPTIONS), todos os usuários autenticados têm permissão.
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        # Para outros métodos (POST, PUT, PATCH, DELETE), apenas administradores autenticados têm permissão.
        return [IsAuthenticated(), EhAdmin()]

    def get_queryset(self):
        """
        Retorna o queryset de livros com base no tipo de usuário.
        """
        user = self.request.user
        # Se o usuário é um administrador, retorna todos os livros (ativos e inativos).
        if user.is_authenticated and user.tipo == 'admin':
            return Livro.objects.all()
        # Para outros tipos de usuário, retorna apenas os livros ativos.
        return Livro.objects.filter(ativo=True)

    def perform_create(self, serializer):
        """
        Cria um novo livro e registra a ação.
        """
        livro = serializer.save()
        registrar_acao(self.request.user, livro, 'CRIACAO', descricao='Livro criado.')

    def perform_update(self, serializer):
        """
        Atualiza um livro existente e registra a ação.
        """
        livro = serializer.save()
        registrar_acao(self.request.user, livro, 'EDICAO', descricao='Livro editado.')

    def destroy(self, request, *args, **kwargs):
        """
        Desativa (soft delete) um livro e registra a ação.
        """
        livro = self.get_object()
        livro.ativo = False # Realiza um soft delete
        livro.save()
        registrar_acao(request.user, livro, 'DESATIVACAO', descricao='Livro desativado.')
        return Response({'mensagem': 'Livro desativado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

# -----------------------------------------------------------------------------
# Views de Empréstimos
# -----------------------------------------------------------------------------

class EmprestimoViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar empréstimos.
    Admin e professor podem ver todos. Alunos veem apenas seus próprios empréstimos.
    """
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin] # EhDonoOuAdmin deve verificar se é o dono ou admin

    def get_queryset(self):
        """
        Retorna o queryset de empréstimos com base no tipo de usuário.
        """
        user = self.request.user
        # Admin e professor podem ver todos os empréstimos.
        if user.is_authenticated and user.tipo in ['admin', 'professor']:
            return Emprestimo.objects.all()
        # Alunos só podem ver seus próprios empréstimos.
        return Emprestimo.objects.filter(usuario=user)

    def perform_create(self, serializer):
        """
        Cria um novo empréstimo, associando-o ao usuário logado.
        """
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        """
        Atualiza um empréstimo existente. Se o status mudar para devolvido,
        chama o método para marcar a devolução.
        """
        instance = self.get_object()
        devolvido_antes = instance.devolvido
        emprestimo = serializer.save()

        # Se o status mudou para devolvido, chama o método para marcar devolução
        if not devolvido_antes and emprestimo.devolvido:
            emprestimo.marcar_devolucao() # Este método já atualiza o livro e notifica a fila

class DevolverEmprestimoView(APIView):
    """
    Endpoint para marcar um empréstimo como devolvido.
    Dispara a notificação para o próximo da fila de reserva.
    """
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem devolver

    def post(self, request, pk):
        try:
            emprestimo = Emprestimo.objects.get(pk=pk)
            # Verifica se o usuário tem permissão para devolver (dono do empréstimo ou admin/professor)
            if request.user.tipo not in ['admin', 'professor'] and emprestimo.usuario != request.user:
                return Response({'erro': 'Você não tem permissão para devolver este empréstimo.'}, status=status.HTTP_403_FORBIDDEN)

            if emprestimo.devolvido:
                return Response({"erro": "Esse empréstimo já foi devolvido."}, status=status.HTTP_400_BAD_REQUEST)

            emprestimo.devolvido = True
            emprestimo.save() # O método save do modelo Emprestimo já lida com a disponibilidade do livro e notificação

            return Response({"mensagem": "Livro devolvido com sucesso e fila notificada."})

        except Emprestimo.DoesNotExist:
            return Response({"erro": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------------------------
# Views de Reservas
# -----------------------------------------------------------------------------

class CriarReservaAPIView(generics.CreateAPIView):
    """
    Endpoint para criar uma nova reserva.
    Verifica a disponibilidade do livro e se o usuário já tem uma reserva ativa.
    """
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
                status=status.HTTP_400_BAD_REQUEST # Use status.HTTP_400_BAD_REQUEST para erros de cliente
            )

        ja_reservado = Reserva.objects.filter(
            livro=livro,
            aluno=request.user,
            status__in=['na_fila', 'aguardando_confirmacao'] # Removido 'notificado' pois é um status transitório
        ).exists()
        if ja_reservado:
            return Response({"erro": "Você já possui uma reserva ativa para este livro."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(aluno=request.user) # Associa a reserva ao usuário logado
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar reservas.
    Admin pode ver todas. Alunos veem apenas suas próprias reservas.
    """
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin] # EhDonoOuAdmin deve verificar se é o dono ou admin

    def get_queryset(self):
        """
        Retorna o queryset de reservas com base no tipo de usuário.
        """
        user = self.request.user
        # Admin pode ver todas as reservas.
        if user.is_authenticated and user.tipo == 'admin':
            return Reserva.objects.all()
        # Alunos só podem ver suas próprias reservas.
        return Reserva.objects.filter(aluno=user)

    @action(detail=True, methods=['post'], url_path='confirmar')
    def confirmar_reserva(self, request, pk=None):
        """
        Confirma uma reserva e cria um empréstimo.
        Apenas o aluno que fez a reserva pode confirmá-la.
        """
        reserva = self.get_object()

        # Verifica se a reserva pertence ao usuário logado
        if reserva.aluno != request.user:
            return Response({'erro': 'Reserva não pertence a este usuário.'}, status=status.HTTP_403_FORBIDDEN)

        # Verifica o status da reserva
        if reserva.status != 'aguardando_confirmacao':
            return Response({'erro': 'Reserva não está aguardando confirmação.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica a disponibilidade do livro novamente
        if not reserva.livro.disponivel:
            return Response({'erro': 'Livro não está mais disponível.'}, status=status.HTTP_400_BAD_REQUEST)

        # Criar empréstimo
        emprestimo = Emprestimo.objects.create(
            livro=reserva.livro,
            usuario=reserva.aluno
        )

        # Atualizar status da reserva para 'concluido'
        reserva.status = 'concluido'
        reserva.save()

        return Response({'mensagem': 'Reserva confirmada e empréstimo criado com sucesso.'}, status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------
# Views de Notificações e Lembretes por E-mail
# -----------------------------------------------------------------------------

class LembreteDevolucaoView(APIView):
    """
    Endpoint para enviar lembretes de devolução de livros.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin] # Apenas admin pode disparar isso

    def get(self, request):
        enviar_lembretes_de_devolucao()
        return Response({"mensagem": "Lembretes de devolução enviados com sucesso."})

class AvisoReservaExpirandoView(APIView):
    """
    Endpoint para enviar avisos de reservas prestes a expirar.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin] # Apenas admin pode disparar isso

    def get(self, request):
        enviar_avisos_reserva_expirando()
        return Response({"mensagem": "Avisos de reserva prestes a expirar enviados com sucesso."})

class TesteEmailView(APIView):
    """
    Endpoint para testar o envio de e-mails.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin] # Apenas admin pode disparar isso

    def get(self, request):
        enviar_email(
            destinatario='contaescola338@gmail.com',  # Ou qualquer outro e-mail de teste
            assunto='Teste de E-mail da Biblioteca Brivo',
            mensagem='Este é um teste do sistema de e-mails da biblioteca. Se você recebeu este e-mail, a configuração está funcionando corretamente.'
        )
        return Response({'mensagem': 'E-mail de teste enviado com sucesso'})

# -----------------------------------------------------------------------------
# Views de Dashboard e Estatísticas
# -----------------------------------------------------------------------------

class DashboardAdminView(APIView):
    """
    Endpoint para o dashboard administrativo com estatísticas da biblioteca.
    Apenas administradores podem acessar.
    """
    permission_classes = [IsAuthenticated] # Permissão inicial para garantir que o usuário está logado

    def get(self, request):
        # Verifica o tipo de usuário explicitamente para o dashboard
        if request.user.tipo != 'admin':
            return Response({'erro': 'Acesso negado. Apenas administradores podem acessar o dashboard.'}, status=status.HTTP_403_FORBIDDEN)

        # 🗓️ Filtro por período (query param ?periodo=ultimos_7_dias ou mes_atual)
        periodo = request.query_params.get('periodo')
        agora = timezone.now()

        filtro_usuarios = {}
        filtro_emprestimos = {}
        filtro_reservas = {}

        if periodo == 'ultimos_7_dias':
            data_limite = agora - timedelta(days=7)
            filtro_usuarios = {'data_cadastro__gte': data_limite}
            filtro_emprestimos = {'data_emprestimo__gte': data_limite}
            filtro_reservas = {'data_reserva__gte': data_limite}

        elif periodo == 'mes_atual':
            inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtro_usuarios = {'data_cadastro__gte': inicio_mes}
            filtro_emprestimos = {'data_emprestimo__gte': inicio_mes}
            filtro_reservas = {'data_reserva__gte': inicio_mes}

        # 📊 Estatísticas básicas
        total_livros = Livro.objects.count()
        livros_ativos = Livro.objects.filter(ativo=True).count()
        livros_inativos = Livro.objects.filter(ativo=False).count()

        total_usuarios = Usuario.objects.filter(ativo=True, **filtro_usuarios).count()
        total_alunos = Usuario.objects.filter(ativo=True, tipo='aluno', **filtro_usuarios).count()
        total_professores = Usuario.objects.filter(ativo=True, tipo='professor', **filtro_usuarios).count()
        total_admins = Usuario.objects.filter(ativo=True, tipo='admin', **filtro_usuarios).count()

        reservas_na_fila = Reserva.objects.filter(status='na_fila', **filtro_reservas).count()
        reservas_aguardando = Reserva.objects.filter(status='aguardando_confirmacao', **filtro_reservas).count()
        reservas_concluidas = Reserva.objects.filter(status='concluido', **filtro_reservas).count()
        reservas_expiradas = Reserva.objects.filter(status='expirado', **filtro_reservas).count()

        emprestimos_ativos = Emprestimo.objects.filter(devolvido=False, **filtro_emprestimos).count()
        emprestimos_concluidos = Emprestimo.objects.filter(devolvido=True, **filtro_emprestimos).count()

        # 📈 Gráficos (gerais, sem filtro de data, ou com filtro se a lógica for adicionada)
        emprestimos_por_mes = (
            Emprestimo.objects.annotate(mes=TruncMonth('data_emprestimo'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        reservas_por_mes = (
            Reserva.objects.annotate(mes=TruncMonth('data_reserva'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        return Response({
            'filtro_aplicado': periodo or 'todos',
            'livros': {
                'total': total_livros,
                'ativos': livros_ativos,
                'inativos': livros_inativos,
            },
            'usuarios': {
                'total': total_usuarios,
                'alunos': total_alunos,
                'professores': total_professores,
                'admins': total_admins,
            },
            'reservas': {
                'na_fila': reservas_na_fila,
                'aguardando': reservas_aguardando,
                'concluidas': reservas_concluidas,
                'expiradas': reservas_expiradas,
            },
            'emprestimos': {
                'ativos': emprestimos_ativos,
                'devolvidos': emprestimos_concluidos,
            },
            'graficos': {
                'emprestimos_por_mes': list(emprestimos_por_mes),
                'reservas_por_mes': list(reservas_por_mes),
            }
        })
