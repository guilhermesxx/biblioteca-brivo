from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Usuario, Livro, Emprestimo

class EmprestimoUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Criando usuários
        self.aluno = Usuario.objects.create_user(
            ra="123", nome="Aluno Teste", email="aluno@example.com",
            turma="1A", tipo="aluno", password="123"
        )

        self.professor = Usuario.objects.create_user(
            ra="456", nome="Professor Teste", email="prof@example.com",
            turma="2B", tipo="professor", password="123"
        )

        self.admin = Usuario.objects.create_user(
            ra="789", nome="Admin Teste", email="admin@example.com",
            turma="ADM", tipo="admin", password="123"
        )

        # Criando livro (sem 'quantidade'!)
        self.livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao="2020-01-01",
            tipo="fisico"
        )

        # Criando empréstimo para o aluno
        self.emprestimo = Emprestimo.objects.create(
            livro=self.livro,
            usuario=self.aluno
        )

        self.url = reverse('emprestimo-detail', kwargs={'pk': self.emprestimo.pk})

    def autenticar(self, usuario):
        self.client.force_authenticate(user=usuario)

    def test_usuario_pode_marcar_devolvido(self):
        self.autenticar(self.aluno)

        response = self.client.patch(self.url, {'devolvido': True}, format='json')
        self.emprestimo.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.emprestimo.devolvido)
        self.assertIsNotNone(self.emprestimo.data_devolucao)

    def test_apenas_dono_ou_admin_pode_editar(self):
        self.autenticar(self.professor)  # Professor tentando editar empréstimo de outro

        response = self.client.patch(self.url, {'devolvido': True}, format='json')

        self.assertEqual(response.status_code, 403)  # Esperado: acesso negado

    def test_admin_pode_editar_emprestimo_de_outro_usuario(self):
        self.autenticar(self.admin)

        response = self.client.patch(self.url, {'devolvido': True}, format='json')
        self.emprestimo.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.emprestimo.devolvido)
