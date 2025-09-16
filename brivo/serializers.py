from rest_framework import serializers
from .models import Livro, Usuario, Emprestimo, Reserva, AlertaSistema
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import datetime, date, time

# Serializers para os Alertas do Sistema
class AlertaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaSistema
        # Inclui todos os campos do modelo AlertaSistema, incluindo os novos
        fields = '__all__'
        # Campos que não devem ser modificados via API (exceto 'resolvido')
        read_only_fields = ['id', 'data_criacao', 'resolvido_em']

    def validate(self, data):
        """
        Valida os dados do AlertaSistema, especialmente para visibilidade e agendamento.
        """
        visibilidade = data.get('visibilidade')
        data_publicacao = data.get('data_publicacao')
        expira_em = data.get('expira_em')

        # Se for uma notificação pública, data_publicacao deve ser fornecida
        if visibilidade == 'publico' and not data_publicacao:
            raise serializers.ValidationError(
                {"data_publicacao": "A data de publicação é obrigatória para notificações públicas."}
            )

        # Se data_publicacao for fornecida, ela não pode ser no passado para novas criações
        # (para atualizações, pode ser que já tenha passado, o que é normal)
        if data_publicacao and self.instance is None: # Apenas para novas criações
            if data_publicacao < timezone.now():
                raise serializers.ValidationError(
                    {"data_publicacao": "A data de publicação não pode ser no passado para novas notificações."}
                )

        # Se expira_em for fornecida, ela não pode ser anterior a data_publicacao (se data_publicacao existir)
        if expira_em and data_publicacao:
            if expira_em <= data_publicacao:
                raise serializers.ValidationError(
                    {"expira_em": "A data de expiração deve ser posterior à data de publicação."}
                )

        # Se expira_em for fornecida, ela não pode ser no passado (a menos que já esteja expirada)
        if expira_em and self.instance is None: # Apenas para novas criações
            if expira_em < timezone.now():
                raise serializers.ValidationError(
                    {"expira_em": "A data de expiração não pode ser no passado para novas notificações."}
                )

        return data

    def create(self, validated_data):
        # O campo email_enviado pode ser definido pelo frontend para indicar se deve enviar notificação
        # Mas inicialmente sempre começa como False, sendo atualizado após o envio bem-sucedido
        should_send = validated_data.get('email_enviado', False)
        validated_data['email_enviado'] = False # Sempre começa como False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Lógica de atualização, especialmente para marcar como resolvido
        # ou para lidar com a data de expiração.
        # O campo email_enviado não deve ser atualizado diretamente aqui.
        return super().update(instance, validated_data)


# Serializers para as Reservas
class ReservaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    # Definir os novos campos como não obrigatórios na criação, mas serão validados juntos
    data_retirada_prevista = serializers.DateField(required=False, allow_null=True)
    hora_retirada_prevista = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'livro', 'aluno', 'aluno_nome', 'livro_titulo',
            'data_reserva', 'status', 'notificado_em',
            'data_retirada_prevista', 'hora_retirada_prevista'
        ]
        # 'status' agora pode ser definido na criação dependendo da data/hora
        read_only_fields = ['id', 'aluno', 'aluno_nome', 'livro_titulo', 'data_reserva', 'notificado_em']

    def validate(self, data):
        """
        Valida os dados da reserva, incluindo a lógica de agendamento.
        """
        livro = data.get('livro')
        data_retirada = data.get('data_retirada_prevista')
        hora_retirada = data.get('hora_retirada_prevista')
        request = self.context.get('request')
        aluno = request.user if request and hasattr(request, 'user') else None

        # Validação: Se data_retirada_prevista ou hora_retirada_prevista forem fornecidas, ambas devem estar presentes
        if (data_retirada and not hora_retirada) or (hora_retirada and not data_retirada):
            raise serializers.ValidationError(
                {"data_retirada_prevista": "Data e hora de retirada devem ser fornecidas juntas."}
            )

        # Lógica para reservas com data e hora (agendamento)
        if data_retirada and hora_retirada:
            # 1. Verificar se a data de retirada não é no passado
            if data_retirada < timezone.localdate():
                raise serializers.ValidationError(
                    {"data_retirada_prevista": "A data de retirada não pode ser no passado."}
                )
            # 2. Se a data for hoje, verificar se a hora não é no passado
            if data_retirada == timezone.localdate() and hora_retirada < timezone.localtime().time():
                raise serializers.ValidationError(
                    {"hora_retirada_prevista": "A hora de retirada não pode ser no passado para a data de hoje."}
                )

            # 3. Verificar se o livro está disponível no momento do agendamento
            # Se o livro não está disponível, ele não pode ser agendado para retirada imediata.
            # Ele só pode ser agendado se estiver disponível, ou se a reserva for para uma data futura
            # e o livro estará disponível até lá (lógica mais complexa, por enquanto focamos no status atual).
            if not livro.disponivel:
                # Se o livro está indisponível, verificar se há um empréstimo ativo
                emprestimo_ativo = Emprestimo.objects.filter(livro=livro, devolvido=False).first()
                if emprestimo_ativo:
                    # Se o livro está emprestado, verificar se a data de devolução prevista é anterior à data de retirada agendada
                    # Se não há data de devolução prevista ou se a data de devolução é posterior à agendada, não permite.
                    if emprestimo_ativo.data_devolucao is None or emprestimo_ativo.data_devolucao.date() > data_retirada:
                        raise serializers.ValidationError(
                            {"livro": "Este livro está atualmente emprestado e não estará disponível na data de retirada prevista."}
                        )
                else:
                    # Se não está disponível e não está emprestado, pode haver outra reserva ativa
                    # Isso será pego pela próxima validação de conflito de reserva.
                    pass # Deixar a validação de conflito de reserva lidar com isso.


            # 4. Verificar conflitos de agendamento para o livro:
            # - Outra reserva 'aguardando_retirada' para a mesma data/hora
            # - Um empréstimo ativo que se sobreponha à data/hora de retirada prevista

            # Verifica se já existe uma reserva 'aguardando_retirada' para o mesmo livro
            # na mesma data e hora prevista.
            conflito_reserva_agendada = Reserva.objects.filter(
                livro=livro,
                data_retirada_prevista=data_retirada,
                hora_retirada_prevista=hora_retirada,
                status='aguardando_retirada'
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if conflito_reserva_agendada:
                raise serializers.ValidationError(
                    {"livro": "Este livro já está agendado para retirada na data e hora selecionadas."}
                )

            # 5. Verificar se o usuário já tem uma reserva ativa (aguardando_retirada ou na_fila) para este livro
            ja_reservado_pelo_usuario = Reserva.objects.filter(
                livro=livro,
                aluno=aluno,
                status__in=['aguardando_retirada', 'na_fila']
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if ja_reservado_pelo_usuario:
                raise serializers.ValidationError(
                    {"livro": "Você já possui uma reserva ativa para este livro."}
                )

        # Lógica para reservas sem data e hora (reserva 'na_fila')
        else:
            # Se o livro está disponível, não pode fazer reserva 'na_fila'
            if livro.disponivel:
                raise serializers.ValidationError(
                    {"livro": "O livro está disponível para empréstimo imediato. Não é necessário entrar na fila."}
                )

            # Verificar se o usuário já tem uma reserva 'na_fila' para este livro
            ja_na_fila = Reserva.objects.filter(
                livro=livro,
                aluno=aluno,
                status='na_fila'
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if ja_na_fila:
                raise serializers.ValidationError(
                    {"livro": "Você já possui uma reserva na fila para este livro."}
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['aluno'] = request.user

        data_retirada = validated_data.get('data_retirada_prevista')
        hora_retirada = validated_data.get('hora_retirada_prevista')

        # Se data e hora de retirada foram fornecidas, o status inicial é 'aguardando_retirada'
        if data_retirada and hora_retirada:
            validated_data['status'] = 'aguardando_retirada'
        else:
            # Caso contrário, mantém o status padrão 'na_fila'
            validated_data['status'] = 'na_fila'

        return super().create(validated_data)

# Serializers para os Usuários
class UsuarioSerializer(serializers.ModelSerializer):
    # Campo 'id' é read-only, garantindo que não seja enviado na requisição PUT/PATCH
    id = serializers.IntegerField(read_only=True)
    senha = serializers.CharField(write_only=True, required=False) # Senha é opcional para updates
    # Adiciona o campo 'avatar' ao serializer.
    # write_only=True: o campo é aceito na entrada, mas não incluído na saída (GET).
    # required=False: o campo é opcional na entrada.
    avatar = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)


    class Meta:
        model = Usuario
        # Incluímos 'avatar' nos campos para que o serializer o reconheça
        fields = ['id', 'ra', 'nome', 'email', 'senha', 'turma', 'tipo', 'avatar']
    
    def validate_email(self, value):
        # Validação de email único apenas se estiver sendo alterado
        if self.instance and self.instance.email == value:
            return value
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value
    
    def validate_ra(self, value):
        # Validação de RA único apenas se estiver sendo alterado
        if self.instance and self.instance.ra == value:
            return value
        if Usuario.objects.filter(ra=value).exists():
            raise serializers.ValidationError("Este RA já está em uso.")
        return value
    
    def validate(self, data):
        # Validação adicional para campos obrigatórios
        errors = {}
        
        # Verifica se nome está vazio
        if 'nome' in data and not data['nome'].strip():
            errors['nome'] = 'O nome não pode estar vazio.'
        
        # Verifica se turma está vazia
        if 'turma' in data and not data['turma'].strip():
            errors['turma'] = 'A turma não pode estar vazia.'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        # Remove o avatar de validated_data antes de criar o usuário,
        # pois o modelo Usuario não tem esse campo.
        avatar = validated_data.pop('avatar', None) 
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(**validated_data, password=senha)
        return usuario

    def update(self, instance, validated_data):
        # Remove o avatar de validated_data antes de atualizar o usuário,
        # pois o modelo Usuario não tem esse campo.
        avatar = validated_data.pop('avatar', None) 
        senha = validated_data.pop('senha', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if senha:
            instance.set_password(senha)
        instance.save()
        return instance


# Serializers para os Livros
class LivroSerializer(serializers.ModelSerializer):
    def validate(self, data):
        erros = {}
        # Validação dos campos obrigatórios
        if not data.get('titulo'):
            erros['titulo'] = 'O título é obrigatório.'
        if not data.get('autor'):
            erros['autor'] = 'O autor é obrigatório.'
        if not data.get('data_publicacao'):
            erros['data_publicacao'] = 'A data de publicação é obrigatória.'
        if not data.get('tipo'):
            erros['tipo'] = "O tipo do livro é obrigatório ('fisico' ou 'pdf')."
        if erros:
            raise serializers.ValidationError(erros)
        return data
    capa = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    disponivel = serializers.BooleanField(read_only=True)
    quantidade_total = serializers.IntegerField(required=False)
    quantidade_emprestada = serializers.IntegerField(required=False)
    subgenero = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # NOVO: Campo subgênero

    titulo = serializers.CharField(
        required=True,
        error_messages={
            "blank": "O título é obrigatório.",
            "required": "O título é obrigatório."
        }
    )
    autor = serializers.CharField(
        required=True,
        error_messages={
            "blank": "O autor é obrigatório.",
            "required": "O autor é obrigatório."
        }
    )

    class Meta:
        model = Livro
        fields = [
            'id', 'titulo', 'autor', 'editora', 'data_publicacao', 'numero_paginas', 'tipo', 'genero', 'subgenero',
            'quantidade_total', 'quantidade_emprestada', 'capa', 'descricao', 'ativo', 'disponivel'
        ]
        read_only_fields = ['id', 'disponivel', 'ativo']


# Serializers para Empréstimos
class EmprestimoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)
    
    # NOVOS CAMPOS: Adiciona a capa e o autor do livro diretamente no serializer do empréstimo
    livro_capa = serializers.URLField(source='livro.capa', read_only=True)
    livro_autor = serializers.CharField(source='livro.autor', read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            'id', 'livro', 'usuario', 'usuario_nome',
            'livro_titulo', 'livro_capa', 'livro_autor', # Incluído capa e autor
            'data_emprestimo', 'data_devolucao', 'devolvido'
        ]

    def validate(self, data):
        # Só valida disponibilidade se o campo 'livro' estiver sendo enviado (POST ou PUT/PATCH com 'livro')
        if 'livro' in data:
            livro = data['livro']
            # Se o livro já estiver emprestado (devolvido=False), não permite um novo empréstimo direto.
            # A efetivação de reserva já lida com a disponibilidade do livro antes de criar o empréstimo.
            # A validação de disponibilidade agora é feita no método save do modelo Emprestimo.
            # if Emprestimo.objects.filter(livro=livro, devolvido=False).exists():
            #     raise serializers.ValidationError({"livro": "Este livro já está emprestado."})

            # Verifica se o livro está ativo. A validação de disponibilidade de exemplares
            # é feita no método save do modelo Emprestimo.
            if not livro.ativo:
                raise serializers.ValidationError({"livro": "Este livro não está ativo."})
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
