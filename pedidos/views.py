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
from clientes.models import EnderecoEntrega, Cliente
import logging
from django.http import JsonResponse
from cart.models import Cupom
import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render, get_object_or_404
from .models import Pedido
from mercado_pago.mercado_livre import cria_preferencia
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('pedidos')


@login_required
def detalhes_pedido(request, pedido_id):
    logger = logging.getLogger('clientes')
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)

    logger.info(f"Usuário {request.user} iniciou a visualização dos detalhes do pedido ID: {pedido_id}")

    total = 0
    itens = pedido.itens.all()

    for item in itens:
        preco = preco_item(item)
        total += item.quantity * preco

    context = {'pedido': pedido, 'total':total}

    return render(request, 'detalhes_pedido.html', context)

@login_required
def visualizar_pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user)
    context = {'pedidos': pedidos}

    return render(request, 'visualizar_pedidos.html', context)

def validar_cupom(request):
    """Def para validacao de cupom"""

    logger.info(f"Usuário {request.user} iniciou a validação de um cupom")
    user = request.user
    cart = Cart.get_or_create_cart(user)
    codigo_cupom = request.POST.get('codigo_cupom')
    frete_selecionado = request.POST.get('frete_selecionado')
    estado_entrega = request.POST.get('estado_frete')
    subtotal = request.POST.get('subtotal')
    codigo_cupom = codigo_cupom.upper()
    email = user.email
    print(email)
    try:
        # Verifica se o cupom existe
        cupom = get_object_or_404(Cupom, codigo=codigo_cupom)
        logger.info(f"Cupom com código {codigo_cupom} encontrado")
    except:
        logger.warning(f"Cupom com código {codigo_cupom} não encontrado para o usuário {request.user}")
        return JsonResponse({'status': 'error', 'mensagem': 'Cupom não encontrado.'})
    try:
        # Calcula o valor a ter desconto e se o cupom pode ser utulizado
        subtotal = float(request.POST.get('subtotal'))

        cupom_pode_ser_utilizado, mensagem_cupom = cupom.pode_ser_utilizado(total=subtotal, estado_entrega=estado_entrega, tipo_frete=frete_selecionado, user=email)
        if not cupom_pode_ser_utilizado:
            logger.warning(f"Cupom com código {codigo_cupom} não pode ser utilizado pelo Usuario {request.user},"
                           f" {mensagem_cupom} ")
            return JsonResponse({'status': 'error', 'mensagem': mensagem_cupom})

        valor_desconto = round(float(cupom.desconto_percentual) / 100 * subtotal, 2)
        valor_total_com_desconto = subtotal - valor_desconto

        logger.info(
            f"Desconto calculado para o cupom {codigo_cupom}: {valor_desconto}. Total após desconto: {valor_total_com_desconto}")

    except Exception as e:
        logger.error(f"Erro ao calcular o desconto para o cupom {codigo_cupom}. Detalhes do erro: {str(e)}")
        return JsonResponse({'status': 'error', 'mensagem': 'Erro ao calcular o desconto.'})

    try:
        # Tenta aplicar o cupom no carrinho do usuario
        cart.aplicar_cupom(codigo_cupom)

    except Exception as e:
        logger.error(f"Erro ao aplicar o cupom {codigo_cupom} ao carrinho. Detalhes do erro: {str(e)}")
        return JsonResponse({'status': 'error', 'mensagem': 'Erro ao aplicar o cupom ao carrinho.'})
    logger.info(f"Cupom com código {codigo_cupom} aplicado com sucesso para o usuario {request.user}")

    return JsonResponse({'status': 'success', 'valor_total_com_desconto': valor_total_com_desconto, 'valor_desconto': valor_desconto})


def validar_cupom_finalizando_pedido(user,cart,frete_selecionado,estado_frete,subtotal):
    """Def para validacao de cupom ao clicar em finalizar pedido"""

    logger.info(f"Usuário {user} iniciou a validação de um cupom ao clicar em finalizar pedido")

    codigo_cupom = cart.cupom

    try:
        # Verifica se o cupom existe
        cupom = get_object_or_404(Cupom, codigo=codigo_cupom)
        logger.info(f"Cupom com código {codigo_cupom} encontrado")
    except:
        mensagem_cupom = 'Cupom não encontrado.'
        logger.warning(f"Cupom com código {codigo_cupom} não encontrado para o usuário {user}")
        raise ValueError(mensagem_cupom)
    try:
        # Calcula o valor a ter desconto e se o cupom pode ser utulizado


        cupom_pode_ser_utilizado, mensagem_cupom = cupom.pode_ser_utilizado(total=subtotal, estado_entrega=estado_frete, tipo_frete=frete_selecionado)
        if not cupom_pode_ser_utilizado:
            logger.warning(f"Cupom com código {codigo_cupom} não pode ser utilizado pelo Usuario {user},"
                           f" {mensagem_cupom} ")
            raise ValueError(mensagem_cupom)



        valor_desconto = round(float(cupom.desconto_percentual) / 100 * subtotal, 2)
        valor_total_com_desconto = subtotal - valor_desconto

        logger.info(
            f"Desconto calculado para o cupom {codigo_cupom}: {valor_desconto}. Total após desconto: {valor_total_com_desconto}")

    except Exception as e:

        logger.error(f"Erro ao calcular o desconto para o cupom {codigo_cupom}. Detalhes do erro: {str(e)}")
        raise ValueError(mensagem_cupom)



    return JsonResponse({'status': 'success', 'resposta': 'true'})


def remover_cupom(request):
    """Def para remover cupom do carrinho do usuario"""

    logger.info(f"Usuário {request.user} iniciou a tentativa de remoção de um cupom")

    cart_id = request.POST['cart_id']
    cupom_id = request.POST['cupom_id']

    try:
        # Verifica se o carrinho pertence ao usuário atual
        cart = get_object_or_404(Cart, id=cart_id, user=request.user)
        logger.info(f"Carrinho ID: {cart_id} encontrado para o usuário {request.user}")
    except:
        logger.warning(f"Carrinho ID: {cart_id} não encontrado para o usuário {request.user}")
        return JsonResponse({'status': 'error', 'mensagem': 'Carrinho não encontrado.'})

        # Verifica se o carrinho tem um cupom
    if not cart.cupom:
        logger.warning(f"Carrinho ID: {cart_id} do usuário {request.user} não tem um cupom associado")
        return JsonResponse({'status': 'error', 'mensagem': 'O carrinho não tem um cupom.'})

        # Verifica se o cupom pertence ao carrinho
    if cart.cupom.id != int(cupom_id):
        logger.warning(f"Cupom ID: {cupom_id} não pertence ao carrinho ID: {cart_id} do usuário {request.user}")
        return JsonResponse({'status': 'error', 'mensagem': 'O cupom não pertence ao carrinho.'})

    try:
        # Remove o cupom do carrinho
        cart.cupom = None
        cart.save()
        logger.info(f"Cupom ID: {cupom_id} removido com sucesso do carrinho ID: {cart_id} do usuário {request.user}")
    except Exception as e:
        logger.error(f"Erro ao remover o cupom ID: {cupom_id} do carrinho ID: {cart_id}. Detalhes do erro: {str(e)}")
        return JsonResponse({'status': 'error', 'mensagem': 'Erro ao remover o cupom.'})

    return JsonResponse({'status': 'success'})


@login_required
def checkout(request):
    """
    Processa a página de checkout, calcula o total do carrinho, aplica descontos de cupom e fornece detalhes de endereço.
    Parameters:
    - request: objeto HttpRequest
    Returns:
    - HttpResponse com os detalhes do checkout ou uma mensagem de erro.
    """

    # Registrar o início da tentativa de acesso ao checkout
    logger.info(f"Usuário {request.user} iniciou a tentativa de acessar o checkout")

    user = request.user

    try:
        # Obtenha o carrinho, os itens do carrinho e o cliente correspondente ao usuário atual
        cart = Cart.get_or_create_cart(user)
        itens = cart.cartitem_set.all()
        cliente = Cliente.objects.get(user=user)
    except:
        # Registrar qualquer erro ao tentar obter o carrinho, itens ou cliente
        logger.error(f"Erro ao obter carrinho, itens ou cliente para o usuário {request.user}")
        return render(request, 'error.html',
                      {'mensagem': 'Erro ao processar o checkout. Por favor, tente novamente mais tarde.'})

    # Calcule o total com base nos itens do carrinho
    total = sum(preco_item(item) * item.quantity for item in itens)

    subtotal = total
    desconto = 0

    # Se houver um cupom associado ao carrinho, calcule o desconto
    if cart.cupom:


        desconto, valor_com_desconto = cart.cupom.aplicar_desconto(subtotal)
        desconto = round(float(desconto),2)

        valor_com_desconto = float(valor_com_desconto)
        total = round(valor_com_desconto, 2)
        logger.info(f"Desconto calculado para o carrinho ID: {cart.id}: {desconto}. Total após desconto: {total}")

    enderecos = []
    endereco_primario = None

    # Se o usuário tiver um objeto Cliente associado, tente obter seus endereços
    if hasattr(user, 'cliente'):
        try:
            enderecos = user.cliente.enderecoentrega_set.all()
            endereco_primario = enderecos.filter(primario=True).first()
        except:
            # Registrar qualquer erro ao tentar obter endereços
            logger.warning(f"Erro ao obter endereços do cliente para o usuário {request.user}")

    # Registrar o sucesso ao carregar a página de checkout
    logger.info(f"Checkout carregado com sucesso para o usuário {request.user}")

    return render(request, 'pedidos/checkout.html',
                  {'cliente': cliente, 'subtotal': subtotal, 'desconto': desconto, 'cart': cart, 'total': total,
                   'endereco': enderecos, 'endereco_primario': endereco_primario, 'itens': itens})

@login_required
def editar_endereco(request):
    """
      Permite ao usuário editar um endereço de entrega existente.
    Parameters:
    - request: objeto HttpRequest contendo os detalhes do endereço a ser editado.
    Returns:
    - HttpResponse com a página de edição de endereço ou uma mensagem de sucesso/erro.
    """
    # Esta função é chamada através de uma solicitação AJAX feita pelo script em templates/pedidos/checkout.html
    # O parâmetro endereco_id é passado pelo script quando o elemento com ID 'editar-endereco' é clicado.

    logger.info('Usuário %s tentando editar endereço', request.user)
    # Caso a requisição seja POST, é uma tentativa de atualizar um endereço existente
    if request.method == 'POST':
        # Obtendo detalhes do endereço do formulário
        endereco_id = request.POST.get('endereco_id')
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')

        try:
            # Tentar atualizar o endereço existente
            endereco = EnderecoEntrega.objects.get(id=endereco_id)
            endereco.rua = rua
            endereco.numero = numero
            endereco.complemento = complemento
            endereco.bairro = bairro
            endereco.cidade = cidade
            endereco.estado = estado
            endereco.cep = cep
            endereco.save()

            # Log da atualização bem-sucedida do endereço
            logger.info('Endereço ID %s atualizado com sucesso para o usuário %s', endereco_id, request.user)
            messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('checkout')

        except EnderecoEntrega.DoesNotExist:
            # Log do erro ao tentar encontrar o endereço para atualização
            logger.error('Erro ao tentar atualizar o endereço ID %s para o usuário %s. Endereço não encontrado.',
                         endereco_id, request.user)
            messages.error(request, 'Endereço não encontrado.')
            return redirect('checkout')
    # Caso a requisição seja GET, é uma tentativa de visualizar a página de edição de endereço
    endereco_id = request.GET.get('endereco_id')
    endereco = get_object_or_404(EnderecoEntrega, pk=endereco_id, cliente=request.user.cliente)
    # Log da tentativa de visualização da página de edição de endereço
    logger.info('Usuário %s acessando a página de edição do endereço ID %s', request.user, endereco_id)
    return render(request, 'editar_endereco.html', {'endereco': endereco})


@login_required
def atualizar_endereco_entrega(request):
    """
    Atualiza o endereço de entrega primário do cliente.

    A partir de uma solicitação AJAX, esta função define um endereço específico
    como primário para o cliente e torna todos os outros endereços não primários.

    Parameters:
    - request: objeto HttpRequest contendo o ID do endereço a ser definido como primário.

    Returns:
    - JsonResponse indicando o sucesso ou falha da operação.
    """

    # Esta função é chamada através de uma solicitação AJAX feita pelo script em templates/pedidos/checkout.html
    # O parâmetro endereco_id é passado pelo script quando o dropdown com ID 'endereco_entrega' muda de valor.

    logger.info('Usuário %s tentando atualizar endereço de entrega', request.user)

    if request.method == 'POST':
        try:
            endereco_id = request.POST.get('endereco_id')
            cliente = request.user.cliente

            # Define o endereço selecionado como primário
            endereco = EnderecoEntrega.objects.get(id=endereco_id)
            endereco.primario = True
            endereco.save()

            # Definir os outros endereços como não primários
            outros_enderecos = EnderecoEntrega.objects.filter(cliente=cliente).exclude(id=endereco_id)
            for e in outros_enderecos:
                e.primario = False
                e.save()

            logger.info('Endereço ID %s definido como primário para o usuário %s', endereco_id, request.user)
            return JsonResponse({'success': True})

        except EnderecoEntrega.DoesNotExist:
            logger.error('Endereço ID %s não encontrado para o usuário %s', endereco_id, request.user)
            return JsonResponse({'success': False, 'message': 'Endereço não encontrado.'})

        except Exception as e:
            logger.error('Erro ao atualizar endereço de entrega para o usuário %s. Erro: %s', request.user, str(e))
            return JsonResponse({'success': False, 'message': 'Erro interno no servidor.'})

    else:
        logger.error('Tentativa inválida de atualizar endereço de entrega para o usuário %s. Método não permitido.',
                     request.user)
        return JsonResponse({'success': False, 'message': 'Método inválido.'})







@login_required
def cotacao_frete_correios(request):
    """
    Obtém cotações de frete dos Correios para o endereço do cliente.

    Com base nos itens no carrinho do cliente, esta função faz uma requisição
    aos Correios para obter cotações de frete para o endereço do cliente.

    Parameters:
    - request: objeto HttpRequest contendo o CEP do endereço de entrega.

    Returns:
    - JsonResponse com os resultados da cotação ou uma mensagem de erro.
    """
    # Esta função é chamada pelo script jQuery localizado em templates/pedidos/checkout.html.
    # Espera receber CEP como parametro POST e retorna um JSON contendo os resultados da cotação ou uma mensagem de erro
    logger.info('Usuário %s iniciando cotação de frete.', request.user)

    user = request.user
    cart = Cart.get_or_create_cart(user)
    itens = cart.cartitem_set.all()


    # Calcula o peso dos itens do carrinho caso o peso for menor que 300 gramas o total peso fica igual a 300 gramas
    total_peso = 0
    try:
        for item in itens:
            peso = item.variation.peso if item.variation else item.product.peso
            total_peso += item.quantity * peso
        if total_peso < 0.3:
            total_peso = 0.3
    except:
        logger.warning(f"Problemas para calcular peso do carrinho {cart}, do usuario {user.username}")
        total_peso = 0.3

    senha = os.getenv('senha_correios')
    codigo_empresa = os.getenv('usuario_correios')
    cep_origem = '12233400'
    cep_destino = request.POST.get('cep')
    if cep_destino == None:
        logger.error('Erro ao coletar cep do destinatario ')
        return JsonResponse({'error': 'Tivemos um erro com cep, verifique por gentileza'})

    try:
        # Realiza a requisição para cotação no webservice dos Correios
        response = requests.post(
            f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?"
            f"nCdEmpresa={codigo_empresa}&sDsSenha={senha}&sCepOrigem={cep_origem}&sCepDestino={cep_destino}"
            f"&nVlPeso={total_peso}&nCdFormato=1&nVlComprimento=20&nVlAltura=20&nVlLargura=20&nVlDiametro=0"
            f"&sCdMaoPropria=n&nVlValorDeclarado=100&sCdAvisoRecebimento=0&nCdServico=03220,03298&StrRetorno=xml")
        if response.status_code == 200:
            tree = ET.ElementTree(ET.fromstring(response.content))
            servicos = tree.getroot().findall('.//cServico')
            results = []
            for servico in servicos:
                code = servico.find('Codigo').text
                if code == '0':
                    continue
                preco = float(servico.find('Valor').text.replace(',', '.'))
                days = int(servico.find('PrazoEntrega').text)
                prazo_entrega = f"{days} {'dia útil' if days == 1 else 'dias úteis'}"
                results.append({
                    'codigo': code,
                    'valor': preco,
                    'prazodeentrega': prazo_entrega
                })
            logger.info(f'Usuário {request.user} finalizou cotação de frete. {results}')
            return JsonResponse({'results': results})

        else:
            logger.error('Erro na resposta dos Correios para o usuário %s. Código de status: %s', request.user,
                         response.status_code)
            return JsonResponse({'error': 'Tivemos um erro ao cotar o frete. Por favor, recarregue o frete.'})

    except Exception as e:
        logger.error('Erro ao cotar frete dos Correios para o usuário %s. Erro: %s', request.user, str(e))
        return JsonResponse({'error': 'Tivemos um erro ao cotar o frete. Por favor, recarregue o frete.'})


def verifica_carrinho(request):
    """
    Verifica a disponibilidade de itens no carrinho em relação ao estoque de matéria-prima.
    Parameters:
    - request: objeto HttpRequest contendo os detalhes do item do carrinho a ser verificado.
    Returns:
    - JsonResponse indicando o sucesso ou falha da verificação.
    """
    logger.info('Iniciando a verificação do carrinho para o usuário %s', request.user)
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        logger.error('Erro ao obter o carrinho do usuário %s', request.user)
        return JsonResponse({'success': False, 'error': 'Carrinho não encontrado.'})

    if request.method == 'POST':
        item_id = int(request.POST.get('item'))
        logger.debug('Verificando item com ID: %s', item_id)
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            variation = item.variation
            quantity = item.quantity
            quantidade_materia_prima = item.variation.materia_prima.stock
            materia_prima_id = item.variation.materia_prima.id
            product = item.product
            fechamento = 2
            try:
                verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                                     materia_prima_id, product, fechamento)
                return JsonResponse({'success': True})
            except ValueError as e:
                logger.warning('Erro ao verificar a quantidade do carrinho: %s', str(e))
                return JsonResponse({'success': False, 'error': str(e)})
        except CartItem.DoesNotExist:
            logger.error('Item com ID %s não encontrado no carrinho do usuário %s', item_id, request.user)
            return JsonResponse({'success': False})
    else:
        logger.warning('Método não permitido para a verificação do carrinho')
        return JsonResponse({'success': False, 'error': 'Método não permitido.'})


def verifica_carrinho_2(item_id, user):
    """
    Esta função verifica a disponibilidade do item no carrinho com base no estoque de matéria-prima ou produto.
    Ela é chamada pela função 'criar_pedido' para garantir que todos os itens no carrinho ainda estejam disponíveis
    antes de finalizar o pedido.

    :param item_id: ID do item no carrinho.
    :param user: Usuário atual.

    :raises ValueError: Se o item não estiver disponível ou outros erros ocorrerem.
    """
    logger.info(f"Verificando disponibilidade do item com ID {item_id} para o usuário {user.username}.")

    try:
        cart = Cart.objects.get(user=user)
        item = CartItem.objects.get(id=int(item_id), cart=cart)

        if item.variation:
            variation = item.variation
            quantidade_materia_prima = item.variation.materia_prima.stock
            materia_prima_id = item.variation.materia_prima.id
        else:
            variation = None
            quantidade_materia_prima = item.product.stock
            materia_prima_id = item.product.id

        quantity = item.quantity
        product = item.product

        # Verificar a disponibilidade do item no carrinho
        verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                                             materia_prima_id, product, fechamento=2, update=True)

    except CartItem.DoesNotExist:
        logger.error(f"Item com ID {item_id} não encontrado no carrinho do usuário {user.username}.")
        raise ValueError("Item não encontrado no carrinho.")
    except ValueError as e:
        logger.error(
            f"Erro ao verificar disponibilidade do item com ID {item_id} para o usuário {user.username}. Erro: {str(e)}")
        raise


@require_POST
@login_required
def criar_pedido(request):
    """
    Esta função cria um novo pedido com base nos itens no carrinho do usuário.
    Também verifica a disponibilidade dos itens, atualiza o estoque e envia um e-mail de confirmação.
    """
    user = request.user

    # Logs para rastreamento
    logger.info(f"Criando pedido para o usuário {user.username}.")

    # Obter informações do formulário
    subtotal = float(request.POST['subtotal'])
    frete = float(request.POST['frete'])
    total = float(request.POST['total'])
    desconto = float(request.POST.get('desconto', 0))
    frete_selecionado = request.POST['frete_selecionado']
    metodo_pagamento = request.POST['metodo_pagamento']
    observacao = request.POST['observacao']
    estado_frete = request.POST['estado_frete']

    try:
        cart = Cart.objects.get(user=request.user)
    except:
        logger.error(f"Carrinho do {user} nao encontrado.")
        return JsonResponse({'success': False, 'error': 'Nao foi encontrado um carrinho,'
                                                        ' por gentileza volte para home'})
    cupom = cart.cupom

    if cupom:
        try:
            validar_cupom_finalizando_pedido(user,cart,frete_selecionado,estado_frete,subtotal)
            logger.info(f"cupom {cupom}, valido para o finalizar o pedido do usuario {user}")
        except ValueError as e:

            logger.error(f"Erro validar cupom {user.username}. Erro: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Erro validar cupom:\n{str(e)}'})


    items = cart.cartitem_set.all()

    if not items:
        logger.error("Nenhum item encontrado no carrinho.")
        return JsonResponse({'success': False, 'error': 'Nao foram encontrados items no carrinho.'})

    # Verificar disponibilidade dos itens
    errors = []
    for item in items:
        try:
            verifica_carrinho_2(item.id, user)
        except ValueError as e:
            errors.append({'item_id': item.id, 'message': str(e)})

    if errors:
        logger.error(f"Erros ao fechar pedido do usuario {user.username}: 'ERROS': {errors}")
        return JsonResponse({'success': False, 'errors': errors, 'error': 'Quantidade de materia prima insuficiente,'
                                                             ' por gentiliza ajuste as quantidades em seu carrinho'})

    endereco_entrega = EnderecoEntrega.objects.filter(cliente=user.cliente, primario=True).first()

    try:
        # Criar EnderecoPedido
        endereco_pedido = EnderecoPedido.objects.create(
            user=user,
            nome=user.username,
            rua=endereco_entrega.rua,
            numero=endereco_entrega.numero,
            complemento=endereco_entrega.complemento,
            bairro=endereco_entrega.bairro,
            cidade=endereco_entrega.cidade,
            estado=endereco_entrega.estado,
            cep=endereco_entrega.cep
        )
        logger.info(f"Endereco de entrega criado  {endereco_pedido} para {user.username}.")

    except Exception as e:
        logger.error(f"Erro ao criar endereço de entrega para o usuário {user.username}. Erro: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Erro ao criar endereço de entrega.'})

    try:
        # Criar Pedido
        pedido = Pedido.objects.create(
            user=request.user,
            endereco_entrega=endereco_pedido,
            status='Aguardando pagamento',
            frete=frete_selecionado,
            subtotal=subtotal,
            valor_frete=frete,
            total=total,
            metodo_de_pagamento=metodo_pagamento,
            observacoes=observacao,
            desconto=desconto,
            cupom=cupom
        )
        logger.info(f"Pedido Criado {pedido} para {user.username}.")

        # Adicionar itens ao Pedido
        for item in items:
            preco = preco_item(item)
            pedido_item = PedidoItem.objects.create(
                product=item.product,
                variation=item.variation,
                quantity=item.quantity,
                price=preco
            )
            pedido.itens.add(pedido_item)
            atualizar_estoque(item)
            pedido_item.atualizar_vendas()

        logger.info(f"Itens adicionados ao {pedido} para {user.username}.")

    except Exception as e:
        logger.error(f"Erro ao criar pedido para o usuário {user.username}. Erro: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Erro ao criar o pedido.'})

    try:
        # Limpar o carrinho
        cart.cartitem_set.all().delete()
        cart.delete()
        logger.info(f"Limpando carrinho do Usuario {user.username}.")
    except Exception as e:
        logger.error(f"Erro ao limpar carrinho antigo. Erro: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Erro ao limpar carrinho antigo.'})
        # Processar pagamento (MercadoPago)
    try:
        mercadolivre_url = cria_preferencia(request, pedido)
        logger.info(f"Criando preferencia mercado livre para {pedido}, do usuario {user.username}.")
        pedido.salvar_link_mercado_pago(mercadolivre_url)
        logger.info(f"Salvando link do mercado pago para o pedido {pedido}, do usuario {user.username}.")
    except Exception as e:
        logger.error(f"Erro ao processar mercado livre para o usuário {user.username}. Erro: {str(e)}")

    try:
        # Enviar e-mail de confirmação
        enviar_email_pedido_criado(user.email, user.username, pedido)
        logger.info(f"Enviando email de confirmacao do pedido para {user.email} do usuario {user.username}.")
    except Exception as e:
        logger.error(f"Erro ao enviar email para {user.email} do usuario {user.username}. Erro: {str(e)}")


    return JsonResponse({'success': True, 'pedido_id': pedido.id})


def preco_item(item):
    """
    Retorna o preço ou valor promocional de um item, seja de sua variação ou do produto em si.

    Parâmetros:
    - item: O item cujo preço ou valor promocional precisa ser obtido.

    Retorna:
    - float: O preço ou valor promocional do item.
    """
    try:
        if hasattr(item, 'variation') and item.variation:
            preco = item.variation.preco_ou_valor_promocional
            # logger.info(f"Preço obtido da variação: {preco}")
        else:
            preco = item.product.preco_ou_valor_promocional
            # logger.info(f"Preço obtido do produto: {preco}")
        return preco

    except AttributeError as e:
        logger.error(f"Erro ao obter preço do item. Detalhes: {str(e)}")
        raise ValueError("O item fornecido não possui preço ou valor promocional associado.")


def atualizar_estoque(item):
    """
    Atualiza o estoque de um produto ou sua variação com base na quantidade do item fornecido.

    Parâmetros:
    - item: O item cujo estoque precisa ser atualizado.

    Lança:
    - ValueError: Se o estoque for insuficiente.
    """
    try:
        produto = item.product
        variacao = item.variation
        quantidade = item.quantity

        if variacao:
            estoque = variacao.materia_prima.stock
            if estoque < quantidade:
                logger.error(f"Estoque insuficiente para {variacao.name}.")
                raise ValueError(f'Estoque insuficiente para {variacao.name}.')

            variacao.materia_prima.stock = estoque - quantidade * variacao.gasto
            variacao.materia_prima.save()
            logger.info(f"Estoque atualizado para {variacao.name}. Novo estoque: {variacao.materia_prima.stock}")

        else:
            estoque = produto.stock
            if estoque < quantidade:
                logger.error(f"Estoque insuficiente para {produto.name}.")
                raise ValueError(f'Estoque insuficiente para {produto.name}.')

            produto.stock = estoque - quantidade
            produto.save()
            logger.info(f"Estoque atualizado para {produto.name}. Novo estoque: {produto.stock}")

    except Exception as e:
        logger.error(f"Erro ao atualizar estoque. Detalhes: {str(e)}")
        raise



def pagina_pagamento(request, pedido_id):
    """
    Renderiza a página de pagamento com detalhes do pedido especificado.

    Parâmetros:
    - request: objeto HttpRequest.
    - pedido_id: ID do pedido a ser visualizado.

    Retorna:
    - HttpResponse: Página de pagamento renderizada com detalhes do pedido.
    """
    try:
        # Busca o pedido pelo ID fornecido
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Verifica se o pedido pertence ao usuário que fez a requisição
        if pedido.user != request.user:
            logger.warning(f"Usuário {request.user} tentou acessar o pedido {pedido_id} de outro usuário.")
            return redirect('home')

        # Busca os itens associados ao pedido
        itens = PedidoItem.objects.filter(pedido=pedido)

        # Prepara o contexto para renderizar a página
        context = {
            'mercadolivre_url': pedido.link_mercado_pago,
            'itens': itens,
            'pedido_id': pedido.id,
            'subtotal': pedido.subtotal,
            'tipo_frete': pedido.frete,
            'valor_frete': pedido.valor_frete,
            'total': pedido.total,
            'desconto': pedido.desconto,
            'frete_selecionado': request.GET.get('frete_selecionado'),
            'metodo_de_pagamento': pedido.metodo_de_pagamento,
        }

        return render(request, 'pagina_pagamento.html', context)

    except Exception as e:
        logger.error(f"Erro ao renderizar a página de pagamento para o pedido {pedido_id}. Detalhes: {str(e)}")
        # Aqui, decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')


import logging

logger = logging.getLogger(__name__)


def paga_pix(request):
    """
    Permite que um usuário envie um comprovante de pagamento via PIX para um pedido específico.

    O usuário deve fazer uma transferência usando a chave PIX fornecida na página de pagamento.
    Após a transferência, o usuário pode enviar um comprovante de pagamento (imagem) usando o formulário
    na página de pagamento.

    Parâmetros:
    - request: objeto HttpRequest contendo o comprovante de pagamento (imagem) e o ID do pedido.

    Retorna:
    - HttpResponse: Redirecionamento após o envio do comprovante.
    """
    if request.method == 'POST':
        try:
            pedido_id = request.POST.get('pedido_id')
            comprovante = request.FILES.get('comprovante')
            pedido = Pedido.objects.get(id=pedido_id)

            # Salvar o arquivo de imagem em um local apropriado
            path = default_storage.save(f'comprovantes/{pedido_id}-{comprovante.name}', ContentFile(comprovante.read()))

            # Atualizar o pedido com o caminho para o comprovante de pagamento
            pedido.comprovante = path
            pedido.status = "Pagamento em análise"
            pedido.save()

            logger.info(f"Comprovante PIX enviado para o pedido {pedido_id}.")

            # Redirecionar o cliente de volta para a página de pagamento com uma mensagem de sucesso
            return redirect('payment_success', pedido_id=pedido_id)

        except Pedido.DoesNotExist:
            logger.error(f"Pedido {pedido_id} não encontrado ao tentar enviar comprovante PIX.")
            # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
            return redirect('home')
        except Exception as e:
            logger.error(f"Erro ao enviar comprovante PIX para o pedido {pedido_id}. Detalhes: {str(e)}")
            # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
            return redirect('home')


def payment_success(request, pedido_id):
    """
    Exibe a página de sucesso após o usuário enviar um comprovante de pagamento via PIX.

    Esta função é geralmente chamada após o envio bem-sucedido de um comprovante PIX pelo usuário.

    Parâmetros:
    - request: objeto HttpRequest.
    - pedido_id: ID do pedido para o qual o comprovante foi enviado.

    Retorna:
    - HttpResponse: Renderização da página 'pagamento_sucesso.html' com detalhes do pedido.
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        return render(request, 'pagamento_sucesso.html', {
            'pedido': pedido,
        })

    except Pedido.DoesNotExist:
        logger.error(f"Pedido {pedido_id} não encontrado ao tentar exibir página de sucesso de pagamento.")
        # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')
    except Exception as e:
        logger.error(f"Erro ao exibir página de sucesso de pagamento para o pedido {pedido_id}. Detalhes: {str(e)}")
        # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')

# mercado pago


@csrf_exempt
def success(request):
    """
    Página de retorno após um pagamento bem-sucedido via Mercado Pago.

    Esta função é chamada pelo Mercado Pago após a finalização bem-sucedida de um pagamento.
    Ela recupera os detalhes do pagamento, como ID do pagamento, status e referência externa,
    e os exibe na página 'mercado_pago/success.html'.

    Parâmetros:
    - request: objeto HttpRequest com detalhes fornecidos pelo Mercado Pago no redirecionamento.

    Retorna:
    - HttpResponse: Renderização da página 'mercado_pago/success.html' com detalhes do pagamento.
    """
    try:
        payment_id = request.GET.get('payment_id')
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')

        logger.info(f"Pagamento bem-sucedido via Mercado Pago. ID do Pagamento: {payment_id}, Status: {status}, Referência Externa: {external_reference}")

        return render(request, 'mercado_pago/success.html', {
            'payment_id': payment_id,
            'status': status,
            'external_reference': external_reference
        })

    except Exception as e:
        logger.error(f"Erro ao processar redirecionamento bem-sucedido do Mercado Pago. Detalhes: {str(e)}")
        # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')



@csrf_exempt
def failure(request):
    """
    Página de retorno após uma falha ou cancelamento de pagamento via Mercado Pago.

    Esta função é chamada pelo Mercado Pago após a falha ou cancelamento de um pagamento.
    Ela recupera os detalhes do pagamento, como ID do pagamento, status e referência externa,
    e os exibe na página 'mercado_pago/failure.html'.

    Parâmetros:
    - request: objeto HttpRequest com detalhes fornecidos pelo Mercado Pago no redirecionamento.

    Retorna:
    - HttpResponse: Renderização da página 'mercado_pago/failure.html' com detalhes do pagamento.
    """
    try:
        payment_id = request.GET.get('payment_id')
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')

        logger.warning(f"Falha ou cancelamento de pagamento via Mercado Pago. ID do Pagamento: {payment_id}, Status: {status}, Referência Externa: {external_reference}")

        # Descomente o código abaixo se quiser atualizar o status do pedido após uma falha de pagamento.
        # pedido = Pedido.objects.get(id=external_reference)
        # if pedido.status != "Cancelado":
        #     pedido.mercado_pago_id = payment_id
        #     pedido.status = "Cancelado"
        #     pedido.save()

        return render(request, 'mercado_pago/failure.html', {
            'payment_id': payment_id,
            'status': status,
            'external_reference': external_reference
        })

    except Exception as e:
        logger.error(f"Erro ao processar redirecionamento de falha do Mercado Pago. Detalhes: {str(e)}")
        # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')


@csrf_exempt
def pending(request):
    """
    Página de retorno após um pagamento pendente no Mercado Pago.

    Esta função é chamada pelo Mercado Pago após um pagamento que ainda está em estado pendente.
    Ela recupera os detalhes do pagamento, como ID do pagamento, status e referência externa,
    e os exibe na página 'mercado_pago/pending.html'.

    Parâmetros:
    - request: objeto HttpRequest com detalhes fornecidos pelo Mercado Pago no redirecionamento.

    Retorna:
    - HttpResponse: Renderização da página 'mercado_pago/pending.html' com detalhes do pagamento.
    """
    try:
        payment_id = request.GET.get('payment_id')
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')

        logger.info(f"Pagamento pendente via Mercado Pago. ID do Pagamento: {payment_id}, Status: {status}, Referência Externa: {external_reference}")

        # Descomente o código abaixo se quiser atualizar o status do pedido para "Pendente" automaticamente.
        # pedido = Pedido.objects.get(id=external_reference)
        # if pedido.status != "Pendente":
        #     pedido.mercado_pago_id = payment_id
        #     pedido.status = "Pendente"
        #     pedido.save()

        return render(request, 'mercado_pago/pending.html', {
            'payment_id': payment_id,
            'status': status,
            'external_reference': external_reference
        })

    except Exception as e:
        logger.error(f"Erro ao processar redirecionamento pendente do Mercado Pago. Detalhes: {str(e)}")
        # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
        return redirect('home')


# def confirmacao_pedido(request, pedido_id):
#     """
#     Renderiza a página de confirmação de pedido com detalhes do pedido especificado.
#
#     Parâmetros:
#     - request: objeto HttpRequest.
#     - pedido_id: ID do pedido a ser confirmado.
#
#     Retorna:
#     - HttpResponse: Página de confirmação de pedido renderizada com detalhes do pedido.
#     """
#     try:
#         # Busca o pedido pelo ID fornecido
#         pedido = Pedido.objects.get(id=pedido_id)
#
#         # Prepara o contexto para renderizar a página
#         context = {'pedido': pedido}
#
#         return render(request, 'pedidos/confirmacao_pedido.html', context)
#
#     except Pedido.DoesNotExist:
#         logger.error(f"Pedido {pedido_id} não encontrado.")
#         # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
#         return redirect('home')
#     except Exception as e:
#         logger.error(f"Erro ao renderizar a página de confirmação para o pedido {pedido_id}. Detalhes: {str(e)}")
#         # Aqui, você pode decidir redirecionar para uma página de erro ou retornar uma mensagem de erro.
#         return redirect('home')
#
#
# @csrf_exempt
# def notifications(request):
#     mp = mercadopago("MERCADO_PAGO_CLIENT_ID")
#
#     if request.method == 'POST':
#         topic = request.POST.get('topic', '')
#         data_id = request.POST.get('id', '')
#         if topic == 'payment':
#             payment_info = mp.get(f'/v1/payments/{data_id}')
#
#             # Processar informações do pagamento e atualizar seu sistema
#             # ...
#
#         return HttpResponse(status=200)
#
#     return HttpResponse(status=400)

#
#
# @login_required
# def cotacao_frete_correios2(endereco):
#     cep = endereco.cep
#     peso = 0.1  # 100 gramas
#     comprimento = 20  # cm
#     largura = 20  # cm
#     altura = 20  # cm
#     valor_declarado = 0
#     servico = '40010,41106'  # SEDEX e SEDEX a Cobrar
#
#     dados = f"""
#     <servicos>
#         <cServico>
#             <nCdEmpresa></nCdEmpresa>
#             <sDsSenha></sDsSenha>
#             <nCdServico>{servico}</nCdServico>
#             <sCepOrigem>01010-001</sCepOrigem>
#             <sCepDestino>{cep}</sCepDestino>
#             <nVlPeso>{peso}</nVlPeso>
#             <nCdFormato>1</nCdFormato>
#             <nVlComprimento>{comprimento}</nVlComprimento>
#             <nVlAltura>{altura}</nVlAltura>
#             <nVlLargura>{largura}</nVlLargura>
#             <nVlValorDeclarado>{valor_declarado}</nVlValorDeclarado>
#             <sCdMaoPropria>N</sCdMaoPropria>
#             <nVlDiametro>0</nVlDiametro>
#             <sCdAvisoRecebimento>N</sCdAvisoRecebimento>
#         </cServico>
#     </servicos>
#     """
#
#     headers = {
#         'Content-Type': 'application/xml',
#         'Accept-Encoding': 'gzip, deflate',
#         'Accept': '*/*',
#         'Connection': 'keep-alive'
#     }
#
#     try:
#         # envia a requisição SOAP e trata a resposta
#         response = requests.post('http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx',
#                                  headers=headers,
#                                  data=dados.encode('utf-8'))
#
#         if response.status_code == 200:
#             # parsing do XML retornado
#             tree = ET.ElementTree(ET.fromstring(response.content))
#             root = tree.getroot()
#
#             servicos = root.findall('.//cServico')
#
#             results = []
#
#             for servico in servicos:
#                 code = servico.find('Codigo').text
#                 if code == '0':
#                     continue  # erro no serviço
#
#                 name = servico.find('Nome').text
#                 price = float(servico.find('Valor').text.replace(',', '.'))
#                 days = int(servico.find('PrazoEntrega').text)
#                 delivery_time = f'{days} dias úteis'
#
#                 results.append({
#                     'servico': name,
#                     'valor': price,
#                     'prazo': delivery_time
#                 })
#
#             return results
#
#         else:
#             return None
#
#     except Exception as e:
#         return None
#
#

#
#

