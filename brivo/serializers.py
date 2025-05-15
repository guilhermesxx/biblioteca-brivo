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
        ra = validated_data.get('ra')
        nome = validated_data.get('nome')
        email = validated_data.get('email')
        turma = validated_data.get('turma')
        tipo = validated_data.get('tipo')

        usuario = Usuario.objects.create_user(
            ra=ra,
            nome=nome,
            email=email,
            turma=turma,
            tipo=tipo,
            senha=senha
        )
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
        livro = data.get('livro')
        usuario = data.get('usuario')

        # Verifica se os campos estão preenchidos
        if not livro:
            raise serializers.ValidationError({"livro": "Este campo é obrigatório."})
        if not usuario:
            raise serializers.ValidationError({"usuario": "Este campo é obrigatório."})

        # Verifica se o livro está disponível
        if not livro.disponivel:
            raise serializers.ValidationError({"livro": "Este livro não está disponível para empréstimo."})

        return data
