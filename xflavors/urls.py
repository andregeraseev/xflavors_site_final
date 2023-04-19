from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from clientes import views
from frontend.views import termos, envio
from produtos.views import product_detail, produto_por_subcategoria, import_products_view, search, pagina_search, add_to_favorites, receitas, adicionar_kit_ao_carrinho, kit_detail
from .views import index
from cart.views import add_to_cart_carrocel,verifica_qunatidade_carrinho_varivel
from tiny_erp.webhook import tiny_webhook
from tiny_erp.webhook_estoque import tiny_webhook_stock_update
from tiny_erp.webhook_rastreio import tiny_rastreio
from pedidos.views import checkout,  atualizar_endereco_entrega, editar_endereco, cotacao_frete_correios,criar_pedido,\
    pagina_pagamento, visualizar_pedidos,detalhes_pedido,paga_pix,payment_success,verifica_carrinho, success,failure,pending, validar_cupom, remover_cupom
from mercado_pago.mercado_livre_weebhook import mercado_pago_webhook
from Importador.clientes import ImportClientesView
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('cart/', include('cart.urls', namespace='cart')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('administracao/', include('administracao.urls', namespace='administracao')),
    path('avise/', include('avise.urls', namespace='avise')),
    path('', index, name='home'),
    path('import_products/', import_products_view, name='import_products'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/cadastro/', views.cadastro, name='cadastro'),
    # path('carrinho/', views.carrinho, name='carrinho'),
    path('add_to_cart_carrocel/', add_to_cart_carrocel, name='add_to_cart_carrocel'),
    # path('add_to_cart/', add_to_cart, name='add_to_cart'),

    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('add_to_favorites/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('categoria/<int:category_id>/subcategoria/<int:subcategory_id>/', produto_por_subcategoria, name='produto_por_subcategoria'),
    path('checkout/', checkout, name='checkout'),
    # path('processar_pagamento/', processar_pagamento, name='processar_pagamento'),
    path('atualizar_endereco_entrega/', atualizar_endereco_entrega, name='atualizar_endereco_entrega'),
    path('editar_endereco/', editar_endereco, name='editar_endereco'),
    path('cotacao_frete_correios/', cotacao_frete_correios, name='cotacao_frete_correios'),
    path('validar_cupom/', validar_cupom, name='validar_cupom'),
    path('remover_cupom/', remover_cupom, name='remover_cupom'),

    path('criar_pedido/', criar_pedido, name='criar_pedido'),
    path('pagina_pagamento/<int:pedido_id>', pagina_pagamento, name='pagina_pagamento'),
    path('visualizar_pedidos', visualizar_pedidos, name='visualizar_pedidos'),
    path('detalhes_pedido/<int:pedido_id>', detalhes_pedido, name='detalhes_pedido'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('alterar_celular/', views.alterar_celular, name='alterar_celular'),
    path('alterar_cpf/', views.alterar_cpf, name='alterar_cpf'),
    path('adicionar_endereco_dashboard', views.adicionar_endereco_dashboard, name='adicionar_endereco_dashboard'),
    path('editar_endereco_dashboard/', views.editar_endereco_dashboard, name='editar_endereco_dashboard'),
    path('excluir_endereco_dashboard/', views.excluir_endereco_dashboard, name='excluir_endereco_dashboard'),
    path('toggle_propaganda/', views.toggle_propaganda, name='toggle_propaganda'),




    path('paga_pix/', paga_pix, name='paga_pix'),
    path('pagamento/sucesso/<int:pedido_id>', payment_success, name='payment_success'),
    path('import_products/', import_products_view, name='import_products'),
    path('verificar_quantidade_carrinho/', verifica_qunatidade_carrinho_varivel, name='verificar_quantidade_carrinho'),
    path('verifica_carrinho/', verifica_carrinho, name='verifica_carrinho'),

    # MERCADO PAGO

    path('success/', success, name='success'),
    path('failure/', failure, name='failure'),
    path('pending/', pending, name='pending'),
    path('webhook/mercado-pago/', mercado_pago_webhook, name='mercado_pago_webhook'),

# PESQUISA
    path('search/', search, name='search'),
    path('pagina_search/<str:q>', pagina_search, name='pagina_search'),

# verificar
    path('verificar_email/', views.verificar_email, name='verificar_email'),
    path('verificar_cpf/', views.verificar_cpf, name='verificar_cpf'),
    path('verificar_nome/', views.verificar_nome, name='verificar_nome'),

    # TINY
    path("webhooks/tiny/", tiny_webhook, name="tiny_webhook"),
    path('webhooks/tiny_rastreio/', tiny_rastreio, name='tiny_rastreio'),
    path('webhooks/tiny_webhook_stock/', tiny_webhook_stock_update, name='tiny_webhook_stock_update'),


#     Termos
    path('termos/', termos, name='termos'),
    path('envio/', envio, name='envio'),


# importacao
    path('importar/', ImportClientesView.as_view(), name='importar'),

# resetpassword
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/', include('django.contrib.auth.urls')),


# receitas
    path('receitas/', receitas, name='receitas'),
    path('adicionar_kit_ao_carrinho/', adicionar_kit_ao_carrinho, name='adicionar_kit_ao_carrinho'),
    path('receitas/<slug:slug>/', kit_detail, name='kit_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

