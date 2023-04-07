from cart.models import Cart
from clientes.models import Cliente
from produtos.models import Category, Subcategory, Produto, Favorito
from django.shortcuts import get_object_or_404

def categorias(request):

    return {'categorias': Category.objects.all()}

def subcategoria(request):
    subcategoria = Subcategory.objects.all()
    return {'subcategoria': Subcategory.objects.all()}

def products(request):
    products = Produto.objects.all()
    return {'products' : Produto.objects.all()}

def cart(request):
    cart = None
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass
    return {'cart': cart }

def total_quantity_cart(request):
    cart = None
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass
    return {'total_quantity_cart': total_quantity_cart}

def favoritos(request):
    try:
        cliente = get_object_or_404(Cliente, user=request.user)
        favoritos = Favorito.objects.filter(cliente=cliente).values_list('produto__id', flat=True)
    except:
        favoritos = []
    return {'favoritos': favoritos}