from django.contrib import admin
from .models import Produto, Category, Subcategory,Variation


class VariationCategoryInline(admin.TabularInline):
    model = Variation

class SubCategoryInline(admin.TabularInline):
    model = Subcategory

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    actions = ['duplicate_product']

    def duplicate_product(self, request, queryset):
        for obj in queryset:
            obj.pk = None
            obj.name = obj.name + ' (Copy)'
            obj.save()
    duplicate_product.short_description = "Duplicate Selected Products"

admin.site.register(Produto, ProdutoAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(Category, CategoryAdmin)

admin.site.register(Subcategory)


class VariantionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

admin.site.register(Variation,VariantionAdmin)
