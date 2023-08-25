# xflavors_site_final

django_migrations, sqlite_sequence, frontend_banner, frontend_bannermenor, produtos_kit, produtos_materiaprima, cart_cupom:
    - Não possuem chaves estrangeiras.

auth_user:
    |
    ├── user_id ──> cart_cart
    ├── user_id ──> auth_user_groups
    ├── user_id ──> auth_user_user_permissions
    ├── user_id ──> django_admin_log
    ├── user_id ──> clientes_cliente
    ├── user_id ──> pedidos_enderecopedido
    └── user_id ──> pedidos_pedido

auth_group:
    |
    ├── group_id ──> auth_group_permissions
    └── group_id ──> auth_user_groups

auth_permission:
    └── content_type_id ──> django_content_type

django_content_type:
    |
    ├── content_type_id ──> django_admin_log
    └── content_type_id ──> auth_permission

cart_cart:
    |
    ├── cart_id ──> cart_cartitem
    ├── cart_id ──> cart_cart_variations
    └── cart_id ──> pedidos_order

cart_cartitem:
    |
    ├── product_id ──> produtos_produto
    └── variation_id ──> produtos_variation

clientes_enderecoentrega:
    └── cliente_id ──> clientes_cliente

produtos_category:
    |
    ├── category_id ──> produtos_subcategory
    └── category_id ──> cart_cupom_categorias_aplicaveis

produtos_subcategory:
    └── subcategory_id ──> produtos_produto

produtos_produto:
    |
    ├── product_id ──> cart_cartitem
    ├── product_id ──> pedidos_pedidoitem
    ├── product_id ──> avise_avisoestoque
    ├── product_id ──> produtos_favorito_produto
    └── product_id ──> cart_cupom_produtos_aplicaveis

produtos_variation:
    |
    ├── variation_id ──> cart_cart_variations
    ├── variation_id ──> cart_cartitem
    ├── variation_id ──> pedidos_pedidoitem
    └── variation_id ──> produtos_kit_variacoes

clientes_cliente:
    └── cliente_id ──> produtos_favorito

produtos_favorito:
    └── favorito_id ──> produtos_favorito_produto

pedidos_pedido:
    └── pedido_id ──> pedidos_pedido_itens

cart_cupom:
    |
    ├── cupom_id ──> cart_cart
    ├── cupom_id ──> cart_cupom_categorias_aplicaveis
    └── cupom_id ──> cart_cupom_produtos_aplicaveis

