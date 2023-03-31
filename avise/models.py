# models.avise

from django.db import models
from django.contrib.auth.models import User
from produtos.models import Produto, Variation


class AvisoEstoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    # variacao = models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, blank=True)
    # quantidade = models.PositiveIntegerField()
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    notificado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return f'{self.cliente.username} - {self.produto.name}'

