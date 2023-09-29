
from django.contrib import admin
from .models import AvisoEstoque


class AvisoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'cliente', 'notificado', 'created_at', 'updated_at')
    list_filter = ('notificado', 'produto__name', 'created_at','updated_at')
    search_fields = ('produto__name', 'cliente__username')
    ordering = ('notificado', 'produto__name')

admin.site.register(AvisoEstoque, AvisoEstoqueAdmin)
