from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from clientes import views
from produtos.views import product_detail, produto_por_subcategoria
from .views import index
from cart.views import add_to_cart_carrocel
from cart.views import add_to_cart
from pedidos.views import checkout,  atualizar_endereco_entrega, editar_endereco, cotacao_frete_correios,criar_pedido,pagina_pagamento

urlpatterns = [

    path('cart/', include('cart.urls', namespace='cart')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('', index, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    # path('carrinho/', views.carrinho, name='carrinho'),
    path('add_to_cart_carrocel/', add_to_cart_carrocel, name='add_to_cart_carrocel'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('categoria/<int:category_id>/subcategoria/<int:subcategory_id>/', produto_por_subcategoria, name='produto_por_subcategoria'),
    path('checkout/', checkout, name='checkout'),
    # path('processar_pagamento/', processar_pagamento, name='processar_pagamento'),
    path('atualizar_endereco_entrega/', atualizar_endereco_entrega, name='atualizar_endereco_entrega'),
    path('editar_endereco/', editar_endereco, name='editar_endereco'),
    path('cotacao_frete_correios/', cotacao_frete_correios, name='cotacao_frete_correios'),
    path('criar_pedido/', criar_pedido, name='criar_pedido'),
    path('pagina_pagamento/<int:pedido_id>', pagina_pagamento, name='pagina_pagamento'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

