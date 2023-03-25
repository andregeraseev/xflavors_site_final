from django.contrib import admin

from django.contrib import admin
from .models import Cliente, EnderecoEntrega

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'celular', 'cpf','last_login', 'created_at')
    search_fields = ('user__username','celular','cpf',)

@admin.register(EnderecoEntrega)
class EnderecoEntrega(admin.ModelAdmin):
    list_display = ('cliente','cep', 'rua', 'numero', 'cidade', 'bairro', 'estado', 'complemento' , 'primario')
    search_fields = ('cliente__user__username',)
    list_editable = ('primario',)
    list_filter = ('primario',)
