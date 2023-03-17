from django.contrib import admin
from .models import Produto, Category, Subcategory,Variation, MateriaPrima
from django.utils.html import format_html

class VariationCategoryInline(admin.TabularInline):
    model = Variation

class SubCategoryInline(admin.TabularInline):
    model = Subcategory

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price', 'stock','tem_variation','localizacao')
    search_fields = ('name',)
    actions = ['duplicate_product']

    def tem_variation(self, obj):
        if obj.variation_set.exists():
            return format_html('<a href="{}">{}</a>', f'/admin/produtos/variation/?produto_pai__id__exact={obj.id}',
                               'SIM')
        else:
            return 'NAO'

    tem_variation.short_description = 'tem Variation'

    def duplicate_product(self, request, queryset):
        for obj in queryset:
            obj.pk = None
            obj.name = obj.name + ' (Copy)'
            obj.save()
    duplicate_product.short_description = "Duplicate Selected Products"

admin.site.register(Produto, ProdutoAdmin)

class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('id','name','stock')
    list_editable = ('stock',)
    search_fields = ('name',)


admin.site.register(MateriaPrima, MateriaPrimaAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(Category, CategoryAdmin)

admin.site.register(Subcategory)


class VariantionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'materia_prima', 'gasto')
    list_editable = ('materia_prima',)
    search_fields = ('name',)

admin.site.register(Variation,VariantionAdmin)
