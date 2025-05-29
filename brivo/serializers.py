from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo


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


class LivroSerializer(serializers.ModelSerializer):
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


class EmprestimoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Emprestimo
        fields = ['id', 'livro', 'usuario', 'usuario_nome', 'livro_titulo', 'data_emprestimo', 'data_devolucao', 'devolvido']

    def validate(self, data):
        # Validação apenas na criação
        if self.instance is None:
            livro = data.get('livro')
            usuario = data.get('usuario')

            if not livro:
                raise serializers.ValidationError({"livro": "Este campo é obrigatório."})
            if not usuario:
                raise serializers.ValidationError({"usuario": "Este campo é obrigatório."})
            if not livro.disponivel:
                raise serializers.ValidationError({"livro": "Este livro não está disponível para empréstimo."})

        return data
