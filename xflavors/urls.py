from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from clientes import views
from produtos.views import product_detail, produto_por_subcategoria, import_products_view, search, pagina_search
from .views import index
from cart.views import add_to_cart_carrocel,verifica_qunatidade_carrinho_varivel
from tiny_erp.webhook import tiny_webhook, tiny_rastreio
from tiny_erp.webhook_estoque import tiny_webhook_stock_update
from pedidos.views import checkout,  atualizar_endereco_entrega, editar_endereco, cotacao_frete_correios,criar_pedido,\
    pagina_pagamento, visualizar_pedidos,detalhes_pedido,paga_pix,payment_success,verifica_carrinho, success,failure,pending

urlpatterns = [
    path('admin/', admin.site.urls),
    path('termos/', views.termos, name='termos'),
    path('cart/', include('cart.urls', namespace='cart')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('administracao/', include('administracao.urls', namespace='administracao')),
    path('', index, name='home'),
    path('import_products/', import_products_view, name='import_products'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/cadastro/', views.cadastro, name='cadastro'),
    # path('carrinho/', views.carrinho, name='carrinho'),
    path('add_to_cart_carrocel/', add_to_cart_carrocel, name='add_to_cart_carrocel'),
    # path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('categoria/<int:category_id>/subcategoria/<int:subcategory_id>/', produto_por_subcategoria, name='produto_por_subcategoria'),
    path('checkout/', checkout, name='checkout'),
    # path('processar_pagamento/', processar_pagamento, name='processar_pagamento'),
    path('atualizar_endereco_entrega/', atualizar_endereco_entrega, name='atualizar_endereco_entrega'),
    path('editar_endereco/', editar_endereco, name='editar_endereco'),
    path('cotacao_frete_correios/', cotacao_frete_correios, name='cotacao_frete_correios'),
    path('criar_pedido/', criar_pedido, name='criar_pedido'),
    path('pagina_pagamento/<int:pedido_id>', pagina_pagamento, name='pagina_pagamento'),
    path('visualizar_pedidos', visualizar_pedidos, name='visualizar_pedidos'),
    path('detalhes_pedido/<int:pedido_id>', detalhes_pedido, name='detalhes_pedido'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('alterar_celular/', views.alterar_celular, name='alterar_celular'),
    path('adicionar_endereco_dashboard', views.adicionar_endereco_dashboard, name='adicionar_endereco_dashboard'),
    path('editar_endereco_dashboard/', views.editar_endereco_dashboard, name='editar_endereco_dashboard'),
    path('paga_pix/', paga_pix, name='paga_pix'),
    path('pagamento/sucesso/<int:pedido_id>', payment_success, name='payment_success'),
    path('import_products/', import_products_view, name='import_products'),
    path('verificar_quantidade_carrinho/', verifica_qunatidade_carrinho_varivel, name='verificar_quantidade_carrinho'),
    path('verifica_carrinho/', verifica_carrinho, name='verifica_carrinho'),

    # MERCADO PAGO

    path('success/', success, name='success'),
    path('failure/', failure, name='failure'),
    path('pending/', pending, name='pending'),


# PESQUISA
    path('search/', search, name='search'),
    path('pagina_search/<str:q>', pagina_search, name='pagina_search'),

# verificar
    path('verificar_email/', views.verificar_email, name='verificar_email'),


    # TINY
    path("webhooks/tiny/", tiny_webhook, name="tiny_webhook"),
     path('webhooks/tiny_rastreio/', tiny_rastreio, name='tiny_rastreio'),
    path('webhooks/tiny_webhook_stock_update/', tiny_webhook_stock_update, name='tiny_webhook_stock_update'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

