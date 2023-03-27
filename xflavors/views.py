from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

from cart.models import Cart
from frontend.models import Banner, BannerMenor

from produtos.models import Produto, Category, Subcategory
from pedidos.models import Pedido


def index(request):
    # Filtra os pedidos que estão com o status 'Pago' e obtém os IDs dos produtos nos itens desses pedidos
    products_in_orders = Pedido.objects.filter(status='Pago').values_list('itens__product', flat=True).distinct()
    print(products_in_orders,'PEDIDOS')
    # Obtém a contagem de cada produto que aparece nos pedidos filtrados anteriormente
    # A contagem é feita pela soma das quantidades de cada produto em todos os itens dos pedidos
    produtos_mais_vendidos = Produto.objects.filter(pk__in=products_in_orders).annotate(
        count=Sum('pedidoitem__quantity')
    ).order_by('-count')

    essencias_mais_vendidos = Produto.objects.filter(
        pk__in=products_in_orders, category__name='Essencias'
    ).annotate(
        count=Sum('pedidoitem__quantity')
    ).order_by('-count')[:10]



    category = Category.objects.all()
    subcategoria = Subcategory.objects.all()
    produtos_mais_vendidos = produtos_mais_vendidos
    # products = product_counts
    cart = None
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass


    active_banners_menor = BannerMenor.objects.filter(active=True)
    active_banners = Banner.objects.filter(active=True)

    context = {
        'essencias_mais_vendidos': essencias_mais_vendidos,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'active_banners_menor': active_banners_menor,
        'active_banners': active_banners,
        # 'products': products,
        'cart': cart,
        'subcategoria': subcategoria,
        'category': category,
        'total_quantity_cart': total_quantity_cart
    }
    return render(request, 'index.html', context)

