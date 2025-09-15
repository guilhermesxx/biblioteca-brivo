# Generated migration for adding subgenero field to Livro model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brivo', '0016_alter_emprestimo_livro'),
    ]

    operations = [
        migrations.AddField(
            model_name='livro',
            name='subgenero',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]