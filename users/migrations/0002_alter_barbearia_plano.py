# Generated by Django 5.1.7 on 2025-03-31 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="barbearia",
            name="plano",
            field=models.CharField(
                choices=[("free", "Grátis"), ("premium", "Premium")],
                default="free",
                max_length=20,
            ),
        ),
    ]
