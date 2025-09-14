from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F, Q
from django.utils import timezone # Importação essencial para lidar com fusos horários
from datetime import timedelta, date
from django.db.models import Count
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Replace with your actual models and permissions
from .models import Livro, Usuario, Emprestimo, Reserva
from .permissions import EhAdmin
from django.utils import timezone

# Importações de modelos e serializers
from .models import Livro, Usuario, Emprestimo, Reserva, AlertaSistema
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer, ReservaSerializer, AlertaSistemaSerializer
from .permissions import EhDonoOuAdmin, EhAdmin, EhProfessorOuAdmin
from .utils import (
    enviar_email,
    enviar_lembretes_de_devolucao,
    notificar_primeiro_da_fila,
    enviar_avisos_reserva_expirando,
    registrar_acao,
    enviar_notificacao_alerta_publico
)

# Importação do Simple JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

# Logger
import logging
logger = logging.getLogger(__name__)

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
    queryset = Usuario.objects.all().order_by('nome') # CORREÇÃO: Adicionado order_by para paginação consistente
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo']
    search_fields = ['nome', 'email', 'ra', 'turma']

    def get_permissions(self):
        """
        Define as permissões com base na ação (list, retrieve, create, update, destroy).
        """
        if self.action == 'create':
            return [permissions.AllowAny()]

        # Para 'list' (listar todos os usuários) e 'counts' (obter contagens),
        # apenas administradores autenticados têm permissão.
        elif self.action in ['list', 'counts']:
            return [IsAuthenticated(), EhAdmin()]

        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), EhDonoOuAdmin()]

        elif self.action == 'destroy':
            return [IsAuthenticated(), EhAdmin()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Retorna o queryset de usuários ativos por padrão para listagem.
        Admins podem ver todos.
        """
        user = self.request.user
        if user.is_authenticated and user.tipo == 'admin':
            queryset = Usuario.objects.all().order_by('nome') # CORREÇÃO: Adicionado order_by
        else:
            queryset = Usuario.objects.filter(ativo=True).order_by('nome') # CORREÇÃO: Adicionado order_by

        # O DjangoFilterBackend e SearchFilter já aplicam os filtros automaticamente
        # com base em filterset_fields e search_fields definidos acima.
        return queryset


    def perform_create(self, serializer):
        """
        Salva um novo usuário e registra a ação.
        DISPARA EMAIL DE BOAS-VINDAS AUTOMATICAMENTE
        """
        usuario = serializer.save()
        user_for_log = self.request.user if self.request.user.is_authenticated else None
        registrar_acao(user_for_log, usuario, 'CRIACAO', descricao='Usuário criado.')
        
        # ENVIAR EMAIL DE BOAS-VINDAS AUTOMATICAMENTE (NÃO QUEBRA SE FALHAR)
        try:
            from .utils import enviar_email_boas_vindas
            enviar_email_boas_vindas(usuario)
        except Exception as e:
            logger.warning(f"Email de boas-vindas nao enviado para {usuario.email}: {str(e)}")

    def perform_update(self, serializer):
        """
        Atualiza um usuário existente e registra a ação.
        """
        usuario = serializer.save()
        registrar_acao(self.request.user, usuario, 'EDICAO', descricao='Usuário editado.')

    def destroy(self, request, *args, **kwargs):
        """
        Remove completamente um usuário do sistema (hard delete).
        Remove todas as dependências relacionadas antes da exclusão.
        """
        usuario = self.get_object()
        
        # Impede que o usuário delete a si mesmo
        if usuario.id == request.user.id:
            return Response({'erro': 'Você não pode excluir sua própria conta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove todas as reservas do usuário
        Reserva.objects.filter(aluno=usuario).delete()
        
        # Remove todos os empréstimos do usuário
        Emprestimo.objects.filter(usuario=usuario).delete()
        
        # Registra a ação antes de deletar
        registrar_acao(request.user, usuario, 'DESATIVACAO', descricao=f'Usuário "{usuario.nome}" e todas suas dependências deletados permanentemente.')
        
        # HARD DELETE - remove completamente do banco
        usuario.delete()
        
        return Response({'mensagem': 'Usuário deletado permanentemente com sucesso.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='counts', permission_classes=[IsAuthenticated, EhAdmin])
    def counts(self, request):
        """
        Retorna as contagens de usuários por tipo (total, alunos, professores, admins).
        Apenas administradores podem acessar.
        """
        total_usuarios_ativos = Usuario.objects.filter(ativo=True).count()
        total_alunos = Usuario.objects.filter(ativo=True, tipo='aluno').count()
        total_professores = Usuario.objects.filter(ativo=True, tipo='professor').count()
        total_admins = Usuario.objects.filter(ativo=True, tipo='admin').count()

        return Response({
            'total_usuarios_ativos': total_usuarios_ativos,
            'alunos': total_alunos,
            'professores': total_professores,
            'admins': total_admins,
        }, status=status.HTTP_200_OK)


# -----------------------------------------------------------------------------
# Views de Livros
# -----------------------------------------------------------------------------

class LivroViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar livros.
    Admin pode criar, editar, deletar. Outros usuários podem apenas visualizar livros ativos.
    """
    queryset = Livro.objects.all().order_by('titulo')
    serializer_class = LivroSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['titulo', 'autor', 'genero']
    search_fields = ['titulo', 'autor', 'genero', 'descricao']

    def get_permissions(self):
        """
        Define as permissões para as ações de livros.
        """
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), EhAdmin()]

    def get_queryset(self):
        """
        Retorna o queryset de livros com base no tipo de usuário.
        """
        user = self.request.user
        if user.is_authenticated and user.tipo == 'admin':
            return Livro.objects.all().order_by('titulo')
        return Livro.objects.filter(ativo=True).order_by('titulo')

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
        Deleta completamente um livro (hard delete) removendo todas as dependências.
        """
        livro = self.get_object()
        
        # Remove todas as reservas relacionadas ao livro
        Reserva.objects.filter(livro=livro).delete()
        
        # Remove todos os empréstimos relacionados ao livro
        Emprestimo.objects.filter(livro=livro).delete()
        
        # Remove todos os alertas relacionados ao livro
        AlertaSistema.objects.filter(titulo__icontains=livro.titulo).delete()
        
        # Registra a ação antes de deletar
        registrar_acao(request.user, livro, 'DESATIVACAO', descricao=f'Livro "{livro.titulo}" e todas suas dependências deletados permanentemente.')
        
        # HARD DELETE - remove completamente do banco
        livro.delete()
        
        return Response({'mensagem': 'Livro e todas suas dependências deletados permanentemente.'}, status=status.HTTP_204_NO_CONTENT)

# -----------------------------------------------------------------------------
# Views de Empréstimzs
# -----------------------------------------------------------------------------

class EmprestimoViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar empréstimos.
    Admin e professor podem ver todos. Alunos veem apenas seus próprios empréstimos.
    """
    queryset = Emprestimo.objects.all().order_by('-data_emprestimo') # CORREÇÃO: Adicionado order_by
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de empréstimos com base no tipo de usuário.
        """
        user = self.request.user
        if user.is_authenticated and user.tipo in ['admin', 'professor']:
            return Emprestimo.objects.all().order_by('-data_emprestimo') # CORREÇÃO: Adicionado order_by
        return Emprestimo.objects.filter(usuario=user).order_by('-data_emprestimo') # CORREÇÃO: Adicionado order_by

    def perform_create(self, serializer):
        """
        Cria um novo empréstimo, associando-o ao usuário logado.
        DISPARA EMAIL DE CONFIRMAÇÃO DE EMPRÉSTIMO AUTOMATICAMENTE
        """
        emprestimo = serializer.save(usuario=self.request.user)
        
        # ENVIAR EMAIL DE CONFIRMAÇÃO DE EMPRÉSTIMO AUTOMATICAMENTE (NÃO QUEBRA SE FALHAR)
        try:
            from .utils import enviar_email_emprestimo_confirmado
            enviar_email_emprestimo_confirmado(emprestimo)
        except Exception as e:
            logger.warning(f"Email de emprestimo nao enviado para {emprestimo.usuario.email}: {str(e)}")

    def perform_update(self, serializer):
        """
        Atualiza um empréstimo existente. Se o status mudar para devolvido,
        chama o método para marcar a devolução.
        """
        instance = self.get_object()
        devolvido_antes = instance.devolvido
        emprestimo = serializer.save()

        if not devolvido_antes and emprestimo.devolvido:
            # A lógica de marcar_devolucao já está no modelo Emprestimo e usa timezone.now()
            emprestimo.marcar_devolucao()
            
            # ENVIAR EMAIL DE DEVOLUÇÃO CONFIRMADA AUTOMATICAMENTE (NÃO QUEBRA SE FALHAR)
            try:
                from .utils import enviar_email_devolucao_confirmada
                enviar_email_devolucao_confirmada(emprestimo)
            except Exception as e:
                logger.warning(f"Email de devolucao nao enviado para {emprestimo.usuario.email}: {str(e)}")

    @action(detail=False, methods=['get'], url_path='recent-reads')
    def recent_reads(self, request):
        """
        Retorna os 3 últimos livros lidos (emprestados e devolvidos) pelo usuário autenticado.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Autenticação necessária."}, status=status.HTTP_401_UNAUTHORIZED)

        # Filtra empréstimos do usuário que foram devolvidos
        # Ordena pela data de devolução em ordem decrescente (mais recente primeiro)
        # Limita aos 3 primeiros resultados
        recent_reads_queryset = Emprestimo.objects.filter(
            usuario=user,
            devolvido=True,
            data_devolucao__isnull=False # Garante que a data de devolução não seja nula
        ).order_by('-data_devolucao')[:3] # Limita aos 3 mais recentes

        serializer = self.get_serializer(recent_reads_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DevolverEmprestimoView(APIView):
    """
    Endpoint para marcar um empréstimo como devolvido.
    Dispara a notificação para o próximo da fila de reserva.
    """
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def post(self, request, pk):
        try:
            emprestimo = Emprestimo.objects.get(pk=pk)

            if emprestimo.devolvido:
                return Response({"erro": "Esse empréstimo já foi devolvido."}, status=status.HTTP_400_BAD_REQUEST)

            emprestimo.devolvido = True
            emprestimo.save() # O save do modelo Emprestimo já chama marcar_devolucao() se 'devolvido' mudar para True

            return Response({"mensagem": "Livro devolvido com sucesso e fila notificada."})

        except Emprestimo.DoesNotExist:
            return Response({"erro": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------------------------
# Views de Reservas
# -----------------------------------------------------------------------------

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar reservas.
    Admin pode ver todas. Alunos e professores veem apenas suas próprias reservas.
    """
    queryset = Reserva.objects.all().order_by('-data_reserva') # CORREÇÃO: Adicionado order_by
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, EhDonoOuAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de reservas com base no tipo de usuário.
        Alunos e professores veem apenas suas próprias reservas.
        Admin pode ver todas.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.tipo == 'admin':
                return Reserva.objects.all().order_by('-data_reserva') # CORREÇÃO: Adicionado order_by
            elif user.tipo in ['aluno', 'professor']:
                return Reserva.objects.filter(aluno=user).order_by('-data_reserva') # CORREÇÃO: Adicionado order_by
        return Reserva.objects.none()

    def perform_create(self, serializer):
        """
        Cria uma nova reserva, associando-a ao usuário logado.
        A validação de conflitos e status inicial é feita no serializer.
        DISPARA EMAILS AUTOMATICAMENTE CONFORME O TIPO DE RESERVA
        """
        reserva = serializer.save(aluno=self.request.user)
        registrar_acao(self.request.user, reserva, 'CRIACAO', descricao='Reserva criada.')
        
        # ENVIAR EMAILS AUTOMATICAMENTE CONFORME O STATUS DA RESERVA (NÃO QUEBRA SE FALHAR)
        try:
            from .utils import enviar_email_confirmacao_reserva, enviar_email_entrada_fila
            
            if reserva.status == 'aguardando_retirada':
                enviar_email_confirmacao_reserva(reserva)
            elif reserva.status == 'na_fila':
                enviar_email_entrada_fila(reserva)
        except Exception as e:
            logger.warning(f"Email de reserva nao enviado para {reserva.aluno.email}: {str(e)}")

    def perform_update(self, serializer):
        """
        Atualiza uma reserva existente e registra a ação.
        """
        reserva = serializer.save()
        registrar_acao(self.request.user, reserva, 'EDICAO', descricao='Reserva atualizada.')

    def destroy(self, request, *args, **kwargs):
        """
        Cancela (soft delete ou muda status para 'cancelada') uma reserva e registra a ação.
        """
        reserva = self.get_object()
        reserva.status = 'cancelada'
        reserva.save()
        registrar_acao(request.user, reserva, 'DESATIVACAO', descricao=f'Reserva do livro {reserva.livro.titulo} cancelada.')
        return Response({'mensagem': 'Reserva cancelada com sucesso.'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='efetivar-emprestimo', permission_classes=[IsAuthenticated, EhProfessorOuAdmin])
    def efetivar_emprestimo(self, request, pk=None):
        """
        Efetiva uma reserva (com status 'aguardando_retirada') criando um empréstimo.
        Apenas professores e administradores podem disparar esta ação.
        """
        try:
            reserva = self.get_object()
        except Reserva.DoesNotExist:
            return Response({'erro': 'Reserva não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if reserva.status != 'aguardando_retirada':
            return Response(
                {'erro': f'Esta reserva não está no status correto para efetivar empréstimo. Status atual: {reserva.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reserva.livro.disponivel:
            return Response(
                {'erro': 'O livro não está disponível para empréstimo no momento. Ele pode estar emprestado ou indisponível.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            emprestimo = Emprestimo.objects.create(
                livro=reserva.livro,
                usuario=reserva.aluno,
                data_emprestimo=timezone.now()
            )
            reserva.status = 'emprestado'
            reserva.save()
            registrar_acao(request.user, reserva, 'EDICAO', descricao=f'Reserva do livro {reserva.livro.titulo} efetivada como empréstimo.')

            return Response(
                {'mensagem': 'Reserva efetivada e empréstimo criado com sucesso.', 'emprestimo_id': emprestimo.id},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'erro': f'Erro ao criar empréstimo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------------------------------------
# Views de Notificações e Lembretes por E-mail
# -----------------------------------------------------------------------------

class LembreteDevolucaoView(APIView):
    """
    Endpoint para enviar lembretes de devolução de livros.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
        enviar_lembretes_de_devolucao()
        return Response({"mensagem": "Lembretes de devolução enviados com sucesso."})

class AvisoReservaExpirandoView(APIView):
    """
    Endpoint para enviar avisos de reservas prestes a expirar.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
        enviar_avisos_reserva_expirando()
        return Response({"mensagem": "Avisos de reserva prestes a expirar enviados com sucesso."})

class TesteEmailView(APIView):
    """
    Endpoint para testar o envio de e-mails.
    Apenas administradores podem disparar esta ação.
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
        enviar_email(
            destinatario='brivo1652@gmail.com',
            assunto='Teste de E-mail da Biblioteca Brivo',
            mensagem='Este é um teste do sistema de e-mails da biblioteca. Se você recebeu este e-mail, a configuração está funcionando corretamente.'
        )
        return Response({'mensagem': 'E-mail de teste enviado com sucesso'})

# -----------------------------------------------------------------------------
# 📧 VIEWS PARA ENVIO MANUAL DE EMAILS
# -----------------------------------------------------------------------------

class EnviarEmailManualView(APIView):
    """
    📧 Endpoint para envio manual de emails
    Permite que administradores enviem emails personalizados
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def post(self, request):
        # DADOS NECESSÁRIOS PARA ENVIO MANUAL
        destinatario = request.data.get('destinatario')
        assunto = request.data.get('assunto')
        mensagem = request.data.get('mensagem')
        
        # VALIDAÇÕES BÁSICAS
        if not destinatario or not assunto or not mensagem:
            return Response({
                'erro': 'Destinatário, assunto e mensagem são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ENVIAR EMAIL MANUAL
        from .utils import enviar_email_manual
        sucesso = enviar_email_manual(
            destinatario_email=destinatario,
            assunto_personalizado=assunto,
            mensagem_personalizada=mensagem,
            remetente_usuario=request.user
        )
        
        if sucesso:
            return Response({
                'mensagem': f'Email enviado com sucesso para {destinatario}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'erro': 'Falha ao enviar email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnviarEmailGrupoView(APIView):
    """
    📧 Endpoint para envio de emails em grupo
    Permite enviar para múltiplos usuários ou tipos específicos
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def post(self, request):
        # DADOS PARA ENVIO EM GRUPO
        tipo_usuarios = request.data.get('tipo_usuarios', [])  # ['aluno', 'professor']
        usuarios_especificos = request.data.get('usuarios_ids', [])  # [1, 2, 3]
        assunto = request.data.get('assunto')
        mensagem = request.data.get('mensagem')
        
        if not assunto or not mensagem:
            return Response({
                'erro': 'Assunto e mensagem são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # BUSCAR USUÁRIOS PARA ENVIO
        usuarios_para_envio = []
        
        # Por tipo de usuário
        if tipo_usuarios:
            usuarios_por_tipo = Usuario.objects.filter(
                ativo=True,
                tipo__in=tipo_usuarios
            )
            usuarios_para_envio.extend(usuarios_por_tipo)
        
        # Usuários específicos
        if usuarios_especificos:
            usuarios_especificos_obj = Usuario.objects.filter(
                id__in=usuarios_especificos,
                ativo=True
            )
            usuarios_para_envio.extend(usuarios_especificos_obj)
        
        if not usuarios_para_envio:
            return Response({
                'erro': 'Nenhum usuário encontrado para envio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ENVIAR EMAILS
        from .utils import enviar_email_manual
        emails_enviados = 0
        emails_falharam = 0
        
        for usuario in usuarios_para_envio:
            sucesso = enviar_email_manual(
                destinatario_email=usuario.email,
                assunto_personalizado=assunto,
                mensagem_personalizada=mensagem,
                remetente_usuario=request.user
            )
            
            if sucesso:
                emails_enviados += 1
            else:
                emails_falharam += 1
        
        return Response({
            'mensagem': f'Envio concluído: {emails_enviados} enviados, {emails_falharam} falharam',
            'emails_enviados': emails_enviados,
            'emails_falharam': emails_falharam
        }, status=status.HTTP_200_OK)

class EnviarEmailsPredefinidosView(APIView):
    """
    📧 Endpoint para disparar emails automáticos predefinidos
    Permite testar e enviar emails automáticos manualmente
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def post(self, request):
        tipo_email = request.data.get('tipo_email')
        usuario_id = request.data.get('usuario_id')
        
        if not tipo_email:
            return Response({
                'erro': 'Tipo de email é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # IMPORTAR FUNÇÕES DE EMAIL
        from .utils import (
            enviar_email_boas_vindas,
            enviar_email_novos_livros,
            enviar_email_dicas_leitura,
            enviar_email_convite_evento
        )
        
        try:
            # EMAIL DE BOAS-VINDAS
            if tipo_email == 'boas_vindas' and usuario_id:
                usuario = Usuario.objects.get(id=usuario_id)
                sucesso = enviar_email_boas_vindas(usuario)
                
            # EMAIL DE NOVOS LIVROS
            elif tipo_email == 'novos_livros':
                usuarios = Usuario.objects.filter(ativo=True, tipo__in=['aluno', 'professor'])
                livros_novos = Livro.objects.filter(ativo=True).order_by('-id')[:3]
                enviar_email_novos_livros(usuarios, livros_novos)
                sucesso = True
                
            # EMAIL DE DICAS DE LEITURA
            elif tipo_email == 'dicas_leitura':
                usuarios = Usuario.objects.filter(ativo=True, tipo__in=['aluno', 'professor'])
                dica_titulo = "Faça anotações enquanto lê"
                dica_conteudo = "Anotar ideias importantes ajuda na compreensão e memorização."
                livro_sugerido = Livro.objects.filter(ativo=True).first()
                enviar_email_dicas_leitura(usuarios, dica_titulo, dica_conteudo, livro_sugerido)
                sucesso = True
                
            # EMAIL DE CONVITE PARA EVENTO
            elif tipo_email == 'convite_evento':
                usuarios = Usuario.objects.filter(ativo=True, tipo__in=['aluno', 'professor'])
                nome_evento = "Semana Literária"
                data_evento = "25/12/2024"
                horario = "14h às 17h"
                local = "Biblioteca da Escola"
                programacao = ["Roda de leitura", "Contação de histórias", "Troca de livros"]
                enviar_email_convite_evento(usuarios, nome_evento, data_evento, horario, local, programacao)
                sucesso = True
                
            else:
                return Response({
                    'erro': 'Tipo de email inválido ou dados insuficientes'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if sucesso:
                return Response({
                    'mensagem': f'Email predefinido "{tipo_email}" enviado com sucesso'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'erro': 'Falha ao enviar email predefinido'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Usuario.DoesNotExist:
            return Response({
                'erro': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'erro': f'Erro interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListarTiposEmailView(APIView):
    """
    📧 Endpoint para listar tipos de emails disponíveis
    Retorna todos os tipos de emails que podem ser enviados
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
        tipos_email = {
            'emails_automaticos': {
                'boas_vindas': {
                    'nome': 'Email de Boas-vindas',
                    'descricao': 'Enviado quando um novo usuário é criado',
                    'requer_usuario': True,
                    'automatico': True
                },
                'confirmacao_reserva': {
                    'nome': 'Confirmação de Reserva',
                    'descricao': 'Enviado quando uma reserva é criada',
                    'automatico': True
                },
                'emprestimo_confirmado': {
                    'nome': 'Empréstimo Confirmado',
                    'descricao': 'Enviado quando um empréstimo é registrado',
                    'automatico': True
                },
                'devolucao_confirmada': {
                    'nome': 'Devolução Confirmada',
                    'descricao': 'Enviado quando um livro é devolvido',
                    'automatico': True
                }
            },
            'emails_predefinidos': {
                'novos_livros': {
                    'nome': 'Novos Livros',
                    'descricao': 'Notifica sobre novos livros adicionados',
                    'manual': True
                },
                'dicas_leitura': {
                    'nome': 'Dicas de Leitura',
                    'descricao': 'Envia dicas educacionais semanais',
                    'manual': True
                },
                'convite_evento': {
                    'nome': 'Convite para Evento',
                    'descricao': 'Convida para eventos da biblioteca',
                    'manual': True
                }
            },
            'emails_manuais': {
                'individual': {
                    'nome': 'Email Individual',
                    'descricao': 'Envio personalizado para um usuário',
                    'endpoint': '/api/emails/enviar-manual/'
                },
                'grupo': {
                    'nome': 'Email em Grupo',
                    'descricao': 'Envio para múltiplos usuários',
                    'endpoint': '/api/emails/enviar-grupo/'
                }
            }
        }
        
        return Response({
            'tipos_email': tipos_email,
            'total_tipos': sum(len(categoria) for categoria in tipos_email.values())
        }, status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------
# Views de Dashboard e Estatísticas
# -----------------------------------------------------------------------------

class DashboardAdminView(APIView):
    """
    Endpoint para o dashboard administrativo com estatísticas da biblioteca.
    Apenas administradores podem acessar.
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
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

        total_livros = Livro.objects.count()
        livros_ativos = Livro.objects.filter(ativo=True).count()
        livros_inativos = Livro.objects.filter(ativo=False).count()

        total_usuarios_ativos_geral = Usuario.objects.filter(ativo=True).count()

        total_usuarios_filtrados = Usuario.objects.filter(ativo=True, **filtro_usuarios).count()

        total_alunos = Usuario.objects.filter(ativo=True, tipo='aluno', **filtro_usuarios).count()
        total_professores = Usuario.objects.filter(ativo=True, tipo='professor', **filtro_usuarios).count()
        total_admins = Usuario.objects.filter(ativo=True, tipo='admin', **filtro_usuarios).count()

        hoje = date.today()
        reservas_hoje = Reserva.objects.filter(
            data_reserva__date=hoje,
            status__in=['na_fila', 'aguardando_retirada', 'emprestado']
        ).count()

        reservas_na_fila = Reserva.objects.filter(status='na_fila', **filtro_reservas).count()
        reservas_aguardando_retirada = Reserva.objects.filter(status='aguardando_retirada', **filtro_reservas).count()
        reservas_emprestadas = Reserva.objects.filter(status='emprestado', **filtro_reservas).count()
        reservas_concluidas = Reserva.objects.filter(status='concluida', **filtro_reservas).count()
        reservas_expiradas = Reserva.objects.filter(status='expirada', **filtro_reservas).count()
        reservas_canceladas = Reserva.objects.filter(status='cancelada', **filtro_reservas).count()

        total_emprestimos_geral = Emprestimo.objects.count()

        emprestimos_ativos = Emprestimo.objects.filter(devolvido=False, **filtro_emprestimos).count()
        emprestimos_concluidos = Emprestimo.objects.filter(devolvido=True, **filtro_emprestimos).count()

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

        # --- NOVOS DADOS PARA O DASHBOARD ---

        # Top Livros Mais Emprestados (considerando apenas empréstimos concluídos ou ativos)
        # Agrupa por livro e conta o número de empréstimos, depois pega os 5 primeiros
        top_livros_emprestados = Emprestimo.objects.filter(
            livro__ativo=True # Considera apenas livros ativos
        ).values('livro__titulo').annotate(
            total_emprestimos=Count('id')
        ).order_by('-total_emprestimos')[:5] # Top 5 livros

        # Reservas por Gênero/Categoria (assumindo que Livro tem um campo 'genero')
        # Agrupa por gênero do livro e conta o número de reservas
        reservas_por_genero = Reserva.objects.filter(
            livro__ativo=True, # Considera apenas livros ativos
            livro__genero__isnull=False # Garante que o gênero não seja nulo
        ).values('livro__genero').annotate(
            total_reservas=Count('id')
        ).order_by('-total_reservas')

        return Response({
            'filtro_aplicado': periodo or 'todos',
            'livros': {
                'total': total_livros,
                'ativos': livros_ativos,
                'inativos': livros_inativos,
            },
            'usuarios': {
                'total_geral_ativos': total_usuarios_ativos_geral,
                'total_filtrado': total_usuarios_filtrados,
                'alunos': total_alunos,
                'total_professores': total_professores,
                'admins': total_admins,
            },
            'reservas': {
                'hoje': reservas_hoje,
                'na_fila': reservas_na_fila,
                'aguardando_retirada': reservas_aguardando_retirada,
                'emprestadas': reservas_emprestadas,
                'concluidas': reservas_concluidas,
                'expiradas': reservas_expiradas,
                'canceladas': reservas_canceladas,
            },
            'emprestimos': {
                'total_geral': total_emprestimos_geral,
                'ativos': emprestimos_ativos,
                'devolvidos': emprestimos_concluidos,
            },
            'graficos': {
                'emprestimos_por_mes': list(emprestimos_por_mes),
                'reservas_por_mes': list(reservas_por_mes),
                'top_livros_emprestados': list(top_livros_emprestados),
                'reservas_por_genero': list(reservas_por_genero),
            }
        })

# -----------------------------------------------------------------------------
# Views de Alertas do Sistema
# -----------------------------------------------------------------------------

class AlertaSistemaViewSet(viewsets.ModelViewSet):
    """
    Viewset para gerenciar Alertas do Sistema.
    Apenas administradores podem criar, listar, atualizar e deletar alertas.
    """
    queryset = AlertaSistema.objects.all().order_by('-data_criacao') # Adicionado order_by para consistência
    serializer_class = AlertaSistemaSerializer
    permission_classes = [IsAuthenticated, EhAdmin] # Apenas admins podem gerenciar alertas

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'resolvido', 'visibilidade']
    search_fields = ['titulo', 'mensagem']
    ordering_fields = ['data_criacao', 'tipo', 'expira_em', 'data_publicacao']
    ordering = ['-data_criacao'] # Ordenação padrão: mais novos primeiro

    def get_queryset(self):
        """
        Retorna o queryset de alertas.
        Admins podem ver todos os alertas.
        """
        queryset = super().get_queryset()
        return queryset

    def perform_create(self, serializer):
        """
        Cria um novo alerta, registra a ação e, se for público e com envio de e-mail,
        dispara a notificação.
        """
        alerta = serializer.save()
        registrar_acao(self.request.user, alerta, 'CRIACAO', descricao=f'Alerta "{alerta.titulo}" criado.')

        # [INTEGRAÇÃO BACKEND] Disparar envio de e-mail/notificação se for público e marcado para envio
        # A lógica para enviar o email e marcar email_enviado=True será feita na função utilitária
        # A verificação de `alerta.email_enviado` aqui é para o caso de o admin já marcar como enviado
        # na criação, mas a função utilitária fará a marcação final após o envio.
        if alerta.visibilidade == 'publico' and alerta.email_enviado:
            enviar_notificacao_alerta_publico(alerta.id)
            print(f"Disparando notificação para o alerta público: {alerta.titulo}")


    def perform_update(self, serializer):
        """
        Atualiza um alerta existente, registra a ação e, se houver mudança relevante
        para alertas públicos, dispara a notificação.
        """
        # Obter o estado original do objeto antes da atualização
        original_alerta = self.get_object()

        alerta = serializer.save() # Salva as alterações
        registrar_acao(self.request.user, alerta, 'EDICAO', descricao=f'Alerta "{alerta.titulo}" editado.')

        # [INTEGRAÇÃO BACKEND] Lógica para disparar envio de e-mail/notificação em caso de atualização
        should_send_email = False

        # Cenário 1: Alerta se tornou público e ainda não foi enviado
        if (original_alerta.visibilidade == 'admin_only' and alerta.visibilidade == 'publico' and not alerta.email_enviado):
            should_send_email = True
        # Cenário 2: Alerta já era público, não foi enviado e o admin o marcou para enviar (ou re-enviar)
        elif (alerta.visibilidade == 'publico' and not original_alerta.email_enviado and alerta.email_enviado):
            should_send_email = True
        # Cenário 3: Alerta já era público, não foi enviado e foi atualizado de alguma forma (re-tentar envio)
        # Este cenário pode ser mais agressivo, dependendo da sua necessidade.
        # Por enquanto, vamos focar nos cenários 1 e 2.
        # elif (alerta.visibilidade == 'publico' and not alerta.email_enviado):
        #     should_send_email = True

        if should_send_email:
            enviar_notificacao_alerta_publico(alerta.id)
            print(f"Disparando notificação para o alerta público (atualizado): {alerta.titulo}")


    def perform_destroy(self, instance):
        """
        Deleta um alerta e registra a ação.
        """
        registrar_acao(self.request.user, instance, 'DESATIVACAO', descricao=f'Alerta "{instance.titulo}" deletado.')
        instance.delete()

    @action(detail=False, methods=['get'], url_path='summary', permission_classes=[IsAuthenticated, EhAdmin])
    def get_alert_summary(self, request):
        """
        Retorna um resumo das contagens de alertas para a tela de dashboard/alertas.
        Inclui contagens de pendentes, alta prioridade e resolvidos.
        """
        # Alertas pendentes (não resolvidos e não expirados ou expirados mas ainda não marcados como resolvidos)
        pendentes_queryset = AlertaSistema.objects.filter(resolvido=False)

        total_pendentes = pendentes_queryset.count()
        alta_prioridade = pendentes_queryset.filter(tipo__in=['critical', 'error']).count()
        total_resolvidos = AlertaSistema.objects.filter(resolvido=True).count()

        return Response({
            'total_pendentes': total_pendentes,
            'alta_prioridade': alta_prioridade,
            'total_resolvidos': total_resolvidos,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-resolved', permission_classes=[IsAuthenticated, EhAdmin])
    def mark_resolved(self, request, pk=None):
        """
        Marca um alerta específico como resolvido.
        """
        try:
            alerta = self.get_object()
            if alerta.resolvido:
                return Response({'mensagem': 'Alerta já está resolvido.'}, status=status.HTTP_200_OK)

            alerta.resolvido = True
            alerta.resolvido_em = timezone.now()
            alerta.save()
            registrar_acao(request.user, alerta, 'EDICAO', descricao=f'Alerta "{alerta.titulo}" marcado como resolvido.')
            return Response({'mensagem': 'Alerta marcado como resolvido com sucesso.'}, status=status.HTTP_200_OK)
        except AlertaSistema.DoesNotExist:
            return Response({'erro': 'Alerta não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PublicAlertaSistemaListView(generics.ListAPIView):
    """
    View para listar alertas do sistema públicos e ativos.
    Qualquer usuário autenticado pode acessar.
    """
    serializer_class = AlertaSistemaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'mensagem']
    ordering_fields = ['data_publicacao', 'tipo']
    ordering = ['-data_publicacao'] # Ordena pelos mais recentes primeiro

    def get_queryset(self):
        """
        Retorna apenas alertas públicos, não resolvidos,
        com data de publicação no passado/presente e data de expiração no futuro ou nula.
        """
        now = timezone.now()
        queryset = AlertaSistema.objects.filter(
            visibilidade='publico',
            resolvido=False,
            data_publicacao__lte=now
        ).filter(
            Q(expira_em__isnull=True) | Q(expira_em__gt=now)
        ).order_by('-data_publicacao') # CORREÇÃO: Adicionado order_by explícito para consistência
        return queryset


# ... (restante do código)

# -----------------------------------------------------------------------------
# Views de Relatórios Pedagógicos
#from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F, Q
from django.utils import timezone # Importação essencial para lidar com fusos horários
from datetime import timedelta, date
from django.db.models import Count
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Replace with your actual models and permissions
from .models import Livro, Usuario, Emprestimo, Reserva
from .permissions import EhAdmin
from django.utils import timezone

# Importações de modelos e serializers
from .models import Livro, Usuario, Emprestimo, Reserva, AlertaSistema
from .serializers import LivroSerializer, UsuarioSerializer, EmprestimoSerializer, ReservaSerializer, AlertaSistemaSerializer
from .permissions import EhDonoOuAdmin, EhAdmin, EhProfessorOuAdmin
from .utils import (
    enviar_email,
    enviar_lembretes_de_devolucao,
    notificar_primeiro_da_fila,
    enviar_avisos_reserva_expirando,
    registrar_acao,
    enviar_notificacao_alerta_publico
)

# Importação do Simple JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


# -----------------------------------------------------------------------------
# Views de Relatórios Pedagógicos
# -----------------------------------------------------------------------------

class RelatoriosPedagogicosView(APIView):
    """
    Endpoint para gerar relatórios pedagógicos com a estrutura correta para o frontend.
    Apenas administradores podem acessar.
    """
    permission_classes = [IsAuthenticated, EhAdmin]

    def get(self, request):
        agora = timezone.now()
        
        # Estatísticas (agrupadas para corresponder à estrutura do frontend)
        total_alunos = Usuario.objects.filter(ativo=True, tipo='aluno').count()
        livros_emprestados_ativos = Emprestimo.objects.filter(devolvido=False).count()
        reservas_ativas_ativas = Reserva.objects.filter(status__in=['na_fila', 'aguardando_retirada']).count()
        total_emprestimos_concluidos = Emprestimo.objects.filter(devolvido=True).count()
        media_leitura_aluno = total_emprestimos_concluidos / total_alunos if total_alunos > 0 else 0

        estatisticas_data = {
            'total_alunos': total_alunos,
            'livros_emprestados': livros_emprestados_ativos,
            'reservas_ativas': reservas_ativas_ativas,
            'media_leitura': round(media_leitura_aluno, 2),
        }

        # Top 10 Alunos Mais Ativos (Empréstimos)
        alunos_mais_ativos = Usuario.objects.filter(
            tipo='aluno',
            ativo=True
        ).annotate(
            # Corrigido para usar 'emprestimos' (plural) conforme o seu models.py
            total_emprestimos=Count('emprestimos') 
        ).order_by('-total_emprestimos')[:10]
        
        alunos_data = [{
            'id': aluno.id,
            'nome': aluno.nome,
            'curso': aluno.turma,
            'ra': aluno.ra,
            'total_emprestimos': aluno.total_emprestimos,
        } for aluno in alunos_mais_ativos]

        # Livros Mais Populares
        populares = Livro.objects.filter(
            ativo=True
        ).annotate(
            # CORRIGIDO: O nome do relacionamento é 'emprestimos', não 'emprestimo'
            total_emprestimos=Count('emprestimos'),
            total_reservas=Count('reservas')
        ).annotate(
            # CORRIGIDO: O nome do relacionamento é 'emprestimos', não 'emprestimo'
            popularidade=Count('emprestimos') + Count('reservas')
        ).order_by('-popularidade')[:5]

        livros_data = [{
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'total_emprestimos': livro.total_emprestimos,
            'total_reservas': livro.total_reservas,
            'popularidade': livro.popularidade,
        } for livro in populares]
        
        # Insights Pedagógicos (exemplo de dados estáticos para o frontend)
        insights_data = [
            {
                'titulo': 'Pico de Leitura',
                'descricao': f"O pico de empréstimos acontece no horário do almoço. Considere promover livros em campanhas nesse período para aumentar a visibilidade."
            },
            {
                'titulo': 'Engajamento de Reservas',
                'descricao': f"Há {reservas_ativas_ativas} reservas ativas. Isso mostra um alto interesse em livros que podem ter poucos exemplares disponíveis."
            },
            {
                'titulo': 'Diversidade de Gêneros',
                'descricao': 'A distribuição de gêneros mostra que fantasia e ficção científica são os mais populares. Considere adquirir mais livros desses gêneros para atender à demanda.'
            }
        ]
        
        return Response({
            'estatisticas': estatisticas_data,
            'alunos_mais_ativos': alunos_data,
            'livros_mais_populares': livros_data,
            'insights': insights_data,
        })