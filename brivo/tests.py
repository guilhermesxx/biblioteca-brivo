from django.test import TestCase
from rest_framework.exceptions import ValidationError
from brivo.serializers import LivroSerializer

from datetime import date

class LivroSerializerTestCase(TestCase):
    def test_numero_paginas_invalido(self):
        """Deve falhar se número de páginas for menor ou igual a zero"""
        data = {
            "titulo": "Livro Teste",
            "autor": "Autor Teste",
            "editora": "Editora Teste",
            "data_publicacao": date.today(),
            "numero_paginas": 0,  # inválido
            "tipo": "fisico",
            "disponivel": True,
        }

        serializer = LivroSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("numero_paginas", serializer.errors)
        self.assertEqual(serializer.errors["numero_paginas"][0], "O número de páginas deve ser maior que zero.")

    def test_titulo_em_branco(self):
        """Deve falhar se o título estiver em branco"""
        data = {
            "titulo": "",
            "autor": "Autor Teste",
            "editora": "Editora Teste",
            "data_publicacao": date.today(),
            "numero_paginas": 100,
            "tipo": "fisico",
            "disponivel": True,
        }

        serializer = LivroSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("titulo", serializer.errors)
        self.assertEqual(serializer.errors["titulo"][0], "O título é obrigatório.")

    def test_autor_em_branco(self):
        """Deve falhar se o autor estiver em branco"""
        data = {
            "titulo": "Livro Teste",
            "autor": "",
            "editora": "Editora Teste",
            "data_publicacao": date.today(),
            "numero_paginas": 100,
            "tipo": "fisico",
            "disponivel": True,
        }

        serializer = LivroSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("autor", serializer.errors)
        self.assertEqual(serializer.errors["autor"][0], "O autor é obrigatório.")
