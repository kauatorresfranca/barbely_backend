# Generated by Django 5.1.7 on 2025-05-22 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_funcionario_imagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='funcionario',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='telefone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
