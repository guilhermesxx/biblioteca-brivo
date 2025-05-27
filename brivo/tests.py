from django.test import TestCase
from django.utils import timezone
from brivo.models import Usuario, Livro, Emprestimo

class EmprestimoModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            ra="1001",
            nome="João da Silva",
            email="joao_unique@example.com",  # Evita conflito com e-mails existentes
            turma="2A",
            tipo="aluno",
            senha="senha123"
        )

        self.livro = Livro.objects.create(
            titulo="Dom Casmurro",
            autor="Machado de Assis",
            data_publicacao="1899-01-01",
            tipo="fisico"
        )

    def test_emprestimo_e_devolucao(self):
        emprestimo = Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro
        )

        self.assertFalse(emprestimo.devolvido)
        self.assertTrue(emprestimo.livro.disponivel)  # Se livro não for marcado como indisponível automaticamente

        emprestimo.marcar_devolucao()

        emprestimo.refresh_from_db()
        emprestimo.livro.refresh_from_db()

        self.assertTrue(emprestimo.devolvido)
        self.assertIsNotNone(emprestimo.data_devolucao)
        self.assertTrue(emprestimo.livro.disponivel)
