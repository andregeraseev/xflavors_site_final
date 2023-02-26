import os
from urllib.parse import urlparse

import requests
from pedidos.models import Produto
from produtos.models import Category, Subcategory, Variation
from django.shortcuts import  get_object_or_404
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
        'id': 675801806,
    }

    # Faz a requisição à API
    response = requests.get(url, params=params)

    # print(response.content.decode('utf-8'))
    # print(response,"RESPOSSE")
    # Verifica se a requisição foi bem sucedida
    if response.status_code == 200:
        # Converte a resposta em um objeto JSON
        products = response.json()['retorno']['produtos']
        # print(products, "products")
        # print(products, "Products")
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
            # Verifica se a requisição foi bem sucedida
            if response.status_code == 200:

                # Converte a resposta em um objeto JSON
                produto = response.json()['retorno']

                produtopai = produto['produto']['idProdutoPai']
                print('produtopai', produtopai)
                if produtopai == '0':
                    print('PAI 0', produtopai)
                    # print('produtopai',produtopai)
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

                            try:
                                image_path = os.path.join('products', filename)
                                # Tenta buscar um produto com o mesmo nome
                                produto1 = Produto.objects.get(name=produto['produto']['nome'])

                                # Se o produto já existe, atualiza os campos
                                produto1.description = ''
                                produto1.price = produto['produto']['preco']
                                produto1.category = category
                                produto1.subcategory = subcategoria
                                produto1.stock = 1
                                produto1.image = image_path
                                produto1.save()

                            except Produto.DoesNotExist:
                                image_path = os.path.join('products', filename)
                                # Se o produto não existe, cria um novo
                                Produto.objects.create(
                                    id= produto['produto']['id'],
                                    name=produto['produto']['nome'],
                                    description='',
                                    price=produto['produto']['preco'],
                                    category=category,
                                    subcategory=subcategoria,
                                    stock=1,
                                    image=image_path,
                                )
                        else:
                            # A requisição para baixar a imagem falhou
                            print('Erro ao baixar imagem do produto ')
                else:

                        pai = Produto.objects.get(id=produtopai)
                        Variation.objects.create(

                            id=produto['produto']['id'],
                            name=produto['produto']['nome'],
                            price=produto['produto']['preco'],
                            stock=1,
                            produto_pai= pai
                        )




            else:
                # A requisição para obter informações do produto falhou
                print('Erro ao obter informações do produto')
        else:
            print('Erro ao obter informações do produto ')

    # name = models.CharField(max_length=255)
            # description = models.TextField()
            # price = models.DecimalField(max_digits=10, decimal_places=2)
            # image = models.ImageField(upload_to='products')
            # slug = models.SlugField(max_length=255, unique=True, blank=True)
            # stock = models.PositiveIntegerField()
            # category = models.ForeignKey(Category, on_delete=models.CASCADE)
            # subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
            # variations = models.ManyToManyField(Variation, blank=True)
            # peso = models.DecimalField(max_digits=10, decimal_places=2, default=0.04)



            # Produto.objects.create(
            #     name=product['produto']['nome'],
            #     description=' ',
            #     price=product['produto']['preco'],
            #     category= category,
            #     subcategory = subcategoria,
            #     stock= 1,
            #     # outros campos do seu modelo de Produto...
            # )
    else:
        # A requisição falhou
        print('Erro ao importar produtos do Tiny ERP: {}'.format(response.text))