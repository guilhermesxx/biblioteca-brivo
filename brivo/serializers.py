from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo

class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)  # Adicionando o campo de senha

    class Meta:
        model = Usuario
        fields = ['ra', 'nome', 'email', 'senha', 'turma', 'tipo']  # Incluindo a senha

    def create(self, validated_data):
        senha = validated_data.pop('senha')  # Remover a senha dos dados validados
        usuario = Usuario.objects.create(**validated_data)  # Criar o usuário sem a senha
        usuario.set_password(senha)  # Criptografar a senha
        usuario.save()  # Salvar o usuário no banco
        return usuario


class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = '__all__'


class EmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = '__all__'

    def validate(self, data):
        # Verificar se o livro existe
        if not Livro.objects.filter(id=data['livro']).exists():
            raise serializers.ValidationError("Livro não encontrado.")
        # Verificar se o usuário existe
        if not Usuario.objects.filter(id=data['usuario']).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return data
