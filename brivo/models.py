from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError 


# Define a constante para o limite de estoque baixo
ESTOQUE_BAIXO_LIMITE = 3 # Exemplo: 3 exemplares restantes ou menos

# Criar o modelo de log abaixo
class HistoricoAcao(models.Model):
    usuario = models.ForeignKey('brivo.Usuario', on_delete=models.SET_NULL, null=True)
    
    ACAO_CHOICES = [
        ('CRIACAO', 'Criação'),
        ('EDICAO', 'Edição'),
        ('DESATIVACAO', 'Desativação'),
    ]

    objeto_tipo = models.CharField(max_length=50)
    objeto_id = models.PositiveIntegerField()
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario} fez {self.acao} em {self.objeto_tipo} (ID {self.objeto_id})"

# Gerenciador customizado de usuário
class CustomUserManager(BaseUserManager):
    def create_user(self, ra, nome, email, turma, tipo, password=None):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        if not ra:
            raise ValueError("O RA é obrigatório.")
        if not nome:
            raise ValueError("O nome é obrigatório.")
        if not turma:
            raise ValueError("A turma é obrigatória.")
        if not tipo:
            raise ValueError("O tipo de usuário é obrigatório.")

        user = self.model(
            ra=ra,
            nome=nome,
            email=self.normalize_email(email),
            turma=turma,
            tipo=tipo,
            is_active=True,
            is_staff=(tipo == "admin"), # Define is_staff com base no tipo
            is_superuser=(tipo == "admin"), # Define is_superuser com base no tipo
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, ra, nome, email, turma="ADM", tipo="admin", password=None):
        # Chama create_user com tipo "admin" para criar um superusuário
        return self.create_user(
            ra=ra,
            nome=nome,
            email=email,
            turma=turma,
            tipo=tipo, # Garante que o tipo seja 'admin' para superusuários
            password=password
        )

class UsuarioQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(ativo=True)

# Combina o CustomUserManager com a Custom QuerySet
class UsuarioManager(CustomUserManager.from_queryset(UsuarioQuerySet)):
    pass

class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('admin', 'Administrador'),
    ]

    ra = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    turma = models.CharField(max_length=20)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES) # Campo 'tipo' para diferenciar usuários
    data_cadastro = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Usado pelo Django Admin
    is_superuser = models.BooleanField(default=False) # Usado pelo Django Admin e permissões

    USERNAME_FIELD = 'email' # Campo usado para login
    REQUIRED_FIELDS = ['ra', 'nome', 'turma', 'tipo'] # Campos obrigatórios na criação de usuário

    ativo = models.BooleanField(default=True) # Campo para soft delete

    objects = UsuarioManager() # Gerenciador customizado para o modelo Usuario

    def __str__(self):
        return self.nome

    # Métodos para compatibilidade com o sistema de permissões do Django
    def has_perm(self, perm, obj=None):
        return self.is_superuser # Superusuário tem todas as permissões

    def has_module_perms(self, app_label):
        return self.is_superuser # Superusuário tem permissões em todos os módulos


class LivroQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(ativo=True)

class Livro(models.Model):
    TIPO_LIVRO_CHOICES = [
        ('fisico', 'Físico'),
        ('pdf', 'PDF'),
    ]

    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    editora = models.CharField(max_length=255, null=True, blank=True)
    data_publicacao = models.DateField()
    numero_paginas = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=6, choices=TIPO_LIVRO_CHOICES)
    genero = models.CharField(max_length=100, null=True, blank=True)
    
    # NOVOS CAMPOS PARA CONTROLE DE ESTOQUE
    quantidade_total = models.IntegerField(default=1, help_text="Número total de exemplares deste livro.")
    quantidade_emprestada = models.IntegerField(default=0, help_text="Número de exemplares atualmente emprestados.")
    # O campo 'disponivel' como BooleanField foi removido, agora é uma propriedade calculada.
    
    capa = models.URLField(blank=True, null=True)
    descricao = models.TextField(null=True, blank=True)

    ativo = models.BooleanField(default=True, help_text="Indica se o livro está ativo no sistema.") # campo para soft delete
    
    objects = LivroQuerySet.as_manager() # Ativa a queryset customizada

    def __str__(self):
        return self.titulo

    @property
    def quantidade_disponivel(self):
        """Calcula a quantidade de exemplares disponíveis."""
        return self.quantidade_total - self.quantidade_emprestada

    @property
    def disponivel(self):
        """Retorna True se há pelo menos um exemplar disponível."""
        return self.quantidade_disponivel > 0

    def save(self, *args, **kwargs):
        # Garante que quantidade_emprestada não seja maior que quantidade_total
        if self.quantidade_emprestada > self.quantidade_total:
            self.quantidade_emprestada = self.quantidade_total
        
        # Garante que quantidade_emprestada não seja menor que zero
        if self.quantidade_emprestada < 0:
            self.quantidade_emprestada = 0

        super().save(*args, **kwargs)
        # Chama a função de verificação de estoque APÓS o save do livro
        self._check_and_create_low_stock_alert() 

    def _check_and_create_low_stock_alert(self):
        """
        Verifica se o estoque do livro está baixo/esgotado e cria/resolve alertas se necessário.
        """
        # Importa AlertaSistema aqui para evitar circular import
        from .models import AlertaSistema 
        
        # Alerta de Estoque Baixo
        if self.quantidade_disponivel > 0 and self.quantidade_disponivel <= ESTOQUE_BAIXO_LIMITE:
            # Verifica se já existe um alerta *pendente* de estoque baixo para este livro
            existing_low_stock_alert = AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Estoque Baixo",
                resolvido=False,
                tipo='warning',
                visibilidade='admin_only' # Alertas de estoque são apenas para o admin
            ).first()

            if not existing_low_stock_alert:
                AlertaSistema.objects.create(
                    titulo=f"Livro: {self.titulo} - Estoque Baixo",
                    mensagem=f"O livro '{self.titulo}' tem apenas {self.quantidade_disponivel} exemplares disponíveis.",
                    tipo='warning',
                    visibilidade='admin_only' # Alertas de estoque são apenas para o admin
                )
                print(f"Alerta de estoque baixo criado para o livro: {self.titulo}")
            else:
                # Atualiza a mensagem se o alerta já existe mas a quantidade mudou
                if existing_low_stock_alert.mensagem != f"O livro '{self.titulo}' tem apenas {self.quantidade_disponivel} exemplares disponíveis.":
                    existing_low_stock_alert.mensagem = f"O livro '{self.titulo}' tem apenas {self.quantidade_disponivel} exemplares disponíveis."
                    existing_low_stock_alert.save(update_fields=['mensagem'])

            # Garante que o alerta de "Esgotado" esteja resolvido se o estoque não é zero
            AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Esgotado",
                resolvido=False
            ).update(resolvido=True, resolvido_em=timezone.now())

        # Alerta de Livro Esgotado
        elif self.quantidade_disponivel == 0:
            # Verifica se já existe um alerta *pendente* de livro esgotado para este livro
            existing_out_of_stock_alert = AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Esgotado",
                resolvido=False,
                tipo='critical',
                visibilidade='admin_only' # Alertas de estoque são apenas para o admin
            ).first()

            if not existing_out_of_stock_alert:
                AlertaSistema.objects.create(
                    titulo=f"Livro: {self.titulo} - Esgotado",
                    mensagem=f"O livro '{self.titulo}' não possui exemplares disponíveis para empréstimo.",
                    tipo='critical',
                    visibilidade='admin_only' # Alertas de estoque são apenas para o admin
                )
                print(f"Alerta de livro esgotado criado para o livro: {self.titulo}")
            
            # Garante que o alerta de "Estoque Baixo" esteja resolvido se o livro está esgotado
            AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Estoque Baixo",
                resolvido=False
            ).update(resolvido=True, resolvido_em=timezone.now())

        # Resolve alertas de estoque baixo/esgotado se o estoque está acima do limite
        elif self.quantidade_disponivel > ESTOQUE_BAIXO_LIMITE:
            AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Estoque Baixo",
                resolvido=False
            ).update(resolvido=True, resolvido_em=timezone.now())
            
            AlertaSistema.objects.filter(
                titulo__icontains=f"Livro: {self.titulo} - Esgotado",
                resolvido=False
            ).update(resolvido=True, resolvido_em=timezone.now())
            print(f"Alertas de estoque baixo/esgotado resolvidos para o livro: {self.titulo}")


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='imagens_categoria/', null=True, blank=True)

    def __str__(self):
        return self.nome


class Configuracao(models.Model):
    nome_app = models.CharField(max_length=100, default="Biblioteca Brivo")
    logo = models.ImageField(upload_to='logos_app/', null=True, blank=True)

    def __str__(self):
        return "Configuração Geral"


class Reserva(models.Model):
    STATUS_CHOICES = [
        ('na_fila', 'Na Fila'), # Para reservas sem data/hora definida, aguardando um livro
        ('aguardando_retirada', 'Aguardando Retirada'), # Nova: Para reservas com data/hora definida
        ('emprestado', 'Emprestado'), # Novo: Quando a reserva é convertida em empréstimo
        ('expirada', 'Expirada'), # Ajuste de nome para 'expirado'
        ('cancelada', 'Cancelada'), # Novo: Para reservas que foram canceladas
        ('concluida', 'Concluída'), # Quando o ciclo de reserva/empréstimo termina (livro devolvido)
    ]

    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='reservas')
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    data_reserva = models.DateTimeField(auto_now_add=True) # Data de criação da reserva
    
    # Novos campos para a data e hora de retirada prevista
    data_retirada_prevista = models.DateField(null=True, blank=True)
    hora_retirada_prevista = models.TimeField(null=True, blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='na_fila')
    notificado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Reserva de {self.livro.titulo} por {self.aluno.nome} ({self.status})'

    # Adicionar uma validação básica para garantir que data_retirada_prevista e hora_retirada_prevista sejam preenchidos juntos se o status for 'aguardando_retirada'
    def clean(self):
        if self.status == 'aguardando_retirada' and (self.data_retirada_prevista is None or self.hora_retirada_prevista is None):
            from django.core.exceptions import ValidationError
            raise ValidationError("Data e hora de retirada previstas são obrigatórias para o status 'Aguardando Retirada'.")
        
        # Se a data de retirada prevista for no passado, e o status ainda não for expirado, pode ser um erro
        if self.data_retirada_prevista and self.data_retirada_prevista < timezone.localdate() and self.status == 'aguardando_retirada':
            # Considerar automaticamente expirar ou exigir ação manual
            pass # A lógica de expiração pode ser um cron job, por exemplo.

    # O método save() pode ser sobrescrito para adicionar lógica, mas faremos isso no ViewSet/Serializer para validação.


class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='emprestimos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='emprestimos')
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    devolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"Empréstimo de {self.livro.titulo} para {self.usuario.nome}"

    def save(self, *args, **kwargs):
        is_new_loan = self.pk is None # Verifica se é um novo empréstimo

        # Se é um novo empréstimo, decrementa a quantidade disponível e incrementa a emprestada
        if is_new_loan:
            # Antes de salvar o empréstimo, verifica se há exemplares disponíveis
            if self.livro.quantidade_disponivel > 0:
                self.livro.quantidade_emprestada += 1
                self.livro.save() # Isso vai disparar o _check_and_create_low_stock_alert do Livro
            else:
                # Se não há exemplares disponíveis, impede o empréstimo
                raise ValidationError("Não há exemplares disponíveis para este livro.")

        super().save(*args, **kwargs) # Salva o empréstimo

        # Lógica para gerenciar a quantidade de livros e alertas APÓS o save
        if not is_new_loan: # Se é uma atualização de um empréstimo existente
            original = Emprestimo.objects.get(pk=self.pk)
            if not original.devolvido and self.devolvido:
                # Livro foi devolvido: decrementa a quantidade emprestada
                self.livro.quantidade_emprestada -= 1
                self.livro.save() # Isso vai disparar o _check_and_create_low_stock_alert do Livro
                self.data_devolucao = timezone.now()
                self._notificar_reserva() # Chama a notificação para o próximo da fila
                # Se o empréstimo foi concluído e era resultado de uma reserva, marque a reserva como concluída
                try:
                    reserva_associada = Reserva.objects.get(livro=self.livro, aluno=self.usuario, status='emprestado')
                    reserva_associada.status = 'concluida'
                    reserva_associada.save()
                except Reserva.DoesNotExist:
                    pass

    def marcar_devolucao(self):
        """Método para uso explícito"""
        if not self.devolvido:
            self.devolvido = True
            self.data_devolucao = timezone.now()
            self.save()

    def _notificar_reserva(self):
        # Esta lógica é para notificar o próximo da fila quando um livro é devolvido.
        # A reserva permanece 'na_fila' até que o usuário agende a retirada.
        proxima_reserva = Reserva.objects.filter(
            livro=self.livro,
            status='na_fila'
        ).order_by('data_reserva').first()

        if proxima_reserva:
            # Marca a reserva como notificada. A notificação real (e-mail)
            # deve ser disparada por um processo separado que verifica 'notificado_em'.
            # O status da reserva permanece 'na_fila' até que o usuário agende a retirada.
            proxima_reserva.notificado_em = timezone.now()
            proxima_reserva.save()
            # Opcional: Chamar a função de utilidade para enviar o e-mail aqui
            # from .utils import notificar_primeiro_da_fila
            # notificar_primeiro_da_fila(proxima_reserva) # Descomente e implemente em utils.py se desejar notificação imediata


# NOVO: Modelo para Alertas do Sistema
class AlertaSistema(models.Model):
    TIPO_ALERTA_CHOICES = [
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
        ('critical', 'Crítico'),
    ]

    VISIBILIDADE_CHOICES = [
        ('admin_only', 'Apenas para Administrador'),
        ('publico', 'Público (para Alunos e Professores)'),
    ]

    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_ALERTA_CHOICES, default='info')
    data_criacao = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False) # Indica se o alerta foi resolvido
    resolvido_em = models.DateTimeField(null=True, blank=True) # Quando foi resolvido
    
    # Novos campos para visibilidade e agendamento
    visibilidade = models.CharField(max_length=20, choices=VISIBILIDADE_CHOICES, default='admin_only', 
                                    help_text="Define quem pode ver este alerta/notificação.")
    data_publicacao = models.DateTimeField(null=True, blank=True, 
                                           help_text="Data e hora em que a notificação deve ser publicada (se 'Público').")
    expira_em = models.DateTimeField(null=True, blank=True, # Renomeado de data_expiracao para expira_em
                                          help_text="Data e hora em que a notificação deve expirar e deixar de ser visível.")
    email_enviado = models.BooleanField(default=False, 
                                        help_text="Indica se o e-mail desta notificação pública já foi enviado.")


    class Meta:
        verbose_name = "Alerta do Sistema"
        verbose_name_plural = "Alertas do Sistema"
        ordering = ['-data_criacao'] # Ordena os alertas do mais novo para o mais antigo

    def __str__(self):
        status_text = "Resolvido" if self.resolvido else "Pendente"
        visibilidade_text = self.get_visibilidade_display()
        return f"[{self.get_tipo_display()}] {self.titulo} ({status_text} - {visibilidade_text})"

    def save(self, *args, **kwargs):
        # Se o alerta for marcado como resolvido, define a data de resolução
        if self.pk is not None: # Verifica se é uma atualização de um objeto existente
            original = AlertaSistema.objects.get(pk=self.pk)
            if not original.resolvido and self.resolvido:
                self.resolvido_em = timezone.now()
        
        # Lógica para publicação e expiração automática de alertas/notificações
        now = timezone.now()
        
        # Se data_publicacao está no futuro, o alerta não deve estar ativo ainda
        if self.data_publicacao and self.data_publicacao > now and not self.resolvido:
            # Poderíamos ter um campo 'ativo' ou 'publicado' para controlar isso,
            # mas por enquanto, a lógica de exibição no frontend/API deve considerar data_publicacao.
            pass 
        
        # Se expira_em está no passado e o alerta não está resolvido, marca como resolvido
        if self.expira_em and self.expira_em < now and not self.resolvido:
            self.resolvido = True
            self.resolvido_em = now # Define a data de resolução se expirou

        super().save(*args, **kwargs)
