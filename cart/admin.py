from django.contrib import admin
from .models import Cart, CartItem, Cupom


class CartItemAdmin(admin.ModelAdmin):
  list_display = ('product', 'quantity', 'variation', 'total_price')
  list_filter = ('product', 'variation')
  search_fields = ('product__name', 'variation__name')
  ordering = ('product',)


admin.site.register(CartItem, CartItemAdmin)


class CartItemInline(admin.TabularInline):
  model = CartItem
  extra = 0

# @admin.register(Cart)
class Cartadmin(admin.ModelAdmin):
  inlines = [CartItemInline]
  list_display = ['id', 'user']

admin.site.register(Cart, Cartadmin)


class CupomAdmin(admin.ModelAdmin):
  list_display = ['codigo', 'desconto_percentual', 'desconto_fixo', 'maximo_usos', 'usos_atuais', 'minimo_compra','status', 'data_validade']
  search_fields = ['codigo', 'status']
  list_filter = ['status', 'data_criacao', 'data_validade']
  ordering = ['-data_criacao']
  date_hierarchy = 'data_criacao'

  readonly_fields = ('data_criacao', 'data_modificacao', 'usos_atuais')

  fieldsets = (
    (None, {
      'fields': (
        'codigo',
        'desconto_percentual',
        'desconto_fixo',
        'maximo_usos',
        'data_validade',
        'minimo_compra'
      )
    }),
    ('Status e Datas', {
      'fields': (
        'status',
        'data_criacao',
        'data_modificacao'
      )
    }),
    ('Frete', {
      'fields': (
        'estados_frete_gratis',
        'tipo_de_frete_gratis',
        'desconto_percentual_frete'
      )
    }),
    ('Restrições', {
      'fields': (
        'produtos_aplicaveis',
        'categorias_aplicaveis',
        'max_uso_por_cliente'
      )
    }),
    ('Controle de Uso', {
      'fields': (
        'usos_atuais',
      )
    }),
  )

  # Este método gerará automaticamente um código ao adicionar um novo cupom
  def save_model(self, request, obj, form, change):
    if not obj.codigo:
      obj.gerar_codigo()
    super().save_model(request, obj, form, change)
admin.site.register(Cupom, CupomAdmin)