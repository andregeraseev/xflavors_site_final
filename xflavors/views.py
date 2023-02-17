from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

from cart.models import Cart

from produtos.models import Produto, Category, Subcategory


def index(request):
    category = Category.objects.all()
    subcategoria = Subcategory.objects.all()
    products = Produto.objects.all()
    cart = None
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass
    print(total_quantity_cart)
    context = {'products': products,
               'cart': cart,
               'subcategoria': subcategoria,
               'category': category,
               'total_quantity_cart': total_quantity_cart
               }
    return render(request, 'index.html', context)
