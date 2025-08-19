import os
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from brivo.models import Livro

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biblioteca.settings")
django.setup()

class LivroCreateTest(TestCase):
    def setUp(self):
        # Cria um usuário admin
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            ra="0001",
            nome="Admin Teste",
            email="admin@teste.com",
            turma="ADM",
            tipo="admin",
            password="admin123"
        )
        # Obtém o token JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.admin)
        self.token = str(refresh.access_token)

    def test_criar_livro_como_admin(self):
        payload = {
            "titulo": "Livro Teste",
            "autor": "Autor Teste",
            "editora": "Editora Teste",
            "data_publicacao": "2025-08-18",
            "numero_paginas": 123,
            "tipo": "fisico",
            "genero": "Aventura",
            "quantidade_total": 5,
            "quantidade_emprestada": 0,
            "capa": "https://exemplo.com/capa.jpg",
            "descricao": "Descrição do livro teste."
        }
        # Adiciona o header Authorization com o token JWT
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post("/api/livros/", payload, format="json", **headers)
        self.assertEqual(response.status_code, 201, f"Erro: {response.content}")
        self.assertEqual(Livro.objects.count(), 1)
        livro = Livro.objects.first()
        self.assertEqual(livro.titulo, payload["titulo"])
        self.assertEqual(livro.autor, payload["autor"])
        print("✅ Teste de criação de livro como admin passou!")
