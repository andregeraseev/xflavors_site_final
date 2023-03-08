from cart.models import Cart
from django.shortcuts import render, get_object_or_404
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
    query = request.GET.get('q')
    results = []
    if query:
        products = Produto.objects.filter(name__icontains=query)[:10]
        print(products)
        for product in products:


            result = {
                'name': product.name,
                'url': product.get_absolute_url(),
                'image_url': product.image.url,

            }
            results.append(result)
    return JsonResponse({'results': results})




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
        'product': produto,
        'total_quantity_cart': total_quantity_cart,
        'subcategoria': subcategoria,
        'category': category,
    }
    return render(request, 'product_detail.html', context)

