import os
from urllib.parse import urlparse
from xflavors.settings import MEDIA_ROOT
import requests
from pedidos.models import Produto
from produtos.models import Category, Subcategory, Variation,MateriaPrima
from django.shortcuts import  get_object_or_404
import time
from PIL import Image
from io import BytesIO
from xflavors.settings import TINY_ERP_API_KEY



def import_products():

    products = pesquisar_produtos()
    delay = 2  # 30 requests per minute

    for product in products:
        product_id = int(product['produto']['id'])
        print(product_id)

        response = obter_info_produto(product_id)
        estoque = obter_info_estoque_produto(product_id)

        produto = response.json()['retorno']

        if produto['produto']['classe_produto'] in ['M', 'O']:
            salvar_ou_atualizar_materia_prima(produto,estoque,product_id)
            continue

        produtopai = produto['produto']['idProdutoPai']
        descricao = produto['produto']['descricao_complementar']
        marca = produto['produto']['marca']
        unidade = produto['produto']['unidade']

        categoria_completa = produto['produto']['categoria']

        category,subcategoria = pegar_category_e_subcategory(categoria_completa)

        if produtopai == '0':
            image_path = pegar_imagem(produto)
            salvar_ou_atualizar_produto(produto, product_id, category, subcategoria, estoque, image_path,descricao, marca)
        else:
            nome_simplificado = produto['produto']['grade']
            try:
                gasto = produto['produto']['kit']
            except:
                gasto = 1
            salvar_ou_atualizar_variacao(produtopai, produto, estoque,nome_simplificado,gasto,unidade)

        time.sleep(delay)

def pegar_category_e_subcategory(categoria_completa):
    if '>>' in categoria_completa:
        split_values = categoria_completa.split(' >> ')
        category = split_values[0]
        if len(split_values) > 2:
            subcategoria = ' >> '.join(split_values[1:])
        else:
            subcategoria = split_values[1]
    else:
        category = categoria_completa
        subcategoria = 'sem_subcategoria'

    category, created = Category.objects.get_or_create(name=category, description='categoria')
    subcategoria, created = Subcategory.objects.get_or_create(name=subcategoria, description='categoria', category=category)

    return category, subcategoria

def pesquisar_produtos():
    url = 'https://api.tiny.com.br/api2/produtos.pesquisa.php'
    token = TINY_ERP_API_KEY
    params = {'token': token, 'formato': 'json', 'pagina': '2'}
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
    token = TINY_ERP_API_KEY
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
    token = TINY_ERP_API_KEY
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
    tamanho_padrao = (800, 800)
    try:
        url_imagem = produto['produto']['imagens_externas'][0]['imagem_externa']['url']
    except:
        url_imagem = 'https://www.arteshowestruturas.com.br/wp-content/uploads/sites/699/2017/01/SEM-IMAGEM.jpg'

    if url_imagem:
        # Faz uma nova requisição para baixar a imagem
        response = requests.get(url_imagem)
        if response.status_code == 200:
            # Extrai o nome do arquivo da URL da imagem
            url_parts = urlparse(url_imagem)
            filename = os.path.basename(url_parts.path)

            # Redimensiona a imagem
            with Image.open(BytesIO(response.content)) as img:
                width, height = img.size
                if width < tamanho_padrao[0] or height < tamanho_padrao[1]:
                    # Caso a imagem seja menor que o tamanho padrão, redimensiona sem manter a proporção
                    img = img.resize(tamanho_padrao)
                else:
                    # Caso contrário, redimensiona mantendo a proporção
                    img.thumbnail(tamanho_padrao)

                # Salva a imagem na pasta "media" do projeto
                with open(os.path.join(MEDIA_ROOT+"/products", filename), 'wb') as f:
                    img.save(f)
                image_path = os.path.join('products', filename)
                return image_path
    else:
        print("ERRO ao pegar imagem")

def salvar_ou_atualizar_produto(produto,product_id,category,subcategoria,estoque,image_path,descricao,marca):
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
                                'marca': marca
                            }
                        )
     print(obj,created)

def salvar_ou_atualizar_variacao(produtopai,produto,estoque,nome_simplificado,gasto,unidade):
    dicionario = nome_simplificado
    nome_simplificado = ' '.join([str(chave) + ' ' + str(valor) for chave, valor in dicionario.items()])

    # Aqui você pode obter o objeto MateriaPrima correspondente ao ID da matéria-prima
    try:
        materia_prima = gasto[0]['item']['id_produto']
        materia_prima = MateriaPrima.objects.get(id=materia_prima)
        print(materia_prima)
    except:
        materia_prima = None

    print('Materia Prima',materia_prima)
    try:
        gasto= gasto[0]['item']['quantidade']
    except:
        gasto = 1
    print(gasto)


    pai = Produto.objects.get(id=produtopai)
    Variation.objects.update_or_create(
        id=produto['produto']['id'],
        produto_pai=pai,
        defaults={'name': produto['produto']['nome'],
                  'price': produto['produto']['preco'],
                  'stock': estoque,
                  'nome_simplificado': nome_simplificado,
                  'gasto':gasto,
                  'materia_prima':materia_prima,
                  'unidade':unidade
                        }
    )

def salvar_ou_atualizar_materia_prima(produto,estoque,product_id):


    MateriaPrima.objects.update_or_create(
        id=produto['produto']['id'],

        defaults={'id': product_id,
                    'name': produto['produto']['nome'],
                  'stock': estoque,
                                        }
                                            )
