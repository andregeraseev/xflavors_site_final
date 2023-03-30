
from django.contrib import admin
from .models import AvisoEstoque

class AvisoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'cliente', 'notificado')
    list_filter = ('notificado', 'produto__name')
    search_fields = ('produto__nome', 'cliente__username')
    ordering = ('notificado', 'produto__name')

admin.site.register(AvisoEstoque, AvisoEstoqueAdmin)
