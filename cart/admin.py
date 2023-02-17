from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
  model = CartItem
  extra = 0

# @admin.register(Cart)
class Cartadmin(admin.ModelAdmin):
  inlines = [CartItemInline]
  list_display = ['id', 'user']

admin.site.register(Cart, Cartadmin)