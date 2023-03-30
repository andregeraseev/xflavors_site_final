import os
from urllib.parse import urlparse

import requests
from pedidos.models import Produto
from produtos.models import Category, Subcategory, Variation
from django.shortcuts import  get_object_or_404

token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'


def search_products():
    # URL of the Tiny ERP API
    url = 'https://api.tiny.com.br/api2/produtos.pesquisa.php'
    # API access token
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    # Parameters for the request
    params = {
        'token': token,
        'formato': 'json',
        'pagina': '1',
    }
    # Sends the request to the API
    response = requests.get(url, params=params)

    # Checks if the request was successful
    if response.status_code == 200:
        # Converts the response to a JSON object
        products = response.json()['retorno']['produtos']
        return products
    else:
        # The request failed
        print('Error while importing products from Tiny ERP: {}'.format(response.text))


def import_products():
    category = get_object_or_404(Category, name='Essencias')
    subcategoria = get_object_or_404(Subcategory, name='TPA')
    # categoria= Category.get(nome='Essencias')

    # URL da API do Tiny ERP
    url = 'https://api.tiny.com.br/api2/produtos.pesquisa.php'
    # Token de acesso à API
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    # Parâmetros da requisição
    params = {
        'token': token,
        'formato': 'json',
        'pagina': '1',
    }
    # Faz a requisição à API
    response = requests.get(url, params=params)

    # Verifica se a requisição foi bem sucedida
    if response.status_code == 200:
        # Converte a resposta em um objeto JSON
        products = response.json()['retorno']['produtos']

        # Cria um objeto Produto para cada produto retornado pela API
        for product in products:
            print(product['produto']['nome'], "name")
            print(product['produto']['preco'], "price")
            # Obtém o ID do produto
            product_id = int(product['produto']['id'])
            print(product_id)

            # Faz uma nova requisição para obter as informações do produto, incluindo a URL da imagem
            url = 'https://api.tiny.com.br/api2/produto.obter.php'
            params = {
                'token': token,
                'formato': 'json',
                'id': product_id,
            }
            response = requests.get(url, params=params)
            print(response)

            # Faz uma nova requisição para obter as informações de estoque do produto
            url_estoque = 'https://api.tiny.com.br/api2/produto.obter.estoque.php'
            params_estoque = {
                'token': token,
                'formato': 'json',
                'id': product_id,
            }
            response_estoque = requests.get(url_estoque, params=params_estoque)
            print(response_estoque,'ESTOQUEEEE')
            # Verifica se a requisição foi bem sucedida
            if response_estoque.status_code == 200:
                # Converte a resposta em um objeto JSON
                estoque = response_estoque.json()['retorno']['produto']['saldo']
                print(estoque,'aquiii')


            # Verifica se a requisição foi bem sucedida
            if response.status_code == 200:

                # Converte a resposta em um objeto JSON
                produto = response.json()['retorno']

                # Verifica se o produto é uma matéria-prima
                if produto['produto']['classe_produto'] in ['M', 'O']:
                    # Se for uma matéria-prima, pula para o próximo produto
                    continue

                produtopai = produto['produto']['idProdutoPai']
                print('produtopai', produtopai)
                if produtopai == '0':
                    print('PAI 0', produtopai)
                    image_path= pegar_imagem(produto)
                    # url_imagem = produto['produto']['imagens_externas'][0]['imagem_externa']['url']
                    # print(url_imagem)

                    # if url_imagem:
                    #     # Faz uma nova requisição para baixar a imagem
                    #     response = requests.get(url_imagem)
                    #     if response.status_code == 200:
                    #         # Extrai o nome do arquivo da URL da imagem
                    #         url_parts = urlparse(url_imagem)
                    #         filename = os.path.basename(url_parts.path)
                    #
                    #         # Salva a imagem na pasta "media" do projeto
                    #         with open(os.path.join('media/products', filename), 'wb') as f:
                    #             f.write(response.content)

                    try:
                        # image_path = os.path.join('products', filename)
                        # Tenta buscar um produto com o mesmo nome
                        produto1 = Produto.objects.get(name=produto['produto']['nome'])

                        # Se o produto já existe, atualiza os campos
                        produto1.description = ''
                        produto1.price = produto['produto']['preco']
                        produto1.category = category
                        produto1.subcategory = subcategoria
                        produto1.stock = estoque
                        produto1.image = image_path
                        produto1.save()

                    except Produto.DoesNotExist:
                            # image_path = os.path.join('products', filename)
                            # Se o produto não existe, cria um novo
                            Produto.objects.create(
                                id= produto['produto']['id'],
                                name=produto['produto']['nome'],
                                description='',
                                price=produto['produto']['preco'],
                                category=category,
                                subcategory=subcategoria,
                                stock=estoque,
                                image=image_path,
                            )
                    else:
                        # A requisição para baixar a imagem falhou
                        print('Erro ao baixar imagem do produto ')
                else:
                    pai = Produto.objects.get(id=produtopai)
                    Variation.objects.update_or_create(
                        id=produto['produto']['id'],
                        produto_pai=pai,
                        defaults={'name': produto['produto']['nome'],
                                  'price': produto['produto']['preco'],
                                  'stock': estoque}
                    )




            else:
                # A requisição para obter informações do produto falhou
                print('Erro ao obter informações do produto')
        else:
            print('Erro ao obter informações do produto ')


    else:
        # A requisição falhou
        print('Erro ao importar produtos do Tiny ERP: {}'.format(response.text))

def pegar_imagem(produto):
    url_imagem = produto['produto']['imagens_externas'][0]['imagem_externa']['url']
    print(url_imagem)

    if url_imagem:
        # Faz uma nova requisição para baixar a imagem
        response = requests.get(url_imagem)
        if response.status_code == 200:
            # Extrai o nome do arquivo da URL da imagem
            url_parts = urlparse(url_imagem)
            filename = os.path.basename(url_parts.path)

            # Salva a imagem na pasta "media" do projeto
            with open(os.path.join('media/products', filename), 'wb') as f:
                f.write(response.content)
            image_path = os.path.join('products', filename)
            return image_path
    else:
        print("ERRO ao pegar imagem")


#
#
#

import os
from urllib.parse import urlparse

import requests
from pedidos.models import Produto
from produtos.models import Category, Subcategory, Variation
from django.shortcuts import  get_object_or_404
import time
token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'

def import_products():

    products = pesquisar_produtos()
    delay = 60 / 40  # 30 requests per minute

    for product in products:
        product_id = int(product['produto']['id'])
        print(product_id)

        response = obter_info_produto(product_id)
        estoque = obter_info_estoque_produto(product_id)

        produto = response.json()['retorno']

        if produto['produto']['classe_produto'] in ['M', 'O']:
            continue

        produtopai = produto['produto']['idProdutoPai']
        descricao = produto['produto']['descricao_complementar']
        categoria_completa = produto['produto']['categoria']

        category,subcategoria = pegar_category_e_subcategory(categoria_completa)

        if produtopai == '0':
            image_path = pegar_imagem(produto)
            salvar_ou_atualizar_produto(produto, product_id, category, subcategoria, estoque, image_path,descricao)
        else:
            salvar_ou_atualizar_variacao(produtopai, produto, estoque)

        time.sleep(delay)

def pegar_category_e_subcategory(categoria_completa):
    if '>>' in categoria_completa:
        category, subcategoria = categoria_completa.split(' >> ')
    else:
        category = categoria_completa
        subcategoria = 'sem_subcategoria'

    category, created = Category.objects.get_or_create(name=category, description='categoria')
    subcategoria, created = Subcategory.objects.get_or_create(name=subcategoria, description='categoria', category=category)

    return category, subcategoria

def pesquisar_produtos():
    url = 'https://api.tiny.com.br/api2/produtos.pesquisa.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    params = {'token': token, 'formato': 'json', 'pagina': '1'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        if 'erros' in response.json()['retorno']:
            erros = response.json()['retorno']['erros']
            for erro in erros:
                print('Erro ao ao pesquisar produtos: ' + erro['erro'])
        else:
            return response.json()['retorno']['produtos']
    else:
        print('Erro ao pesquisar produtos', response.status_code)

def obter_info_produto(product_id):
    url = 'https://api.tiny.com.br/api2/produto.obter.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    params = {
        'token': token,
        'formato': 'json',
        'id': product_id,
    }
    response = requests.get(url, params=params)
    print(response)

    if response.status_code == 200:
        return response
    else:
        print('Erro ao obter informações do produto',response.status_code)

def obter_info_estoque_produto(product_id):
    url_estoque = 'https://api.tiny.com.br/api2/produto.obter.estoque.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    params_estoque = {'token': token, 'formato': 'json', 'id': product_id}
    response_estoque = requests.get(url_estoque, params=params_estoque)

    if response_estoque.status_code == 200:
        if 'erros' in response_estoque.json()['retorno']:
            erros = response_estoque.json()['retorno']['erros']
            for erro in erros:
                print('Erro ao obter informações do estoque do produto: ' + erro['erro'])

        else:
            return response_estoque.json()['retorno']['produto']['saldo']

    else:
        error_descricao = response_estoque.json()['retorno']['erros'][0]['erro']
        print(f'Erro ao obter informações do estoque do produto{error_descricao}')
def pegar_imagem(produto):
    url_imagem = produto['produto']['imagens_externas'][0]['imagem_externa']['url']
    print(url_imagem)

    if url_imagem:
        # Faz uma nova requisição para baixar a imagem
        response = requests.get(url_imagem)
        if response.status_code == 200:
            # Extrai o nome do arquivo da URL da imagem
            url_parts = urlparse(url_imagem)
            filename = os.path.basename(url_parts.path)

            # Salva a imagem na pasta "media" do projeto
            with open(os.path.join('media/products', filename), 'wb') as f:
                f.write(response.content)
            image_path = os.path.join('products', filename)
            return image_path
    else:
        print("ERRO ao pegar imagem")

def salvar_ou_atualizar_produto(produto,product_id,category,subcategoria,estoque,image_path,descricao):
     obj, created = Produto.objects.update_or_create(
                            name=produto['produto']['nome'],
                            defaults={
                                'id':product_id,
                                'description': descricao,
                                'price': produto['produto']['preco'],
                                'category': category,
                                'subcategory': subcategoria,
                                'stock': estoque,
                                'image': image_path,
                            }
                        )
     print(obj,created)

def salvar_ou_atualizar_variacao(produtopai,produto,estoque):
    pai = Produto.objects.get(id=produtopai)
    Variation.objects.update_or_create(
        id=produto['produto']['id'],
        produto_pai=pai,
        defaults={'name': produto['produto']['nome'],
                  'price': produto['produto']['preco'],
                  'stock': estoque}
    )


#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa






import requests
import json

import requests
import json


def enviar_pedido_para_tiny(pedido):
    # Informações necessárias para criar o pedido no TinyERP
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    empresa = 'xflavors'
    nome = pedido.user.username
    telefone = pedido.user.cliente.celular
    email = pedido.user.email
    cpf = pedido.user.cliente.cpf
    total = float(pedido.total)
    id_pedido = pedido.id

    # Monta a estrutura do pedido para enviar à API
    itens = []
    for item in pedido.itens.all():
        if item.variation:
            nome_item = item.variation.name
            id_item = item.variation.id
        else:
            nome_item = item.product.name
            id_item = item.id
        # print(nome_item,id_item, 'DESCRICAO')
        item_price = float(item.price)
        itens.append({
            'descricao': nome_item,
            'codigo': id_item,
            'qtde': item.quantity,
            'valor': item_price,
            'un': 'UN',
        })
    print(itens)
    pedido_data = {
  "pedido": {
    "data_pedido": "04/03/2023",
    "data_prevista": "05/03/2023",
    "cliente": {
      "codigo": "1235",
      "nome": nome,

      "tipo_pessoa": "F",
      "cpf_cnpj": cpf,

      "endereco": "Rua Teste",
      "numero": "123",
      "complemento": "sala 2",
      "bairro": "Teste",
      "cep": "95700000",
      "cidade": "Bento Gonçalves",
      "uf": "RS",
      "fone": "5430553808"
    },
     'itens': itens,

      "valor_frete": "35.00",
      "valor_desconto": "0",
      "numero_pedido_ecommerce": id_pedido,
      "situacao": "Aberto",
      "obs": "Observações do Pedido",
      "forma_envio": "c",
      "forma_frete": "PAC",
  }
}

    # Envia o pedido para o TinyERP via API
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    params = {
        'token': token,
        'formato': 'json',
        'pedido': json.dumps(pedido_data),
    }

    response = requests.post(url, params=params)

    try:
        json.dumps(pedido_data)
    except ValueError as e:
        print('Erro ao criar JSON do pedido:')
        print(str(e))
        return False
    print(params)
    # response = requests.post(url, json=pedido_data, headers=headers, params=params)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        status_processamento = response_data.get('retorno', {}).get('status_processamento')

        if status_processamento == 'sucesso':
            return True
        else:
            print('Erro ao enviar pedido para o TinyERP')
            response_data = response.json()
            if response_data['retorno']['status'] == 'Erro':
                print(response_data['retorno']['registros'])
    return False

# 2222222222222222222222222222222222222222222

import requests
import json

import requests
import json


def enviar_pedido_para_tiny(pedido):
    # Informações necessárias para criar o pedido no TinyERP
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    empresa = 'xflavors'
    nome = pedido.user.username
    telefone = pedido.user.cliente.celular
    email = pedido.user.email
    cpf = pedido.user.cliente.cpf
    total = float(pedido.total)
    id_pedido = pedido.id

    # Monta a estrutura do pedido para enviar à API
    itens = []
    for item in pedido.itens.all():
        item_price = float(item.price)
        itens.append({
            "codigo": item.product.id,
            "id_produto": item.product.id,
            "descricao": "TESTE 1",
            "quantidade": item.quantity,
            "valor_unitario": item_price,
            "unidade": "UN",
        })

    pedido_data = {
  "pedido": {
    "data_pedido": "04/03/2023",
    "data_prevista": "05/03/2023",
    "cliente": {
      "codigo": "1235",
      "nome": nome,

      "tipo_pessoa": "F",
      "cpf_cnpj": cpf,

      "endereco": "Rua Teste",
      "numero": "123",
      "complemento": "sala 2",
      "bairro": "Teste",
      "cep": "95700000",
      "cidade": "Bento Gonçalves",
      "uf": "RS",
      "fone": "5430553808"
    },
    "itens": itens,

      "valor_frete": "35.00",
      "valor_desconto": "0",
      "numero_pedido_ecommerce": id_pedido,
      "situacao": "Aberto",
      "obs": "Observações do Pedido",
      "forma_envio": "c",
      "forma_frete": "PAC",
  }
}

    # Envia o pedido para o TinyERP via API
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = 'a39bbddfcec2a176fe2cc12fc9fbb1467bf2aa47'
    params = {
        'token': token,
        'formato': 'json',
        'pedido': json.dumps(pedido_data),
    }

    response = requests.post(url, params=params)

    try:
        json.dumps(pedido_data)
    except ValueError as e:
        print('Erro ao criar JSON do pedido:')
        print(str(e))
        return False
    print(params)
    # response = requests.post(url, json=pedido_data, headers=headers, params=params)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        status_processamento = response_data.get('retorno', {}).get('status_processamento')

        if status_processamento == 'sucesso':
            return True
        else:
            print('Erro ao enviar pedido para o TinyERP')
            response_data = response.json()
            if response_data['retorno']['status'] == 'Erro':
                print(response_data['retorno']['registros'])
    return False

