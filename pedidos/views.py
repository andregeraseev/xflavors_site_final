import os

from enviadores.email import enviar_email_pedido_criado
import mercadopago
from django.contrib import messages

from cart.views import verifica_qunatidade_carrinho_varivel

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from tiny_erp.envia_pedido import enviar_pedido_para_tiny
from .models import PedidoItem, EnderecoPedido
from cart.models import CartItem, Cart
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect
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



def verifica_carrinho(request):
    print('VERIFICANDO CARRINHO')
    cart = Cart.objects.get(user=request.user)
    if request.method == 'POST':
        item_id = int(request.POST.get('item'))
        print('item_id', item_id)
        try:
            print('tentativa')
            item = CartItem.objects.get(id=item_id, cart=cart)
            variation =item.variation
            quantity= item.quantity
            print(quantity,'quantidade')
            quantidade_materia_prima = item.variation.materia_prima.stock
            print(quantidade_materia_prima,'quantidade_materiaprima')
            materia_prima_id = item.variation.materia_prima.id
            product = item.product
            print(item.variation, 'ITEMMSSSSSSSS')
            fechamento = 2
            try:
                verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                     materia_prima_id, product,fechamento)
                return JsonResponse({'success': True})
            except ValueError as e:
                print(e)
                return JsonResponse({'success': False, 'error': str(e)})

        except CartItem.DoesNotExist:
            print('erro')
            return JsonResponse({'success': False})



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
    print("atualizando endereco")
    if request.method == 'POST':

        endereco_id = request.POST.get('endereco_id')
        cliente = request.user.cliente
        # Define o endereço selecionado como primário
        endereco = EnderecoEntrega.objects.get(id=endereco_id)
        print(endereco)
        endereco.primario = True
        endereco.save()
        # Definir os outros endereços como não primários
        outros_enderecos = EnderecoEntrega.objects.filter(cliente=cliente).exclude(id=endereco_id)
        print("outros enderecos", outros_enderecos)
        for e in outros_enderecos:
            e.primario = False
            e.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Método inválido.'})


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
        # print(f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?nCdEmpresa={codigo_empresa}&sDsSenha={senha}&sCepOrigem=12233400&sCepDestino=12245500&nVlPeso={peso}&nCdFormato=1&nVlComprimento=20&nVlAltura=20&nVlLargura=20&nVlDiametro=0&sCdMaoPropria=n&nVlValorDeclarado=100&sCdAvisoRecebimento=0&nCdServico=40010,41106&nVlDiametro=0&StrRetorno=xml")
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
            #     print(results, 'results')
            # print('Cotação de frete realizada com sucesso.')
            return JsonResponse({'results': results})

        else:
            # print(f'Resposta da requisição inválida: {response.status_code}')
            return JsonResponse({'error': 'Houve um problema ao processar sua requisição.'})

    except Exception as e:
        # print(f'Erro na requisição: {e}')
        return JsonResponse({'error': 'Houve um problema ao processar sua requisição.'})



def verifica_carrinho_2(item_id, user):
    # print('VERIFICANDO CARRINHO')
    cart = Cart.objects.get(user=user)

    item_id = int(item_id)
    # print('item_id', item_id)
    try:
        # print('tentativa')
        item = CartItem.objects.get(id=item_id, cart=cart)
        if item.variation:
            variation =item.variation
            quantidade_materia_prima = item.variation.materia_prima.stock
            # print(quantidade_materia_prima, 'quantidade_materiaprima')
            materia_prima_id = item.variation.materia_prima.id

        else:
            variation = None
            quantidade_materia_prima = item.product.stock
            materia_prima_id = item.product.id


        quantity= item.quantity
        # print(quantity,'quantidade')


        product = item.product
        # if item.variation:
        #     print(item.variation, 'ITEMMSSSSSSSS')
        # else:
            # print(item.product, 'ITEMMSSSSSSSS')
        fechamento = 2
        try:
            verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                 materia_prima_id, product,fechamento, update=True)

        except ValueError as e:
            raise ValueError(str(e))


    except CartItem.DoesNotExist:
        print('erro')
        raise ValueError




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
    observacao = request.POST['observacao']
    print(observacao)


    print(metodo_pagamento, 'CRIAR PEDIDO')
    # endereco_de_entrega_id = request.POST['endereco_de_entrega']
    # endereco_de_entrega = EnderecoEntrega.objects.get(id=endereco_de_entrega_id)
    endereco_entrega = EnderecoEntrega.objects.filter(cliente=user.cliente, primario=True).first()
    # Obter o carrinho atual do usuário
    cart = Cart.objects.get(user=request.user)
    # print('SUBTOTAL',subtotal)

    items = cart.cartitem_set.all()
    if items:
        print("TEM ITEMS")
        errors = []
        for item in items:
            try:
                verifica_carrinho_2(item.id, user)
            except ValueError as e:
                print(e)
                errors.append({'item_id': item.id, 'message': str(e)})

        if errors:
            data = {'success': False, 'errors': errors}
            return JsonResponse(data)


        endereco_pedido= EnderecoPedido.objects.create(
            user=user,
            nome = user.username,
            rua = endereco_entrega.rua,
            numero = endereco_entrega.numero,
            complemento = endereco_entrega.complemento,
            bairro = endereco_entrega.bairro,
            cidade = endereco_entrega.cidade,
            estado = endereco_entrega.estado,
            cep = endereco_entrega.cep
        )
        endereco_pedido.save()


        # Criar uma nova instância de Pedido
        print('CRIANDO PEDIDO')
        pedido = Pedido.objects.create(
            user=request.user,
            endereco_entrega=endereco_pedido,
            status='Aguardando pagamento',
            frete=frete_selecionado,
            subtotal=subtotal,
            valor_frete=frete,
            total=total,
            metodo_de_pagamento=metodo_pagamento,
            observacoes = observacao
        )

        print(pedido.metodo_de_pagamento, "METODO DE PAGAMENTO")



        print(items)
        print('itenerando items')
        for item in items:

            print('COLOCANDO ITEM NO CARRINHO')
            print(item)
            if item.variation:
                preco = item.variation.price
            else:
                preco = item.product.price
            try:
                pedido_item = PedidoItem.objects.create(
                    product=item.product,
                    variation=item.variation,
                    quantity=item.quantity,
                    price= preco
                )
                pedido_item.save()
                pedido.itens.add(pedido_item)


            except:
                e= 'erro ao adicionar item ao carrinho', item
                print(e)
                data = {'success': False, 'error': str(e)}
                return JsonResponse(data)

            try:
                atualizar_estoque(item)
                print(item.quantity)
                pedido_item.atualizar_vendas()

            except ValueError as e:
                print(e)
                errors.append({'item_id': item.id, 'message': str(e)})
            pedido.save()

        # Limpar o carrinho
        print('deletando carrinho')
        cart.cartitem_set.all().delete()
        print(pedido.id, 'PEDIDO ID')

        try:
            mercadolivre_url = cria_preferencia(request, pedido)
        except:
            mercadolivre_url = "sem url"
            raise ValueError('Problema para criar link do mercado Pago')

        pedido.salvar_link_mercado_pago(mercadolivre_url)

        # envia email
        try:
            destinatario= user.email
            nome= user.username
            pedido= pedido
            enviar_email_pedido_criado(destinatario, nome, pedido)
        except:
            raise ValueError('Problema para enviar o email')



        data = {'success': True, 'pedido_id': pedido.id}
        return JsonResponse(data)

    else:
        e='Nao foram encontrados items no carrinho'
        return JsonResponse({'success': False, 'error': str(e)})

def atualizar_estoque(item):
    produto = item.product
    variacao = item.variation
    quantidade = item.quantity
    # print('TIRANDOOOOOO')
    if variacao:
        estoque = variacao.materia_prima.stock
        if estoque < quantidade:
            raise ValueError('Estoque insuficiente para %s.' % variacao.name)
        item.variation.materia_prima.stock = estoque - quantidade * item.variation.gasto
        item.variation.materia_prima.save()
    else:
        estoque = produto.stock
        if estoque < quantidade:
            raise ValueError('Estoque insuficiente para %s.' % produto.name)
        produto.stock = estoque - quantidade
        produto.save()





from django.shortcuts import render, get_object_or_404
from .models import Pedido

from mercado_pago.mercado_livre import cria_preferencia



def pagina_pagamento(request, pedido_id):


    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens = PedidoItem.objects.filter(pedido=pedido)

    if pedido.user != request.user:
        return redirect('home')


    print(itens)
    for item in itens:
        print(item.quantity)
        print(item.variation)
        print(item.product)
        print(pedido.metodo_de_pagamento)




    context = {
        'mercadolivre_url': pedido.link_mercado_pago,
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

# mercado pago

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def notifications(request):
    mp = mercadopago("MERCADO_PAGO_CLIENT_ID")

    if request.method == 'POST':
        topic = request.POST.get('topic', '')
        data_id = request.POST.get('id', '')
        if topic == 'payment':
            payment_info = mp.get(f'/v1/payments/{data_id}')

            # Processar informações do pagamento e atualizar seu sistema
            # ...

        return HttpResponse(status=200)

    return HttpResponse(status=400)


@csrf_exempt
def success(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    print(payment_id, status, external_reference)


    pedido = Pedido.objects.get(id=external_reference)
    if pedido.status != "Pago":
        pedido.mercado_pago_id = payment_id
        pedido.status = "Pago"
        pedido.save()
        enviar_pedido_para_tiny(pedido)

    return render(request, 'mercado_pago/success.html', {'payment_id': payment_id, 'status': status,
                                                         'external_reference': external_reference})



@csrf_exempt
def failure(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    print(payment_id, status, external_reference)
    pedido = Pedido.objects.get(id=external_reference)
    if pedido.status != "Cancelado":
        pedido.mercado_pago_id = payment_id
        pedido.status = "Cancelado"
        pedido.save()


    return render(request, 'mercado_pago/failure.html', {'payment_id': payment_id, 'status': status,
                                                         'external_reference': external_reference})




@csrf_exempt
def pending(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    print(payment_id, status, external_reference)
    pedido = Pedido.objects.get(id=external_reference)
    if pedido.status != "Pendente":
        pedido.mercado_pago_id = payment_id
        pedido.status = "Pendente"
        pedido.save()


    return render(request, 'mercado_pago/pending.html', {'payment_id': payment_id, 'status': status,
                                                         'external_reference': external_reference})
