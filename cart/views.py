from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from pedidos.models import Order
from produtos.models import Produto,Variation
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse


class CartView(TemplateView):
    template_name = "carrinho.html"


@login_required
def carrinho(request):
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass

    itens = cart.cartitem_set.all() if cart else []

    # Calcula o valor total dos itens no carrinho
    total = 0
    for item in itens:
        if item.variation:
            preco = item.variation.price
        else:
            preco = item.product.price
        total += item.quantity * preco

    total_do_item = item.quantity * item.product.price if itens else 0

    return render(request, 'carrinho.html', {'itens': itens, 'total': total, 'total_quantity_cart': total_quantity_cart, 'total_do_item': total_do_item})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def add_to_cart_carrocel(request):
    if not request.user.is_authenticated:

        return JsonResponse({'success': False, 'login_required': True,
                             'error': 'Por favor, faça login ou cadastre-se para adicionar produtos ao carrinho.'})

    product_id = request.POST.get('productId')

    variation_id = request.POST.get('variation_id')
    user = request.user
    product = get_object_or_404(Produto, id=product_id)
    cart = Cart.get_or_create_cart(user)
    quantity = int(request.POST.get('quantity', 1))
    if variation_id:

        variation = get_object_or_404(Variation, id=variation_id)
        quantidade_materia_prima = variation.materia_prima.stock
        materia_prima_id= variation.materia_prima.id
        quantity = int(quantity)
        # print(quantity, quantidade_materia_prima, 'TESEEEEEEE')
        # Verificar se a variação pertence ao produto atual
        if variation.produto_pai != product:
            return JsonResponse({'success': False,
                                 'error': 'Desculpe, essa variação não está disponível para esse produto.'})
    else:
        variation = None
        quantidade_materia_prima = product.stock
        materia_prima_id = product.id

    if variation:
        try:
            verifica_qunatidade_carrinho_varivel(quantity,quantidade_materia_prima,variation,cart,materia_prima_id,product)
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})

        success, message = cria_item_carrinho(cart, product, variation, quantity)
        if success:
            return JsonResponse({'success': True, 'produto_adicionado': message})
        else:
            return JsonResponse({'success': False, 'error': message})


    else:
        if quantity > product.stock:
            return JsonResponse({'success': False,
                                 'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.'})

        else:
            try:
                verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                     materia_prima_id, product)
            except ValueError as e:
                return JsonResponse({'success': False, 'error': str(e)})
            success, message = cria_item_carrinho(cart, product, variation, quantity)
            if success:
                return JsonResponse({'success': True, 'produto_adicionado': message})
            else:
                return JsonResponse({'success': False, 'error': message})




def verifica_qunatidade_carrinho_varivel(quantity,quantidade_materia_prima,variation,cart,materia_prima_id,product,fechamento=1, update=False):
    if variation:
        print('passou por aqui')
        if quantity > quantidade_materia_prima:
            print('passou por aqui 1')
            raise ValueError(
                f'Desculpe, não há estoque suficiente do produto {variation.name}. Somente {variation.materia_prima.stock} unidades disponíveis.')
        existing_items = CartItem.objects.filter(cart=cart, variation__materia_prima_id=materia_prima_id)

        # Multiplicar a quantidade pelo gasto e somar as quantidades de todas as CartItems encontradas
        quantidade_no_carrinho = sum(
            existing_item.quantity * existing_item.variation.gasto for existing_item in existing_items)
        # print(quantidade_no_carrinho, 'quantidade no carrinho')
        if fechamento == 2:
            total_quantity = quantidade_no_carrinho
            # print(total_quantity, 'TQ', quantity, 'Q', quantidade_no_carrinho, 'QnC')
            print(quantidade_no_carrinho, 'quantidade_no_carrinho')
            print(total_quantity, 'total_quantity')
        else:
            total_quantity = quantity * variation.gasto + quantidade_no_carrinho
            # print(total_quantity, 'TQ', quantity, 'Q', quantidade_no_carrinho, 'QnC')
            print(quantidade_no_carrinho, 'quantidade_no_carrinho')
            print(total_quantity, 'total_quantity')

        if total_quantity > quantidade_materia_prima:
            print('passou por aqui 2')
            raise ValueError(
                f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {variation.materia_prima.stock} {variation.materia_prima.unidade} disponíveis e tem {quantidade_no_carrinho} mls no seu carrinho.')
    # CASO O ITEM NAO TENHA VARIATION
    else:
        print('passou por aqui produto')
        if quantity > quantidade_materia_prima:
            print('passou por aqui 1 produto')
            raise ValueError(
                f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.')
        existing_items = CartItem.objects.filter(cart=cart, product=materia_prima_id)

        # Multiplicar a quantidade pelo gasto e somar as quantidades de todas as CartItems encontradas
        quantidade_no_carrinho = sum(
            existing_item.quantity * 1 for existing_item in existing_items)
        # print(quantidade_no_carrinho, 'quantidade no carrinho')
        if fechamento == 2:
            total_quantity = quantidade_no_carrinho
            # print(total_quantity, 'TQ', quantity, 'Q', quantidade_no_carrinho, 'QnC')
            print(quantidade_no_carrinho, 'quantidade_no_carrinho')
            print(total_quantity, 'total_quantity')
        else:
            total_quantity = quantity + quantidade_no_carrinho
            # print(total_quantity, 'TQ', quantity, 'Q', quantidade_no_carrinho, 'QnC')
            print(quantidade_no_carrinho, 'quantidade_no_carrinho')
            print(total_quantity, 'total_quantity')

        if update:
            pass
        else:
            if total_quantity > quantidade_materia_prima:
                print('passou por aqui 2 produto')
                raise ValueError(
                    f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis e tem {quantidade_no_carrinho} unidades no seu carrinho.')


def cria_item_carrinho(cart,product,variation,quantity):
    try:
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variation=variation,
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        message = f'{quantity} unidade' if quantity == 1 else f'{quantity} unidades'
        if variation:
            success_msg = f'{message} da variação {variation.name} adicionado ao carrinho com sucesso'
        else:
            success_msg = f'{message} do produto {product.name} adicionado ao carrinho com sucesso'

        return (True, success_msg)

    except Exception as e:
        error_msg = str(e)
        return (False, error_msg)


def update_item(request):
    print('UPDATE_ITEM')
    cart = get_object_or_404(Cart, user=request.user)
    product_id = request.POST.get('product_id', None)
    variation_id = request.POST.get('variation_id', None)
    quantity = request.POST.get('quantity', None)
    if cart and product_id and quantity:

        try:
            if variation_id:

                product = get_object_or_404(Produto, id=product_id)
                variation = get_object_or_404(Variation, id=variation_id)
                quantidade_materia_prima = variation.materia_prima.stock
                materia_prima_id = variation.materia_prima.id
                quantity = int(quantity)
                fechamento = 2
                try:
                    verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                         materia_prima_id, product, fechamento, update=True)
                except ValueError as e:
                    return JsonResponse({'success': False, 'error': str(e)})

                item = CartItem.objects.get(cart=cart, product__id=product_id, variation__id=variation_id)
                item.quantity = quantity
                item.save()
                return JsonResponse({'success': True, 'mensagem': 'item atualizado'})

            else:

                product = get_object_or_404(Produto, id=product_id)
                quantity = int(quantity)
                variation = None
                quantidade_materia_prima = product.stock
                materia_prima_id = product.id
                fechamento = 2
                try:
                    verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                         materia_prima_id, product, fechamento, update=True)
                except ValueError as e:
                    return JsonResponse({'success': False, 'error': str(e)})


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
