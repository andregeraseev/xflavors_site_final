# clientes/models.py
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser


class Cliente(models.Model):
    # relacionamento um-para-um com o modelo de usuário do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # CPF único do cliente
    cpf = models.CharField(max_length=11, blank=True, null=True)
    # número de celular do cliente
    celular = models.CharField(max_length=20, blank=True, null=True)
    #numero de celular possui whatsapp
    whatsapp = models.BooleanField(default=True)
    #ultimo login do cliente
    last_login = models.DateTimeField(verbose_name='last login', blank=True, null=True)
    # criacao do cliente
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    # cliente aceita receber email de propaganda
    propaganda = models.BooleanField(default=True)
    def __str__(self):
        return self.user.username

    def toggle_propaganda(self):
        """
        Alterna o valor do campo propaganda entre True e False.
        """
        self.propaganda = not self.propaganda
        self.save()




class EnderecoEntrega(models.Model):
    primario = models.BooleanField(default=True)
    # relacionamento com o modelo Cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # cep do endereço de entrega
    cep = models.CharField(max_length=8)
    # rua do endereço de entrega
    rua = models.CharField(max_length=50)
    # número do endereço de entrega
    numero = models.CharField(max_length=5)
    # bairro do endereço de entrega
    bairro = models.CharField(max_length=30)
    # cidade do endereço de entrega
    cidade = models.CharField(max_length=30)
    # estado do endereço de entrega
    estado = models.CharField(max_length=2, choices=[
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ])
    # complemento do endereço de entrega
    complemento = models.CharField(max_length=100, blank=True)
