from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

from cart.views import carrinho,update_item,remove_item,clear_cart, add_to_cart


app_name = 'cart'

urlpatterns = [
    path('carrinho/', carrinho, name='carrinho'),
    path('update_item/', update_item, name='update_item'),
    path('remove_item/', remove_item, name='remove_item'),
    path('clear/', clear_cart, name='clear_cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)