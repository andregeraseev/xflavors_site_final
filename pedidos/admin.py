from django.contrib import admin
from .models import Pedido
from .models import PedidoItem


class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'variation']

admin.site.register(PedidoItem, PedidoItemAdmin)




@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'endereco_entrega', 'status', 'data_pedido','metodo_de_pagamento','rastreamento', 'producao')
    list_editable = ('rastreamento', 'producao', 'status',)
    # list_filter = ('status', 'data_pedido')
    # search_fields = ('id', 'user__username', 'endereco_entrega__endereco')
