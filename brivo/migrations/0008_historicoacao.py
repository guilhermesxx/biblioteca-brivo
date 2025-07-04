# Generated by Django 5.2 on 2025-06-21 02:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brivo', '0007_livro_ativo_usuario_ativo'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoAcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objeto_tipo', models.CharField(max_length=50)),
                ('objeto_id', models.PositiveIntegerField()),
                ('acao', models.CharField(choices=[('CRIACAO', 'Criação'), ('EDICAO', 'Edição'), ('DESATIVACAO', 'Desativação')], max_length=20)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('descricao', models.TextField(blank=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
