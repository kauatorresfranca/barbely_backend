# Generated by Django 5.1.7 on 2025-05-03 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0015_alter_barbearia_imagem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="barbearia",
            name="imagem",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
