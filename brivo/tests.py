from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from .models import Usuario

class UsuarioAPITests(APITestCase):
    """
    Conjunto de testes para a API de Usuario.
    """
    def setUp(self):
        """
        Configura o ambiente de teste com usuários e dados iniciais.
        """
        # Cria um usuário admin para os testes de permissão
        self.admin_user = Usuario.objects.create_user(
            ra='12345',
            nome='Admin User',
            email='admin@example.com',
            turma='A',
            tipo='admin',
            password='adminpassword'
        )
        
        # Cria um usuário normal (aluno) para ser o alvo das atualizações
        self.target_user = Usuario.objects.create_user(
            ra='67890',
            nome='Target User',
            email='target@example.com',
            turma='B',
            tipo='aluno',
            password='targetpassword'
        )

        # URLs para os endpoints
        self.list_url = reverse('usuario-list')
        self.detail_url = reverse('usuario-detail', kwargs={'pk': self.target_user.pk})

        # Autentica o cliente de teste como o usuário admin
        admin_token = AccessToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

    def test_admin_can_update_user_info(self):
        """
        Verifica se um usuário admin pode atualizar informações de outro usuário.
        """
        # Dados para a atualização
        update_data = {
            'nome': 'Updated Target Name',
            'turma': 'C'
        }

        # Realiza a requisição PATCH para atualizar o usuário
        response = self.client.patch(self.detail_url, update_data, format='json')
        
        # Verifica se a resposta foi um sucesso
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Recarrega o usuário do banco de dados para verificar as mudanças
        self.target_user.refresh_from_db()

        # Verifica se os campos foram atualizados corretamente
        self.assertEqual(self.target_user.nome, update_data['nome'])
        self.assertEqual(self.target_user.turma, update_data['turma'])
        # O RA não deve ter mudado
        self.assertEqual(self.target_user.ra, '67890')

    def test_non_admin_cannot_update_user_info(self):
        """
        Verifica se um usuário não-admin (como um aluno) não pode atualizar informações de outro usuário.
        """
        # Cria um terceiro usuário (não-admin) para tentar editar o target_user
        other_user = Usuario.objects.create_user(
            ra='99999',
            nome='Other User',
            email='other@example.com',
            turma='C',
            tipo='aluno',
            password='otherpassword'
        )
        
        # Remove as credenciais do admin
        self.client.credentials()

        # Autentica como o terceiro usuário (não o target_user)
        other_token = AccessToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')

        # Dados para a tentativa de atualização do target_user
        update_data = {
            'nome': 'Hacker Name',
            'turma': 'Z'
        }

        # Realiza a requisição PATCH tentando editar outro usuário
        response = self.client.patch(self.detail_url, update_data, format='json')

        # Verifica se a resposta foi um erro de permissão (403 Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Recarrega o usuário do banco de dados
        self.target_user.refresh_from_db()

        # Verifica se os campos NÃO foram alterados
        self.assertNotEqual(self.target_user.nome, update_data['nome'])
        self.assertNotEqual(self.target_user.turma, update_data['turma'])
