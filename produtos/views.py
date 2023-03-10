from django.db.models import Count

from cart.models import Cart
from django.shortcuts import render, get_object_or_404

from pedidos.models import PedidoItem, Pedido
from .models import Category, Subcategory, Produto
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect

from tiny_erp.tiny_api import import_products


from tiny_erp.tiny_api import import_products



from django.http import JsonResponse
from django.views.decorators.http import require_GET



@require_GET
def search(request):
    query = request.GET.get('q', '')
    products = Produto.objects.filter(name__icontains=query)
    data = {'results': []}
    for product in products:
        has_variation = product.variation_set.exists()
        url= product.get_absolute_url()
        product_data = {'id': product.id, 'name': product.name, 'url': url, 'price': product.price, 'image_url': product.image.url, 'has_variation': has_variation}
        variations = []
        if product.variation_set.exists():
            for variation in product.variation_set.all():
                if variation.nome_simplificado:
                    variation_data = {'id': variation.id, 'name': variation.nome_simplificado, 'price': variation.price}
                else:
                    variation_data = {'id': variation.id, 'name': variation.name, 'price': variation.price}
                variations.append(variation_data)
            product_data['variations'] = variations
        data['results'].append(product_data)
    print(product_data)
    return JsonResponse(data)



def pagina_search(request, q):
    query = q
    products = Produto.objects.filter(name__icontains=query)

    context= { "products": products}

    return  render(request, 'pagina_search.html', context)


def import_products_view(request):
    if request.method == 'GET':
        import_products()
        return HttpResponse('Produtos importados com sucesso!')

# def import_products_view(request):
#     import_products()
#     return redirect('admin:produtos_produto_changelist')


def produto_por_subcategoria(request, category_id, subcategory_id):
    category = Category.objects.all()
    subcategoria = Subcategory.objects.all()
    category_filter = get_object_or_404(Category, pk=category_id)
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    produtos = Produto.objects.filter(category=category_filter, subcategory=subcategory)
    produtos_por_pagina = 20
    paginator = Paginator(produtos, produtos_por_pagina)
    pagina_numero = request.GET.get('pagina')
    pagina = paginator.get_page(pagina_numero)
    total_quantity_cart = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass

    context = {
        'category_filter': category_filter,
         'subcategory': subcategory,
         'produtos': produtos,
         'pagina': pagina,
        'total_quantity_cart': total_quantity_cart,
        'subcategoria': subcategoria,
        'category': category,
    }
    return render(request, 'produto_por_subcategoria.html', context)


def product_detail(request, slug):
    # Obter o produto
    produto = get_object_or_404(Produto, slug=slug)

    # Obter o pedido item correspondente
    pedido_itens = PedidoItem.objects.filter(product=produto)

    # Obtenha todos os pedidos que cont??m o item em quest??o
    # Obtenha todos os pedidos que cont??m o produto em quest??o
    orders = Pedido.objects.filter(itens__in=pedido_itens, status="Pago").order_by().values_list('itens', flat=True).distinct()

    # Obtenha todos os outros itens que aparecem nos mesmos pedidos que o item em quest??o
    related_item_ids = PedidoItem.objects.filter(pedido__in=orders).exclude(product=produto).annotate(
        count=Count('product')).order_by('-count')

    related_items = Produto.objects.filter(pedidoitem__in=related_item_ids).distinct()[:4]
    print(related_items, "RELATED ITENS")
    # Ordene o dicion??rio pelos valores em ordem decrescente para obter os itens mais comuns


    category = Category.objects.all()
    subcategoria = Subcategory.objects.all()
    produto = get_object_or_404(Produto, slug=slug)
    total_quantity_cart = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass

    context = {
        'related_products': related_items,
        'product': produto,
        'total_quantity_cart': total_quantity_cart,
        'subcategoria': subcategoria,
        'category': category,
    }
    return render(request, 'product_detail.html', context)

