from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify

class BarbeariaManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

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

    objects = BarbeariaManager()  # Usa o manager personalizado

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome_barbearia)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_barbearia
