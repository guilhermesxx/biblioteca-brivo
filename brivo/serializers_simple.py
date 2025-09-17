from rest_framework import serializers
from .models import Usuario

class SimpleUsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'ra', 'nome', 'email', 'senha', 'turma', 'tipo']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(**validated_data, password=senha)
        return usuario