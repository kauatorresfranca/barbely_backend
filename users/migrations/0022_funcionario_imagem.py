# Generated by Django 5.1.7 on 2025-05-17 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0021_cliente_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="funcionario",
            name="imagem",
            field=models.ImageField(blank=True, null=True, upload_to="funcionarios/"),
        ),
    ]
