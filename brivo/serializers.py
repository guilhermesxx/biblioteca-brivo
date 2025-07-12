# brivo/serializers.py

from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo, Reserva
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

# Serializers para as Reservas
class ReservaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)  # opcional, aparece no retorno

    class Meta:
        model = Reserva
        fields = ['id', 'livro', 'aluno', 'aluno_nome', 'data_reserva', 'status', 'notificado_em']
        read_only_fields = ['id', 'aluno', 'aluno_nome', 'data_reserva', 'status', 'notificado_em']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['aluno'] = request.user

        livro = validated_data['livro']
        if livro.disponivel:
            raise serializers.ValidationError({"livro": "O livro ainda está disponível. Você pode fazer o empréstimo direto."})

        return super().create(validated_data)


# Serializers para os Usuários
class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'ra', 'nome', 'email', 'senha', 'turma', 'tipo']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(**validated_data, password=senha)
        return usuario

    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if senha:
            instance.set_password(senha)
        instance.save()
        return instance


# Serializers para os Livros
class LivroSerializer(serializers.ModelSerializer):
    capa = serializers.URLField(required=False)

    titulo = serializers.CharField(
        error_messages={
            "blank": "O título é obrigatório.",
            "required": "O título é obrigatório."
        }
    )
    autor = serializers.CharField(
        error_messages={
            "blank": "O autor é obrigatório.",
            "required": "O autor é obrigatório."
        }
    )

    class Meta:
        model = Livro
        fields = '__all__'


# Serializers para Empréstimos
class EmprestimoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)  # será preenchido pela view
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            'id', 'livro', 'usuario', 'usuario_nome',
            'livro_titulo', 'data_emprestimo', 'data_devolucao', 'devolvido'
        ]

    def validate(self, data):
        # Só valida disponibilidade se o campo 'livro' estiver sendo enviado (POST ou PUT/PATCH com 'livro')
        if 'livro' in data:
            livro = data['livro']
            if not livro.disponivel:
                raise serializers.ValidationError({"livro": "Este livro não está disponível para empréstimo."})
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Sobrescreve o método validate para adicionar a lógica de verificação de tipo de usuário
    def validate(self, attrs):
        # Chama o método validate da classe pai para realizar a autenticação padrão (email/senha)
        data = super().validate(attrs)
        user = self.user # O usuário autenticado é acessível via self.user após a validação do pai

        # Verifica se o usuário está ativo
        if not user.is_active:
            raise AuthenticationFailed("Usuário inativo.", code='user_inactive')

        # Obtém o tipo de usuário enviado na requisição do frontend
        tipo_enviado = self.context['request'].data.get('tipo')

        # Lógica para verificar o tipo de usuário
        # Se um tipo foi enviado E o tipo do usuário autenticado não corresponde ao tipo enviado,
        # lança uma exceção AuthenticationFailed.
        # Isso fará com que o login retorne um erro 401/403, conforme a sua necessidade.
        if tipo_enviado and user.tipo.lower() != tipo_enviado.lower():
            raise AuthenticationFailed(
                f"Tipo de usuário inválido para o login. Você tentou logar como '{tipo_enviado}', mas o usuário é '{user.tipo}'.",
                code='invalid_user_type'
            )

        # Adiciona informações do usuário ao payload do token de resposta
        data['user'] = {
            "id": user.id,
            "email": user.email,
            "tipo": user.tipo,
            "nome": user.nome,
        }

        return data

