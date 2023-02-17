from cart.models import Cart
from produtos.models import Category, Subcategory, Produto


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
