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
