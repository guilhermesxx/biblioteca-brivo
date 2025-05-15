from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo

# Serializer de Usuário
class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'ra', 'nome', 'email', 'senha', 'turma', 'tipo']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(**validated_data, senha=senha)
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
        if not data.get('livro'):
            raise serializers.ValidationError({"livro": "Este campo é obrigatório."})
        if not data.get('usuario'):
            raise serializers.ValidationError({"usuario": "Este campo é obrigatório."})
        return data
