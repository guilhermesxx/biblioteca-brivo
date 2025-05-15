from rest_framework import status
from rest_framework.test import APITestCase
from .models import Usuario, Livro, Emprestimo
from django.utils import timezone
from datetime import date

class LivroTests(APITestCase):
    def test_criar_livro(self):
        data = {
            "titulo": "Dom Casmurro",
            "autor": "Machado de Assis",
            "editora": "Editora Exemplo",
            "data_publicacao": "2020-01-01",
            "numero_paginas": 256,
            "tipo": "fisico",
            "descricao": "Um clássico da literatura brasileira."
        }
        response = self.client.post("/api/livros/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listar_livros(self):
        Livro.objects.create(
            titulo="Dom Casmurro",
            autor="Machado de Assis",
            editora="Editora Exemplo",
            data_publicacao=date(2020, 1, 1),
            numero_paginas=256,
            tipo="fisico",
            descricao="Um clássico"
        )
        response = self.client.get("/api/livros/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)


class EmprestimoTests(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            ra="12345",
            nome="Aluno Teste",
            email="aluno@teste.com",
            turma="3A",
            tipo="aluno",
            senha="123456"
        )
        self.livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Autor Teste",
            editora="Editora Teste",
            data_publicacao=date(2020, 1, 1),
            numero_paginas=100,
            tipo="fisico",
            descricao="Descrição teste"
        )

    def test_criar_emprestimo(self):
        data = {
            "usuario": self.usuario.id,
            "livro": self.livro.id
        }
        response = self.client.post("/api/emprestimos/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listar_emprestimos(self):
        Emprestimo.objects.create(usuario=self.usuario, livro=self.livro)
        response = self.client.get("/api/emprestimos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
