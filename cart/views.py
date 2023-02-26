from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from pedidos.models import Order
from produtos.models import Produto,Variation
from cart.models import Cart, CartItem

from django.http import HttpResponseBadRequest, JsonResponse


class CartView(TemplateView):
    template_name = "carrinho.html"



def carrinho(request):
    cart = Cart.objects.get(user=request.user)
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass


    itens = cart.cartitem_set.all()
    # Calcula o valor total dos itens no carrinho
    total = 0
    for item in itens:
        if item.variation:
            preco= item.variation.price
        else:
            preco = item.product.price
        total += item.quantity * preco

    return render(request, 'carrinho.html', {'itens': itens, 'total': total, 'total_quantity_cart':total_quantity_cart})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def add_to_cart_carrocel(request):

    product_id = request.POST.get('productId')
    print("product_id",product_id)
    quantity = request.POST.get('quantity')
    print("quantidade",quantity)

    variation_id = request.POST.get('variation_id')
    print('variacao', variation_id)
    user = request.user
    print("usuario",user)
    product = get_object_or_404(Produto, id=product_id)
    cart = Cart.get_or_create_cart(user)
    print("quantidade",quantity)
    quantity = int(quantity)
    product_name = product.name

    if variation_id:
        variation = get_object_or_404(Variation, id=variation_id)
        # Verificar se a variação pertence ao produto atual
        if variation.produto_pai != product:
            return JsonResponse({'success': False,
                                 'error': 'Desculpe, essa variação não está disponível para esse produto.'})
    else:
        variation = None

    cart = Cart.get_or_create_cart(user)
    quantity = int(request.POST.get('quantity', 1))


    if quantity > product.stock:
        return JsonResponse({'success': False,
                             'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.'})

    try:

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variation=variation
        )

        # Verificar se já existe um item no carrinho com o mesmo produto e variação
        existing_items = CartItem.objects.filter(cart=cart, product=product, variation=variation)
        if existing_items.exists():
            quantidade_no_carrinho = existing_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_quantity = quantity + quantidade_no_carrinho
            if total_quantity > product.stock:
                return JsonResponse({'success': False,
                                     'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis e tem {quantidade_no_carrinho} unidades no seu carrinho.'})
            item = existing_items.first()

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        message = f'{quantity} unidade' if quantity == 1 else f'{quantity} unidades'
        if variation:
            return JsonResponse({'success': True,
                                 'produto_adicionado': f'{message} da variação {variation.name} adicionado ao carrinho com sucesso',
                                 'variacao_adicionada': variation.name})
        else:
            return JsonResponse({'success': True,
                                 'produto_adicionado': f'{message} do produto {product.name} adicionado ao carrinho com sucesso'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def add_to_cart(request, product_id):

    user = request.user
    product = get_object_or_404(Produto, id=product_id)
    variation_id = request.POST.get('variation')

    if variation_id:
        variation = get_object_or_404(Variation, id=variation_id)
        # Verificar se a variação pertence ao produto atual
        if variation.produto_pai != product:
            return JsonResponse({'success': False,
                                 'error': 'Desculpe, essa variação não está disponível para esse produto.'})
    else:
        variation = None

    cart = Cart.get_or_create_cart(user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        return JsonResponse({'success': False,
                             'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.'})

    try:
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variation=variation
        )

        # Verificar se já existe um item no carrinho com o mesmo produto e variação
        existing_items = CartItem.objects.filter(cart=cart, product=product, variation=variation)
        if existing_items.exists():
            quantidade_no_carrinho = existing_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_quantity = quantity + quantidade_no_carrinho
            if total_quantity > product.stock:
                return JsonResponse({'success': False,
                                     'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis e tem {quantidade_no_carrinho} unidades no seu carrinho.'})
            item = existing_items.first()

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        message = f'{quantity} unidade' if quantity == 1 else f'{quantity} unidades'
        if variation:
            return JsonResponse({'success': True,
                                 'produto_adicionado': f'{message} da variação {variation.name} adicionado ao carrinho com sucesso',
                                 'variacao_adicionada': variation.name})
        else:
            return JsonResponse({'success': True,
                                 'produto_adicionado': f'{message} do produto {product.name} adicionado ao carrinho com sucesso'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



# def add_to_cart(request, product_id):
#   user = request.user
#   product = get_object_or_404(Produto, id=product_id)
#   cart = Cart.get_or_create_cart(user)
#   quantity = int(request.POST.get('quantity', 1))
#
#
#   if quantity > product.stock:
#       return JsonResponse({'success': False,
#                            'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.'})
#   try:
#     Cart.add_item_to_cart(cart, product, request.POST.get('quantity', 1))
#     message = f'{quantity} unidade' if quantity == 1 else f'{quantity} unidades'
#     return JsonResponse({'success': True,
#                          'produto_adicionado': f'{message} do produto {product.name} adicionado ao carrinho com sucesso'})
#   except Exception as e:
#     return JsonResponse({'success': False})

def update_item(request):
    cart = get_object_or_404(Cart, user=request.user)
    product_id = request.POST.get('product_id', None)
    variation_id = request.POST.get('variation_id', None)
    quantity = request.POST.get('quantity', None)
    if cart and product_id and quantity:
        try:
            if variation_id:
                item = CartItem.objects.get(cart=cart, product__id=product_id, variation__id=variation_id)
                item.quantity = quantity
                item.save()
            else:
                item = CartItem.objects.get(cart=cart, product__id=product_id)
                item.quantity = quantity
                item.save()

            return JsonResponse({'status': 'success'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho'})
    return JsonResponse({'status': 'error', 'message': 'Dados insuficientes para atualizar item'})


def remove_item(request):
    cart = get_object_or_404(Cart, user=request.user)
    product_id= request.POST.get('product_id', 1)
    variation_id = request.POST.get('variation_id', None)
    print('aqui',variation_id)
    if cart:
        try:
            if variation_id:
                item = CartItem.objects.get(cart=cart, product__id=product_id, variation__id=variation_id)
                item.delete()
            else:
                item = CartItem.objects.get(cart=cart, product__id=product_id)
                item.delete()


            return JsonResponse({'status': 'success'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho'})
    return JsonResponse({'status': 'error', 'message': 'Carrinho não encontrado'})


def clear_cart(request):
    pedido = Order.objects.get_or_create_from_request(request)
    pedido.itens.all().delete()
    return redirect('carrinho:carrinho')
