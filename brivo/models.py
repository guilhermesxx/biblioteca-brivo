from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Gerenciador customizado de usuário
class CustomUserManager(BaseUserManager):
    def create_user(self, ra, nome, email, turma, tipo, senha=None):
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
            is_staff=(tipo == "admin"),
            is_superuser=(tipo == "admin"),
        )
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, ra, nome, email, turma="ADM", tipo="admin", senha=None):
        return self.create_user(
            ra=ra,
            nome=nome,
            email=email,
            turma=turma,
            tipo=tipo,
            senha=senha
        )


# Modelo de Usuário Customizado
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
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['ra', 'nome', 'turma', 'tipo']

    objects = CustomUserManager()

    def __str__(self):
        return self.nome


# Modelo de Livro
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
    disponivel = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='livros/', null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.titulo


# Modelo de Empréstimo
class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    devolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"Empréstimo de {self.livro.titulo} para {self.usuario.nome}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.devolvido:
            self.livro.disponivel = False
            self.livro.save()

    def marcar_devolucao(self):
        if not self.devolvido:
            self.devolvido = True
            self.data_devolucao = timezone.now()
            self.save()
            self.livro.disponivel = True
            self.livro.save()
