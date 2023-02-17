from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView
from produtos.models import Produto
from .forms import EnderecoEntregaForm
from .models import Order
from cart.models import CartItem, Cart
from clientes.models import EnderecoEntrega
from clientes.models import Cliente

from django.shortcuts import render, redirect
from clientes.models import EnderecoEntrega

from django.shortcuts import get_object_or_404
def checkout(request):
    user = request.user
    cart = Cart.get_or_create_cart(user)
    itens = cart.cartitem_set.all()

    total = 0
    for item in itens:
        if item.variation:
            preco= item.variation.price
        else:
            preco = item.product.price
        total += item.quantity * preco

    # Verifica se o usuário está autenticado e se existe um objeto Cliente correspondente a ele
    if user.is_authenticated and hasattr(user, 'cliente'):
        enderecos = user.cliente.enderecoentrega_set.all()
        endereco_primario = enderecos.filter(primario=True).first()
        print(enderecos)

    return render(request, 'pedidos/checkout.html', {'cart': cart, 'total': total, 'endereco': enderecos, 'endereco_primario': endereco_primario, 'itens': itens})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from clientes.models import EnderecoEntrega
from pedidos.models import Pedido


@login_required
def processar_pagamento(request):
    # Obtém o carrinho e o endereço de entrega do usuário
    cart = Cart(request)
    endereco = request.user.cliente.enderecoentrega if hasattr(request.user, 'cliente') else None

    # Obtém o método de pagamento escolhido pelo cliente
    metodo_pagamento = request.POST.get('metodo_pagamento', None)

    if metodo_pagamento == 'cartao':
        # Processa o pagamento via cartão de crédito
        # Aqui você poderia adicionar a lógica para processar o pagamento via cartão de crédito
        # ...

        # Cria um novo pedido com as informações do carrinho e do endereço de entrega
        pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)

        # Limpa o carrinho do usuário
        cart.clear()

        # Redireciona o usuário para a página de confirmação do pedido
        messages.success(request, 'Seu pedido foi realizado com sucesso.')
        return redirect('pedido_confirmado', pedido_id=pedido.id)

    elif metodo_pagamento == 'pix':
        # Processa o pagamento via PIX
        # Aqui você poderia adicionar a lógica para processar o pagamento via PIX
        # ...

        # Cria um novo pedido com as informações do carrinho e do endereço de entrega
        pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)

        # Limpa o carrinho do usuário
        cart.clear()

        # Redireciona o usuário para a página de confirmação do pedido
        messages.success(request, 'Seu pedido foi realizado com sucesso.')
        return redirect('pedido_confirmado', pedido_id=pedido.id)

    elif metodo_pagamento == 'deposito':
        # Processa o pagamento via depósito bancário
        # Aqui você poderia adicionar a lógica para processar o pagamento via depósito bancário
        # ...

        # Cria um novo pedido com as informações do carrinho e do endereço de entrega
        pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)

        # Limpa o carrinho do usuário
        cart.clear()

        # Redireciona o usuário para a página de confirmação do pedido

        return redirect('confirmacao_pedido', pedido_id=pedido.id)
    else:
        form = EnderecoEntregaForm()

    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'pedidos/checkout.html', context)


@login_required

def editar_endereco(request):
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')

        try:
            endereco = EnderecoEntrega.objects.get(id=endereco_id)
            endereco.rua = rua
            endereco.numero = numero
            endereco.complemento = complemento
            endereco.bairro = bairro
            endereco.cidade = cidade
            endereco.estado = estado
            endereco.cep = cep
            endereco.save()
            messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('checkout')
        except EnderecoEntrega.DoesNotExist:
            messages.error(request, 'Endereço não encontrado.')
            return redirect('checkout')



    endereco_id = request.GET.get('endereco_id')
    endereco = get_object_or_404(EnderecoEntrega, pk=endereco_id, cliente=request.user.cliente)
    return render(request, 'editar_endereco.html', {'endereco': endereco})



def atualizar_endereco_entrega(request):
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        cliente = request.user.cliente
        # Define o endereço selecionado como primário
        endereco = EnderecoEntrega.objects.get(id=endereco_id)
        endereco.primario = True
        endereco.save()
        # Definir os outros endereços como não primários
        outros_enderecos = EnderecoEntrega.objects.exclude(id=endereco_id)
        for e in outros_enderecos:
            e.primario = False
            e.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Método inválido.'})


from django.shortcuts import render

from .models import Pedido

def confirmacao_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    return render(request, 'pedidos/confirmacao_pedido.html', {'pedido': pedido})
