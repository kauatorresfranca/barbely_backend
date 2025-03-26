# Generated by Django 5.1.7 on 2025-03-26 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_barbearia_nome"),
    ]

    operations = [
        migrations.AlterField(
            model_name="barbearia",
            name="nome",
            field=models.CharField(default="Desconhecido", max_length=100),
        ),
        migrations.AlterField(
            model_name="barbearia",
            name="username",
            field=models.CharField(
                default="temp_username", max_length=150, unique=True
            ),
        ),
    ]
