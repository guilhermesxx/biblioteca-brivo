from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo

# Serializer de Usuário
class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'ra', 'nome', 'email', 'senha', 'turma', 'tipo']  # Incluindo ID

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(senha)
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if senha:
            instance.set_password(senha)
        instance.save()
        return instance

# Serializer de Livro
class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = '__all__'

# Serializer de Empréstimo
class EmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = '__all__'

    def validate(self, data):
        # Verifica se o livro existe
        livro = data.get('livro')
        if not Livro.objects.filter(id=livro.id).exists():
            raise serializers.ValidationError("Livro não encontrado.")
        # Verifica se o usuário existe
        usuario = data.get('usuario')
        if not Usuario.objects.filter(id=usuario.id).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return data
