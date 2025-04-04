from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify

class Barbearia(AbstractUser):
    nome_barbearia = models.CharField(max_length=100)
    nome_proprietario = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True)
    plano = models.CharField(
        max_length=20, 
        choices=[("free", "Grátis"), ("premium", "Premium")],
        default="free"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = BaseUserManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nome_barbearia)
            unique_slug = base_slug
            contador = 1

            while Barbearia.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{contador}"
                contador += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def get_url_personalizada(self):
        return f"https://barberly.com/{self.slug}"

    def __str__(self):
        return self.nome_barbearia
