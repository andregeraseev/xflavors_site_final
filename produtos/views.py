from django.db.models import Count
from avise.models import AvisoEstoque
from cart.models import Cart, CartItem
from django.shortcuts import render, get_object_or_404
#from cart.views import cria_item_carrinho ,verifica_qunatidade_carrinho_varivel, verifica_estoque_produto_com_variacao
from clientes.models import Cliente
from pedidos.models import PedidoItem, Pedido
from .models import Category, Subcategory, Produto, Favorito, Kit, Variation
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from tiny_erp.tiny_api import import_products
from tiny_erp.tiny_api import import_products
from django.http import JsonResponse
from django.views.decorators.http import require_GET



@require_GET
def search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        data = {'message': "Por favor, digite algo para realizar a busca."}
        return JsonResponse(data)

    products = Produto.objects.filter(name__icontains=query)
    data = {'results': []}
    if not products:
        data = {'message': "Sem Resultados."}
        return JsonResponse(data)

    for product in products:
        has_variation = product.variation_set.exists()
        url = product.get_absolute_url()
        product_data = {'id': product.id, 'name': product.name, 'url': url, 'price': product.preco_ou_valor_promocional, 'image_url': product.image.url, 'has_variation': has_variation}
        variations = []

        if product.variation_set.exists():
            for variation in product.variation_set.all():
                if variation.nome_simplificado:
                    variation_data = {'id': variation.id, 'name': variation.nome_simplificado, 'price': variation.preco_ou_valor_promocional}
                else:
                    variation_data = {'id': variation.id, 'name': variation.name, 'price': variation.preco_ou_valor_promocional}
                variations.append(variation_data)
            product_data['variations'] = variations

        data['results'].append(product_data)

    return JsonResponse(data)



def pagina_search(request, q):
    query = q
    products = Produto.objects.filter(name__icontains=query)


    if request.user.is_authenticated:
        avisos = AvisoEstoque.objects.filter(cliente=request.user, notificado=False)
    else:
        avisos = None

    produtos_notificados = [aviso.produto.id for aviso in avisos] if avisos else []
    context= { "products": products, "produtos_notificados":produtos_notificados}



    return  render(request, 'pagina_search.html', context)


def import_products_view(request):
    if request.method == 'GET':
        import_products()
        return HttpResponse('Produtos importados com sucesso!')

# def import_products_view(request):
#     import_products()
#     return redirect('admin:produtos_produto_changelist')


def produto_por_subcategoria(request, category_id, subcategory_id):
    # Busca todas as categorias e subcategorias para exibir no template
    category = Category.objects.all()
    subcategoria = Subcategory.objects.all()

    # Filtra a categoria e subcategoria selecionada
    category_filter = get_object_or_404(Category, pk=category_id)
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)

    # Filtra os produtos pela categoria e subcategoria selecionada
    produtos = Produto.objects.filter(category=category_filter, subcategory=subcategory).order_by('name')

    produtos_com_estoque = []
    produtos_sem_estoque = []

    for produto in produtos:
        if produto.get_stock > 9:
            produtos_com_estoque.append(produto)
        else:
            produtos_sem_estoque.append(produto)

    # Concatena as listas de produtos com estoque e sem estoque
    produtos = produtos_com_estoque + produtos_sem_estoque

    # Ordenação dos produtos
    ordenacao = request.GET.get('ordenacao')
    if ordenacao and not "None" in ordenacao:
        produtos = Produto.objects.filter(category=category_filter, subcategory=subcategory).order_by('name')

    if ordenacao == 'alfabetica':
        # Ordena em ordem alfabética pelo nome
        produtos = produtos.order_by('name')
    elif ordenacao == 'alfabetica_decrescente':
        # Ordena em ordem alfabética pelo nome
        produtos = produtos.order_by('-name')
    elif ordenacao == 'preco-crescente':
        # Ordena em ordem crescente pelo preço
        produtos = produtos.order_by('price')
    elif ordenacao == 'preco-decrescente':
        # Ordena em ordem decrescente pelo preço
        produtos = produtos.order_by('-price')
    elif ordenacao == 'mais-vendidos':
        # Ordena pelo número de vendas dos produtos, do maior para o menor
        produtos = produtos.order_by('-num_vendas')

    # Paginação dos produtos
    produtos_por_pagina = 20
    paginator = Paginator(produtos, produtos_por_pagina)
    pagina_numero = request.GET.get('pagina')
    pagina = paginator.get_page(pagina_numero)

    # Quantidade total de produtos no carrinho
    total_quantity_cart = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_quantity_cart = cart.total_quantity()
        except Cart.DoesNotExist:
            pass

    if request.user.is_authenticated:
        avisos = AvisoEstoque.objects.filter(cliente=request.user, notificado=False)
    else:
        avisos = None
    produtos_notificados = [aviso.produto.id for aviso in avisos] if avisos else []

    # Contexto para ser exibido no template
    context = {
        "produtos_notificados": produtos_notificados,
        'category_filter': category_filter,
        'subcategory': subcategory,
        'produtos': produtos,
        'pagina': pagina,
        'total_quantity_cart': total_quantity_cart,
        'subcategoria': subcategory,
        'category': category,
        'ordenacao': ordenacao,
    }

    # Renderiza o template 'produto_por_subcategoria.html' com o contexto
    return render(request, 'produto_por_subcategoria.html', context)

def product_detail(request, slug):
    # Obter o produto
    produto = get_object_or_404(Produto, slug=slug)

    # Obter o pedido item correspondente
    pedido_itens = PedidoItem.objects.filter(product=produto)

    # Obtenha todos os pedidos que contêm o item em questão
    # Obtenha todos os pedidos que contêm o produto em questão
    orders = Pedido.objects.filter(itens__in=pedido_itens, status__in=["Pago", "Enviado"]).order_by().values_list('id', flat=True).distinct()
    # print(("ORDERS",orders))
    # Obtenha todos os outros itens que aparecem nos mesmos pedidos que o item em questão
    related_item_ids = PedidoItem.objects.filter(pedido__in=orders).exclude(product=produto).annotate(
        count=Count('product')).order_by('-count')
    # print(related_item_ids, "ITENS")
    related_items = Produto.objects.filter(pedidoitem__in=related_item_ids).distinct()[:4]
    # print(related_items, "RELATED ITENS")
    # Ordene o dicionário pelos valores em ordem decrescente para obter os itens mais comuns



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


    if request.user.is_authenticated:
        avisos = AvisoEstoque.objects.filter(cliente=request.user, notificado=False)
    else:
        avisos = None
    produtos_notificados = [aviso.produto.id for aviso in avisos] if avisos else []

    context = {
        "produtos_notificados":produtos_notificados,
        'related_products': related_items,
        'product': produto,
        'total_quantity_cart': total_quantity_cart,
        'subcategoria': subcategoria,
        'category': category,
    }
    return render(request, 'product_detail.html', context)

def add_to_favorites(request, product_id):
    # Obtenha o produto que o usuário deseja adicionar aos favoritos
    produto = get_object_or_404(Produto, pk=product_id)
    user= request.user
    cliente = get_object_or_404(Cliente, user=user)
    # Verifique se o usuário já tem o produto em seus favoritos
    favorite, created = Favorito.objects.get_or_create(cliente=cliente)
    if produto in favorite.produto.all():
        # Remova o produto dos favoritos
        favorite.produto.remove(produto)
        print(favorite)
        status = 'removed'
        print("removido")
    else:
        # Adicione o produto aos favoritos
        favorite.produto.add(produto)
        status = 'added'
        print("adicionado")

    # Retorne uma resposta JSON com o status da operação
    return JsonResponse({'status': status})


def kit_detail(request, slug):
    kit = get_object_or_404(Kit, slug=slug)
    print(kit)
    items = []

    for variacao in kit.variacoes.all():
        items.append({
            'product': variacao.produto_pai.name
        })

    context = {
        'kit': kit,
        'kit_items': items
    }
    return render(request, 'kits/kit_detail.html', context)




def receitas(request):
    kits = Kit.objects.all()

    # Ordenação dos produtos
    ordenacao = request.GET.get('ordenacao')
    if ordenacao == 'alfabetica':
        # Ordena em ordem alfabética pelo nome
        kits = kits.order_by('name')
    elif ordenacao == 'alfabetica_decrescente':
        # Ordena em ordem alfabética pelo nome
        kits = kits.order_by('-name')
    elif ordenacao == 'preco-crescente':
        # Ordena em ordem crescente pelo preço
        kits = kits.order_by('price')
    elif ordenacao == 'preco-decrescente':
        # Ordena em ordem decrescente pelo preço
        kits = kits.order_by('-price')
    elif ordenacao == 'mais-vendidos':
        # Ordena pelo número de vendas dos produtos, do maior para o menor
        kits = kits.order_by('-num_vendas')
    else:
        # Ordenação padrão, caso nenhuma seja especificada
        kits = kits.order_by('name')  # ou qualquer outro campo que faça sentido

    # Paginação dos produtos
    produtos_por_pagina = 20
    paginator = Paginator(kits, produtos_por_pagina)
    pagina_numero = request.GET.get('pagina')
    pagina = paginator.get_page(pagina_numero)

    items = []

    for kit in kits:
        for variacao in kit.variacoes.all():
            items.append({
                'product': variacao.produto_pai.name
            })
    print(items)
    context = {
        'kits': kits,
        'kit_items': items,
        'pagina': pagina,
    }
    return render(request, 'kits/kits.html', context)


def adicionar_kit_ao_carrinho(request):
    user = request.user

    cart = Cart.get_or_create_cart(user)

    if request.method == "POST":
        # print("AQUIIIIIIIIIIIIIIIII")
        kit_id = request.POST.get("kit_id")
        kit = get_object_or_404(Kit, id=kit_id)
        kit.num_vendas += 1
        kit.save()
        # print("NUMERO DE VENDAS DO KIT", kit, kit.num_vendas)

        # print(kit_id)
        variation_ids = request.POST.getlist("variation_ids[]")
        # print(variation_ids)
        quantities = request.POST.getlist("quantities[]")
        # print(quantities)

        # Cria o carrinho se ainda não existe
        # user = request.user
        # cart_id = Cart.get_or_create_cart(user)

        # Adiciona cada variação ao carrinho
        for variation_id, quantity in zip(variation_ids, quantities):

            variation = Variation.objects.get(id=variation_id)
            quantity= int(quantity)
            # print(quantity)
            if variation:
                quantidade_materia_prima = variation.materia_prima.stock
                materia_prima_id = variation.materia_prima.id
                quantity = int(quantity)
                product = variation.produto_pai
                # try:
                #     verifica_qunatidade_carrinho_varivel(quantity, quantidade_materia_prima, variation, cart,
                #                                          materia_prima_id, product)
                # except ValueError as e:
                #     return JsonResponse({'success': False, 'error': str(e)})
                #
                # # except ValueError as e:
                # #     return JsonResponse({'success': False, 'error': str(e)})
                # quantity = int(quantity)
                # if quantity <= 0:
                #     continue
                # print(quantity,'QUANTIDE')
                # cria_item_carrinho(cart, product, variation, quantity)
                try:
                    cart.add_item(product, quantity, variation)
                except ValueError as e:
                    return JsonResponse({'success': False, 'error': str(e)})


        data = {"success": True, "message": "Kit adicionado ao carrinho com sucesso!"}
        return JsonResponse(data)

