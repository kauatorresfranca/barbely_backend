# Generated by Django 5.1.7 on 2025-03-26 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="barbearia",
            name="nome",
            field=models.CharField(default="Desconhecido", max_length=100),
        ),
    ]
