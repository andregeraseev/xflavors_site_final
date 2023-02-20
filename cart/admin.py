from django.contrib import admin
from .models import Cart, CartItem


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