# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brivo', '0018_remove_livro_subgenero'),
    ]

    operations = [
        migrations.AddField(
            model_name='livro',
            name='subgenero',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]