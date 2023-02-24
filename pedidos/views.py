import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView
from produtos.models import Produto
from .forms import EnderecoEntregaForm
from .models import Order, PedidoItem
from cart.models import CartItem, Cart
from django.contrib.auth.decorators import login_required
from clientes.models import EnderecoEntrega
from clientes.models import Cliente

from django.shortcuts import render, redirect
from clientes.models import EnderecoEntrega



@login_required
def detalhes_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)

    total = 0

    itens = pedido.itens.all()

    for item in itens:
        if item.variation:
            preco = item.variation.price
        else:
            preco = item.product.price
        total += item.quantity * preco
    context = {'pedido': pedido, 'total':total}

    return render(request, 'detalhes_pedido.html', context)

@login_required
def visualizar_pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user)
    context = {'pedidos': pedidos}
    return render(request, 'visualizar_pedidos.html', context)

from django.shortcuts import get_object_or_404
@login_required
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

#
# @login_required
# def processar_pagamento(request):
#     # Obtém o carrinho e o endereço de entrega do usuário
#     cart = Cart(request)
#     endereco = request.user.cliente.enderecoentrega if hasattr(request.user, 'cliente') else None
#
#     # Obtém o método de pagamento escolhido pelo cliente
#     metodo_pagamento = request.POST.get('metodo_pagamento', None)
#
#     if metodo_pagamento == 'cartao':
#         # Processa o pagamento via cartão de crédito
#         # Aqui você poderia adicionar a lógica para processar o pagamento via cartão de crédito
#         # ...
#
#         # Cria um novo pedido com as informações do carrinho e do endereço de entrega
#         pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)
#
#         # Limpa o carrinho do usuário
#         cart.clear()
#
#         # Redireciona o usuário para a página de confirmação do pedido
#         messages.success(request, 'Seu pedido foi realizado com sucesso.')
#         return redirect('pedido_confirmado', pedido_id=pedido.id)
#
#     elif metodo_pagamento == 'pix':
#         # Processa o pagamento via PIX
#         # Aqui você poderia adicionar a lógica para processar o pagamento via PIX
#         # ...
#
#         # Cria um novo pedido com as informações do carrinho e do endereço de entrega
#         pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)
#
#         # Limpa o carrinho do usuário
#         cart.clear()
#
#         # Redireciona o usuário para a página de confirmação do pedido
#         messages.success(request, 'Seu pedido foi realizado com sucesso.')
#         return redirect('pedido_confirmado', pedido_id=pedido.id)
#
#     elif metodo_pagamento == 'deposito':
#         # Processa o pagamento via depósito bancário
#         # Aqui você poderia adicionar a lógica para processar o pagamento via depósito bancário
#         # ...
#
#         # Cria um novo pedido com as informações do carrinho e do endereço de entrega
#         pedido = Pedido.objects.create(user=request.user, endereco_entrega=endereco, itens=cart)
#
#         # Limpa o carrinho do usuário
#         cart.clear()
#
#         # Redireciona o usuário para a página de confirmação do pedido
#
#         return redirect('confirmacao_pedido', pedido_id=pedido.id)
#     else:
#         form = EnderecoEntregaForm()
#
#     context = {
#         'cart': cart,
#         'form': form,
#     }
#     return render(request, 'pedidos/checkout.html', context)


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


@login_required
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


import requests
import xml.etree.ElementTree as ET
import re

@login_required
def cotacao_frete_correios2(endereco):
    cep = endereco.cep
    peso = 0.1  # 100 gramas
    comprimento = 20  # cm
    largura = 20  # cm
    altura = 20  # cm
    valor_declarado = 0
    servico = '40010,41106'  # SEDEX e SEDEX a Cobrar

    dados = f"""
    <servicos>
        <cServico>
            <nCdEmpresa></nCdEmpresa>
            <sDsSenha></sDsSenha>
            <nCdServico>{servico}</nCdServico>
            <sCepOrigem>01010-001</sCepOrigem>
            <sCepDestino>{cep}</sCepDestino>
            <nVlPeso>{peso}</nVlPeso>
            <nCdFormato>1</nCdFormato>
            <nVlComprimento>{comprimento}</nVlComprimento>
            <nVlAltura>{altura}</nVlAltura>
            <nVlLargura>{largura}</nVlLargura>
            <nVlValorDeclarado>{valor_declarado}</nVlValorDeclarado>
            <sCdMaoPropria>N</sCdMaoPropria>
            <nVlDiametro>0</nVlDiametro>
            <sCdAvisoRecebimento>N</sCdAvisoRecebimento>
        </cServico>
    </servicos>
    """

    headers = {
        'Content-Type': 'application/xml',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    try:
        # envia a requisição SOAP e trata a resposta
        response = requests.post('http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx',
                                 headers=headers,
                                 data=dados.encode('utf-8'))

        if response.status_code == 200:
            # parsing do XML retornado
            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()

            servicos = root.findall('.//cServico')

            results = []

            for servico in servicos:
                code = servico.find('Codigo').text
                if code == '0':
                    continue  # erro no serviço

                name = servico.find('Nome').text
                price = float(servico.find('Valor').text.replace(',', '.'))
                days = int(servico.find('PrazoEntrega').text)
                delivery_time = f'{days} dias úteis'

                results.append({
                    'servico': name,
                    'valor': price,
                    'prazo': delivery_time
                })

            return results

        else:
            return None

    except Exception as e:
        return None



import requests
import xml.etree.ElementTree as ET


@login_required
def cotacao_frete_correios(request):
    user = request.user
    cart = Cart.get_or_create_cart(user)
    itens = cart.cartitem_set.all()

    total = 0
    for item in itens:
        if item.variation:
            peso = item.variation.peso
        else:
            peso = item.product.peso
        total += item.quantity * peso

    senha= os.getenv('senha_correios')
    codigo_empresa= os.getenv('usuario_correios')
    cep_origem = 12233-400
    cep = request.POST.get('cep')
    peso = total
    comprimento = 20  # cm
    largura = 20  # cm
    altura = 20  # cm
    valor_declarado = 0
    servico = '40010'  # SEDEX e SEDEX a Cobrar


    try:

        # envia a requisição SOAP e trata a resposta
        response = requests.post(f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?nCdEmpresa={codigo_empresa}&sDsSenha={senha}&sCepOrigem=12233400&sCepDestino={cep}&nVlPeso={peso}&nCdFormato=1&nVlComprimento=20&nVlAltura=20&nVlLargura=20&nVlDiametro=0&sCdMaoPropria=n&nVlValorDeclarado=100&sCdAvisoRecebimento=0&nCdServico=03220,03298&nVlDiametro=0&StrRetorno=xml")
        print(f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?nCdEmpresa={codigo_empresa}&sDsSenha={senha}&sCepOrigem=12233400&sCepDestino=12245500&nVlPeso={peso}&nCdFormato=1&nVlComprimento=20&nVlAltura=20&nVlLargura=20&nVlDiametro=0&sCdMaoPropria=n&nVlValorDeclarado=100&sCdAvisoRecebimento=0&nCdServico=40010,41106&nVlDiametro=0&StrRetorno=xml")
        if response.status_code == 200:

            # parsing do XML retornado
            tree = ET.ElementTree(ET.fromstring(response.content))

            root = tree.getroot()

            servicos = root.findall('.//cServico')
            results = []



            for servico in servicos:
                code = servico.find('Codigo').text
                if code == '0':
                    continue  # erro no serviço
                preco = float(servico.find('Valor').text.replace(',', '.'))
                days = int(servico.find('PrazoEntrega').text)

                prazo_entrega = f"{days} {'dia útil' if days == 1 else 'dias úteis'}"

                results.append({
                    'codigo': code,
                    'valor': preco,
                    'prazodeentrega': prazo_entrega
                })
                print(results, 'results')
            print('Cotação de frete realizada com sucesso.')
            return JsonResponse({'results': results})

        else:
            print(f'Resposta da requisição inválida: {response.status_code}')
            return JsonResponse({'error': 'Houve um problema ao processar sua requisição.'})

    except Exception as e:
        print(f'Erro na requisição: {e}')
        return JsonResponse({'error': 'Houve um problema ao processar sua requisição.'})


@require_POST
@login_required
def criar_pedido(request):
    # Obter informações do formulário
    user = request.user
    subtotal = float(request.POST['subtotal'])
    frete = float(request.POST['frete'])
    total = float(request.POST['total'])
    frete_selecionado = request.POST['frete_selecionado']
    metodo_pagamento = request.POST['metodo_pagamento']
    print(metodo_pagamento, 'AQUIIIIII')
    # endereco_de_entrega_id = request.POST['endereco_de_entrega']
    # endereco_de_entrega = EnderecoEntrega.objects.get(id=endereco_de_entrega_id)
    endereco_entrega = EnderecoEntrega.objects.filter(cliente=user.cliente, primario=True).first()
    # Obter o carrinho atual do usuário
    cart = Cart.objects.get(user=request.user)
    print('SUBTOTAL',subtotal)




    # Criar uma nova instância de Pedido
    pedido = Pedido.objects.create(
        user=request.user,
        endereco_entrega=endereco_entrega,
        status='Aguardando_pagamento',
        frete=frete_selecionado,
        subtotal=subtotal,
        valor_frete=frete,
        total=total,
        metodo_de_pagamento=metodo_pagamento
    )




    for item in cart.cartitem_set.all():
        print(item)
        pedido_item = PedidoItem.objects.create(
            product=item.product,
            variation=item.variation,
            quantity=item.quantity
        )
        pedido_item.save()
        pedido.itens.add(pedido_item)
    pedido.save()


    # Adicionar os itens do carrinho ao pedido
    # print(cart, 'CARINHOO')
    # for item in cart.cartitem_set.all():
    #     print(item)
    #     pedido.itens.add(item)
    # pedido.save()

    # Limpar o carrinho
    cart.cartitem_set.all().delete()
    print(pedido.id, 'PEDIDO ID')
    # Redirecionar para a página de detalhes do pedido
    return JsonResponse({'pedido_id': pedido.id})

from django.shortcuts import render

from .models import Pedido



from django.shortcuts import render, get_object_or_404
from .models import Pedido

def pagina_pagamento(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    itens = PedidoItem.objects.filter(pedido=pedido)
    print(itens)
    for item in itens:
        print(item.quantity)
        print(item.variation)
        print(item.product)
        print(pedido.metodo_de_pagamento)


    context = {
        'itens': itens,
        'pedido_id': pedido.id,
        'subtotal': pedido.subtotal,
        'tipo_frete': pedido.frete,
        'valor_frete': pedido.valor_frete,
        'total': pedido.total,
        'frete_selecionado': request.GET.get('frete_selecionado'),
        'metodo_de_pagamento': pedido.metodo_de_pagamento,
    }
    return render(request, 'pagina_pagamento.html', context)




def confirmacao_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    return render(request, 'pedidos/confirmacao_pedido.html', {'pedido': pedido})


def paga_pix(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        comprovante = request.FILES.get('comprovante')
        pedido = Pedido.objects.get(id=pedido_id)

        # Salvar o arquivo de imagem em um local apropriado
        path = default_storage.save(f'comprovantes/{pedido_id}-{comprovante.name}', ContentFile(comprovante.read()))

        # Atualizar o pedido com o caminho para o comprovante de pagamento
        pedido.comprovante = path
        pedido.save()

        # Redirecionar o cliente de volta para a página de pagamento com uma mensagem de sucesso
        return redirect('payment_success', pedido_id=pedido_id)

    # Se o método HTTP não for POST, exibir a página de pagamento com o formulário de envio do comprovante
    pedido_id = request.GET.get('pedido_id')
    pedido = Pedido.objects.get(id=pedido_id)
    metodo_de_pagamento = pedido.metodo_de_pagamento

    return render(request, 'pagamento_pix.html', {
        'pedido_id': pedido_id,
        'metodo_de_pagamento': metodo_de_pagamento,
    })

def payment_success(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    return render(request, 'pagamento_sucesso.html', {
        'pedido': pedido,
    })