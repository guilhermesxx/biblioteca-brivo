from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Livro, Emprestimo

Usuario = get_user_model()

class UsuarioModelTest(TestCase):
    def test_criacao_usuario(self):
        usuario = Usuario.objects.create_user(
            ra="123456",
            nome="Aluno Teste",
            email="aluno@teste.com",
            turma="3A",
            tipo="aluno",
            senha="senha123"
        )
        self.assertEqual(usuario.email, "aluno@teste.com")
        self.assertTrue(usuario.check_password("senha123"))
        self.assertFalse(usuario.is_staff)

    def test_criacao_superusuario(self):
        admin = Usuario.objects.create_superuser(
            ra="admin001",
            nome="Administrador",
            email="admin@teste.com",
            senha="admin123"
        )
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.tipo, "admin")


class LivroModelTest(TestCase):
    def test_criacao_livro(self):
        livro = Livro.objects.create(
            titulo="Dom Casmurro",
            autor="Machado de Assis",
            editora="Editora Teste",
            data_publicacao="1899-01-01",
            numero_paginas=256,
            tipo="fisico",
            disponivel=True,
            descricao="Clássico da literatura brasileira."
        )
        self.assertEqual(livro.titulo, "Dom Casmurro")
        self.assertTrue(livro.disponivel)


class EmprestimoModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            ra="78910",
            nome="Usuário Exemplo",
            email="usuario@teste.com",
            turma="2B",
            tipo="aluno",
            senha="teste123"
        )
        self.livro = Livro.objects.create(
            titulo="1984",
            autor="George Orwell",
            data_publicacao="1949-06-08",
            tipo="fisico"
        )

    def test_realizar_emprestimo(self):
        emprestimo = Emprestimo.objects.create(
            livro=self.livro,
            usuario=self.usuario
        )
        self.livro.refresh_from_db()
        self.assertFalse(self.livro.disponivel)
        self.assertFalse(emprestimo.devolvido)

    def test_marcar_devolucao(self):
        emprestimo = Emprestimo.objects.create(
            livro=self.livro,
            usuario=self.usuario
        )
        emprestimo.marcar_devolucao()
        self.livro.refresh_from_db()
        emprestimo.refresh_from_db()
        self.assertTrue(emprestimo.devolvido)
        self.assertIsNotNone(emprestimo.data_devolucao)
        self.assertTrue(self.livro.disponivel)

    def test_emprestar_livro_indisponivel(self):
        Emprestimo.objects.create(livro=self.livro, usuario=self.usuario)
        self.livro.refresh_from_db()
        self.assertFalse(self.livro.disponivel)

        # Tentar novo empréstimo
        novo_usuario = Usuario.objects.create_user(
            ra="98765",
            nome="Outro Usuário",
            email="outro@teste.com",
            turma="1C",
            tipo="aluno",
            senha="teste456"
        )

        # Mesmo que a lógica da view deva bloquear isso, o modelo permite — por isso você deve bloquear via view ou serializer
        novo_emprestimo = Emprestimo.objects.create(livro=self.livro, usuario=novo_usuario)
        self.assertFalse(novo_emprestimo.devolvido)
