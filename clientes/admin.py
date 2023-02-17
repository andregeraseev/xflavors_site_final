from django.contrib import admin

from django.contrib import admin
from .models import Cliente, EnderecoEntrega

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'celular', 'cpf')

@admin.register(EnderecoEntrega)
class EnderecoEntrega(admin.ModelAdmin):
    list_display = ('cliente','cep', 'rua', 'numero', 'cidade', 'bairro', 'estado', 'complemento')
