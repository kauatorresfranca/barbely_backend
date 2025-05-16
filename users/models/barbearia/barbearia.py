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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Barbearia(AbstractUser):
    nome_barbearia = models.CharField(max_length=100)
    nome_proprietario = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    telefone = models.CharField(max_length=16, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.CharField(max_length=500, blank=True, null=True)  # Armazena URL
    plano = models.CharField(
        max_length=20,
        choices=[("free", "Grátis"), ("premium", "Premium")],
        default="free"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    pix = models.BooleanField(default=True)
    credit_card = models.BooleanField(default=True)
    debit_card = models.BooleanField(default=True)
    cash = models.BooleanField(default=True)
    intervalo_agendamento = models.PositiveIntegerField(default=30)
    prazo_cancelamento = models.PositiveIntegerField(default=30)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='barbearia_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='barbearia_permissions',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = BarbeariaManager()

    def save(self, *args, **kwargs):
        if not self.slug and self.nome_barbearia:
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