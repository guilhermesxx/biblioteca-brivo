# brivo/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth import get_user_model


# Criar o modelo de log abaixo
class HistoricoAcao(models.Model):
    # O campo 'usuario' já está definido uma vez, a linha duplicada foi removida.
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
    disponivel = models.BooleanField(default=True)
    capa = models.URLField(blank=True, null=True)
    descricao = models.TextField(null=True, blank=True)

    ativo = models.BooleanField(default=True) # campo para soft delete
    
    objects = LivroQuerySet.as_manager() # Ativa a queryset customizada

    def __str__(self):
        return self.titulo


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
        ('na_fila', 'Na Fila'),
        ('aguardando_confirmacao', 'Aguardando Confirmação'),
        ('expirado', 'Expirado'),
        ('concluido', 'Concluído'),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='reservas')
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    data_reserva = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='na_fila')
    notificado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Reserva de {self.livro.titulo} por {self.aluno.nome} ({self.status})'


class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    devolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"Empréstimo de {self.livro.titulo} para {self.usuario.nome}"

    def save(self, *args, **kwargs):
        # Verifica se foi marcado como devolvido
        if self.pk is not None:
            original = Emprestimo.objects.get(pk=self.pk)
            if not original.devolvido and self.devolvido:
                self.data_devolucao = timezone.now()
                self.livro.disponivel = True
                self.livro.save()
                self._notificar_reserva()
        elif not self.devolvido:
            # Novo empréstimo → livro fica indisponível
            self.livro.disponivel = False
            self.livro.save()

        super().save(*args, **kwargs)

    def marcar_devolucao(self):
        """Método para uso explícito"""
        if not self.devolvido:
            self.devolvido = True
            self.data_devolucao = timezone.now()
            self.save()

    def _notificar_reserva(self):
        proxima_reserva = Reserva.objects.filter(
            livro=self.livro,
            status='na_fila'
        ).order_by('data_reserva').first()

        if proxima_reserva:
            proxima_reserva.status = 'aguardando_confirmacao'
            proxima_reserva.notificado_em = timezone.now()
            proxima_reserva.save()
