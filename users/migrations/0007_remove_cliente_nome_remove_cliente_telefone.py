# Generated by Django 5.1.7 on 2025-04-18 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_cliente_imagem"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cliente",
            name="nome",
        ),
        migrations.RemoveField(
            model_name="cliente",
            name="telefone",
        ),
    ]
