from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from pedidos.models import Order
from produtos.models import Produto,Variation
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
import logging

# Configuração inicial para logs
logger = logging.getLogger(__name__)

class CartView(TemplateView):
    template_name = "carrinho.html"


def preco_item(item):
    if item.variation:
        preco = item.variation.preco_ou_valor_promocional
    else:
        preco = item.product.preco_ou_valor_promocional

    return preco

@login_required
def carrinho(request):
    total_quantity_cart = 0

    if request.user.is_authenticated:
        try:
            user = request.user
            cart = Cart.get_or_create_cart(user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass

    itens = cart.cartitem_set.all() if cart else []

    # Calcula o valor total dos itens no carrinho
    total = 0
    for item in itens:
        preco = preco_item(item)
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
    quantity = int(request.POST.get('quantity', 1))

    user = request.user

    try:
        product = Produto.objects.get(id=product_id)
        cart = Cart.get_or_create_cart(user)

        if variation_id:
            variation = Variation.objects.get(id=variation_id)

            # Verificar se a variação pertence ao produto atual
            if variation.produto_pai != product:
                return JsonResponse({'success': False,
                                     'error': 'Desculpe, essa variação não está disponível para esse produto.'})

            pluralizar_unidade = "unidade" if quantity == 1 else "unidades"
            message = f"{quantity} {pluralizar_unidade} do produto {variation.name} foram adicionados ao carrinho!"
        else:
            pluralizar_unidade = "unidade" if quantity == 1 else "unidades"
            variation = None
            message = f"{quantity} {pluralizar_unidade} do produto {product.name} foram adicionadas ao carrinho!"

        cart.add_item(product, quantity, variation)
        return JsonResponse({'success': True, 'produto_adicionado': message})

    except Produto.DoesNotExist:
        logger.error(f"Produto com ID {product_id} não encontrado para usuário {user}.")
        return JsonResponse({'success': False, 'error': 'Produto não encontrado.'})

    except Variation.DoesNotExist:
        logger.error(f"Variação com ID {variation_id} não encontrada para usuário {user}.")
        return JsonResponse({'success': False, 'error': 'Variação não encontrada.'})

    except ValueError as e:
        logger.warning(f"Erro ao adicionar item ao carrinho para o usuário {user}. Detalhes: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

    except Exception as e:
        # Para quaisquer outras exceções não previstas
        logger.error(f"Erro inesperado ao adicionar item ao carrinho para o usuário {user}. Detalhes: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'})



def update_item(request):
    cart = get_object_or_404(Cart, user=request.user)
    product_id = request.POST.get('product_id')
    variation_id = request.POST.get('variation_id')
    quantity = request.POST.get('quantity')
    try:
        success, message = cart.update_item(product_id, quantity, variation_id)
        return JsonResponse({'success': success, 'message': message})
    except ValueError as e:
        print(e)
        return JsonResponse({'success': False, 'error': e})


def remove_item(request):
    cart = get_object_or_404(Cart, user=request.user)
    product_id= request.POST.get('product_id', 1)
    variation_id = request.POST.get('variation_id', None)
    # print('aqui',variation_id)
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

@login_required
def clear_cart(request):
    # Obtém o carrinho do usuário atual
    cart = Cart.objects.get(user=request.user)
    # Remove todos os itens do carrinho
    cart.cartitem_set.all().delete()
    # Redireciona o usuário para a página do carrinho vazio
    return redirect('cart:carrinho')


#
# def add_to_cart_carrocel(request):
#     if not request.user.is_authenticated:
#
#         return JsonResponse({'success': False, 'login_required': True,
#                              'error': 'Por favor, faça login ou cadastre-se para adicionar produtos ao carrinho.'})
#
#     product_id = request.POST.get('productId')
#
#     variation_id = request.POST.get('variation_id')
#     user = request.user
#     product = get_object_or_404(Produto, id=product_id)
#     cart = Cart.get_or_create_cart(user)
#     quantity = int(request.POST.get('quantity', 1))
#     if variation_id:
#
#         variation = get_object_or_404(Variation, id=variation_id)
#         quantidade_materia_prima = variation.materia_prima.stock
#         materia_prima_id= variation.materia_prima.id
#         quantity = int(quantity)
#         # print(quantity, quantidade_materia_prima, 'TESEEEEEEE')
#         # Verificar se a variação pertence ao produto atual
#         if variation.produto_pai != product:
#             return JsonResponse({'success': False,
#                                  'error': 'Desculpe, essa variação não está disponível para esse produto.'})
#     else:
#         variation = None
#         quantidade_materia_prima = product.stock
#         materia_prima_id = product.id
#
#     if variation:
#         try:
#             verifica_qunatidade_carrinho_varivel(quantity,quantidade_materia_prima,variation,cart,materia_prima_id,product)
#         except ValueError as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#
#         success, message = cria_item_carrinho(cart, product, variation, quantity)
#         if success:
#             return JsonResponse({'success': True, 'produto_adicionado': message})
#         else:
#             return JsonResponse({'success': False, 'error': message})
#
#
#     else:
#         if quantity > product.stock:
#             return JsonResponse({'success': False,
#                                  'error': f'Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.'})
#
#         else:
#             try:
#                 verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
#                                                      materia_prima_id, product)
#             except ValueError as e:
#                 return JsonResponse({'success': False, 'error': str(e)})
#             success, message = cria_item_carrinho(cart, product, variation, quantity)
#             if success:
#                 return JsonResponse({'success': True, 'produto_adicionado': message})
#             else:
#                 return JsonResponse({'success': False, 'error': message})




# def verifica_estoque_produto_com_variacao(quantity, variation, cart, update=False):
#
#     if quantity * variation.gasto > variation.materia_prima.stock:
#         raise ValueError(
#             f"Desculpe, não há estoque suficiente do produto {variation.name}. Somente {variation.materia_prima.stock} {variation.materia_prima.unidade} disponíveis.")
#
#     existing_items = CartItem.objects.filter(cart=cart, variation__materia_prima=variation.materia_prima)
#
#     total_quantity_in_cart = sum(existing_item.quantity * existing_item.variation.gasto for existing_item in existing_items)
#     total_quantity = total_quantity_in_cart
#     # print(total_quantity, 'quantidade_total')
#     if not update:
#         total_quantity += quantity * variation.gasto
#     else:
#         total_quantity += (quantity - cart.cartitem_set.get(variation=variation).quantity) * variation.gasto
#
#     print(total_quantity, variation.materia_prima.stock)
#     if total_quantity > variation.materia_prima.stock:
#
#         raise ValueError(
#             f"Desculpe, não há estoque suficiente do produto {variation.name}. Somente {variation.materia_prima.stock} {variation.materia_prima.unidade} disponíveis e tem {total_quantity_in_cart} mls no seu carrinho.")
#
# def verifica_estoque_produto_sem_variacao(quantity, product, cart, update=False):
#     if quantity > product.stock:
#         raise ValueError(
#             f"Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis.")
#
#     existing_items = CartItem.objects.filter(cart=cart, product=product)
#
#     total_quantity_in_cart = sum(existing_item.quantity for existing_item in existing_items)
#     total_quantity = total_quantity_in_cart
#     if not update:
#         # print(" verificando adicao")
#         total_quantity += quantity
#
#     if total_quantity > product.stock:
#         raise ValueError(
#             f"Desculpe, não há estoque suficiente do produto {product.name}. Somente {product.stock} unidades disponíveis e tem {total_quantity_in_cart} unidades no seu carrinho.")


# def verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart, materia_prima_id, product, fechamento=1, update=False):
#     if variation:
#         # print(" verificando quantidade variacao")
#         verifica_estoque_produto_com_variacao(quantity, variation, cart, update)
#     else:
#         # print(" verificando quantidade produto")
# #         verifica_estoque_produto_sem_variacao(quantity, product, cart, update)
#
#
# def cria_item_carrinho(cart,product,variation,quantity):
#     try:
#         item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=product,
#             variation=variation,
#         )
#         if not created:
#             item.quantity += quantity
#         else:
#             item.quantity = quantity
#         item.save()
#
#         message = f'{quantity} unidade' if quantity == 1 else f'{quantity} unidades'
#         if variation:
#             success_msg = f'{message} da variação {variation.name} adicionado ao carrinho com sucesso'
#         else:
#             success_msg = f'{message} do produto {product.name} adicionado ao carrinho com sucesso'
#
#         return (True, success_msg)
#
#     except Exception as e:
#         error_msg = str(e)
#         return (False, error_msg)
#
#
#
# def update_item(request):
#     # print('UPDATE_ITEM')
#     cart = get_object_or_404(Cart, user=request.user)
#     product_id = request.POST.get('product_id', None)
#     variation_id = request.POST.get('variation_id', None)
#     quantity = request.POST.get('quantity', None)
#     if cart and product_id and quantity:
#
#         try:
#             if variation_id:
#
#                 product = get_object_or_404(Produto, id=product_id)
#                 variation = get_object_or_404(Variation, id=variation_id)
#                 quantidade_materia_prima = variation.materia_prima.stock
#                 materia_prima_id = variation.materia_prima.id
#                 quantity = int(quantity)
#                 fechamento = 2
#                 try:
#                     verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
#                                                          materia_prima_id, product, fechamento, update=True)
#                 except ValueError as e:
#                     return JsonResponse({'success': False, 'error': str(e)})
#
#                 item = CartItem.objects.get(cart=cart, product__id=product_id, variation__id=variation_id)
#                 item.quantity = quantity
#                 item.save()
#                 return JsonResponse({'success': True, 'mensagem': 'item atualizado'})
#
#             else:
#
#                 product = get_object_or_404(Produto, id=product_id)
#                 quantity = int(quantity)
#                 variation = None
#                 quantidade_materia_prima = product.stock
#                 materia_prima_id = product.id
#                 fechamento = 2
#                 try:
#                     verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
#                                                          materia_prima_id, product, fechamento, update=True)
#                 except ValueError as e:
#                     return JsonResponse({'success': False, 'error': str(e)})
#
#
#                 item = CartItem.objects.get(cart=cart, product__id=product_id)
#                 item.quantity = quantity
#                 item.save()
#                 return JsonResponse({'success': True, 'mensagem': 'item atualizado'})
#
#         except CartItem.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho'})
#     return JsonResponse({'status': 'error', 'message': 'Dados insuficientes para atualizar item'})

