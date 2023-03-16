from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from PIL import Image
from io import BytesIO
from produtos.models import Produto, Subcategory
import os
from urllib.parse import urlparse
from produtos.models import Category, Subcategory, Variation,MateriaPrima
import time
from xflavors.settings import MEDIA_ROOT
@csrf_exempt
def tiny_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    payload = parse_payload(request.body)
    if payload is None:
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    print_payload_data(payload['dados'])
    if payload['tipo'] == 'produto':
        response_data = process_product_event(payload['dados'])
        if response_data is None:
            return HttpResponseBadRequest("Erro ao processar evento de produto")
        else:
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
    else:
        return HttpResponse(json.dumps({'error': 'Tipo de evento desconhecido'}), status=400,
                            content_type="application/json")

def parse_payload(request_body):
    try:
        return json.loads(request_body.decode("utf-8"))
    except json.JSONDecodeError:
        return None

def process_product_event(dados_produto):
    try:
        variacoes = [dados_produto] + dados_produto.get('variacoes', [])
        mapeamentos = []
        print(dados_produto['classeProduto'], 'CLASSEDOPRODUTO')
        print(dados_produto['kit'], 'KIT')

        for prod in variacoes:
            id_mapeamento = prod['idMapeamento']
            sku_mapeamento = prod['codigo']

            mapeamento = {
                'idMapeamento': id_mapeamento,
                'skuMapeamento': sku_mapeamento
            }
            mapeamentos.append(mapeamento)

        return mapeamentos

    except Exception as e:
        return None





def print_payload_data(payload):
    print("ID:", payload["id"])
    produto_pai = payload["id"]

    print("ID Mapeamento:", payload["idMapeamento"])
    print("SKU Mapeamento:", payload["skuMapeamento"])
    print("Nome:", payload["nome"])

    print("Código:", payload["codigo"])
    print("Unidade:", payload["unidade"])
    print("Preço:", payload["preco"])

    print("Preço Promocional:", payload["precoPromocional"])
    # print("NCM:", payload["ncm"])
    # print("Origem:", payload["origem"])
    # print("GTIN:", payload["gtin"])
    # print("GTIN Embalagem:", payload["gtinEmbalagem"])
    # print("Localização:", payload["localizacao"])
    # print("Peso Líquido:", payload["pesoLiquido"])
    # print("Peso Bruto:", payload["pesoBruto"])
    # print("Estoque Mínimo:", payload["estoqueMinimo"])
    # print("Estoque Máximo:", payload["estoqueMaximo"])
    # print("ID Fornecedor:", payload["idFornecedor"])
    # print("Código Fornecedor:", payload["codigoFornecedor"])
    # print("Código Pelo Fornecedor:", payload["codigoPeloFornecedor"])
    # print("Unidade Por Caixa:", payload["unidadePorCaixa"])
    print("Estoque Atual:", payload["estoqueAtual"])

    print("Preço Custo:", payload["precoCusto"])
    print("Preço Custo Médio:", payload["precoCustoMedio"])
    print("Situação:", payload["situacao"])
    print("Descrição Complementar:", payload["descricaoComplementar"])

    print("Observações:", payload["obs"])
    print("Garantia:", payload["garantia"])
    print("CEST:", payload["cest"])
    print("Sob Encomenda:", payload["sobEncomenda"])
    print("Marca:", payload["marca"])

    # print("Tipo Embalagem:", payload["tipoEmbalagem"])
    # print("Altura Embalagem:", payload["alturaEmbalagem"])
    # print("Largura Embalagem:", payload["larguraEmbalagem"])
    # print("Comprimento Embalagem:", payload["comprimentoEmbalagem"])
    # print("Diâmetro Embalagem:", payload["diametroEmbalagem"])
    # print("Classe Produto:", payload["classeProduto"])
    # print("ID Categoria:", payload["idCategoria"])
    # print("Descrição Categoria:", payload["descricaoCategoria"])

    print("Descrição Árvore Categoria:", payload["descricaoArvoreCategoria"])

    print("Árvore Categoria:")
    try:
        for categoria in payload["arvoreCategoria"]:
            print("  ID:", categoria["id"])
            print("  ID Pai:", categoria["idPai"])
            print("  Descrição:", categoria["descricao"])
            print("  Descrição Completa:", categoria["descricaoCompleta"])
            print()
    except:
        print("Sem Arvore de Categoria")

    nome = payload["nome"]
    preco = payload["preco"]
    estoque = payload["estoqueAtual"]
    product_id = payload["id"]
    descricao = payload["descricaoComplementar"]
    marca = payload["marca"]
    category, subcategoria = categoria_subcategoria(payload)
    image_path = salva_imagem(payload)

    print("Classe do produto", payload['classeProduto'])
    if payload['classeProduto'] == "M":
        print("Materia Prima")
        salvar_ou_atualizar_materia_prima(nome, estoque, product_id)
    else:
        print("Produto")
        salvar_ou_atualizar_produto(nome, product_id, preco, category, subcategoria, estoque, image_path, descricao, marca)
    print("Variações:")
    for variacao in payload["variacoes"]:
        print("  ID:", variacao["id"])
        variacao_id = variacao["id"]
        obter_info_produto(variacao_id, produto_pai)
        print("  ID Mapeamento:", variacao["idMapeamento"])
        print("  SKU Mapeamento:", variacao["skuMapeamento"])
        print("  Código:", variacao["codigo"])
        print("  GTIN:", variacao["gtin"])
        print("  Preço:", variacao["preco"])
        print("  Preço Promocional:", variacao["precoPromocional"])
        print("  Estoque Atual:", variacao["estoqueAtual"])

        print("  Grade:")
        for grade in variacao["grade"]:
            print("    Chave:", grade["chave"])
            print("    Valor:", grade["valor"])

        print("  Anexos:")
        for anexo in variacao["anexos"]:
            print("    URL:", anexo["url"])
            print("    Nome:", anexo["nome"])
            print("    Tipo:", anexo["tipo"])



    print("Anexos:")
    for anexo in payload["anexos"]:
        print("  URL:", anexo["url"])
        print("  Nome:", anexo["nome"])
        print("  Tipo:", anexo["tipo"])





    # print("SEO:")
    # seo = payload["seo"]
    # print("  Title:", seo["title"])
    # print("  Description:", seo["description"])
    # print("  Keywords:", seo["keywords"])
    # print("  Link Vídeo:", seo["linkVideo"])
    # print("  Slug:", seo["slug"])

    print("Kit:")
    for kit in payload["kit"]:
        print("  ID:", kit["id"])
        print("  Quantidade:", kit["quantidade"])



def salva_imagem(payload):
    tamanho_padrao = (800, 800)
    try:
        for anexo in payload["anexos"]:
            url_imagem = anexo["url"]
        print(url_imagem)
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


def categoria_subcategoria(payload):
    try:
        categoria_completa = payload["descricaoArvoreCategoria"]
        if '>' in categoria_completa:
            split_values = categoria_completa.split(' > ')
            category = split_values[0]
            if len(split_values) > 2:
                subcategoria = ' > '.join(split_values[1:])
            else:
                subcategoria = split_values[1]
        else:
            category = categoria_completa
            subcategoria = 'sem_subcategoria'
        category, created = Category.objects.get_or_create(name=category, description='categoria')
        subcategoria, created = Subcategory.objects.get_or_create(name=subcategoria, description='categoria',
                                                                  category=category)
    except:
        category = 'Sem Categoria'
        subcategoria = 'Sem Subcategoria'
    return category, subcategoria




def obter_info_produto(product_id,produtopai):
    time.sleep(2)
    url = 'https://api.tiny.com.br/api2/produto.obter.php'
    token = TINY_ERP_API_KEY
    params = {
        'token': token,
        'formato': 'json',
        'id': product_id,
    }
    response = requests.get(url, params=params)
    produto= response.json()['retorno']
    print(response.json()['retorno']['produto']['kit'])
    gasto = response.json()['retorno']['produto']['kit']
    materia_prima = gasto[0]['item']['id_produto']
    estoque = 0
    nome_simplificado = produto['produto']['grade']

    try:
        gasto = produto['produto']['kit']
    except:
        gasto = 1
    unidade = produto['produto']['unidade']

    obtendo_materia_prima(materia_prima)


    salvar_ou_atualizar_variacao(produtopai, produto, estoque, nome_simplificado, gasto, unidade)



    print('MATERIA PRIMA 1', materia_prima)
    if response.status_code == 200:
        return response
    else:
        print('Erro ao obter informações do produto',response.status_code)


def obtendo_materia_prima(materia_prima):
    try:
        if materia_prima:
            url = 'https://api.tiny.com.br/api2/produto.obter.php'
            token = TINY_ERP_API_KEY
            params = {
                'token': token,
                'formato': 'json',
                'id': materia_prima,
            }
            resposta = requests.get(url, params=params)
            print(resposta.json()['retorno']['produto'], 'RESPOSTAAAAA')
            materia_prima_nome = resposta.json()['retorno']['produto']['nome']
            materia_prima_id = resposta.json()['retorno']['produto']['id']
            estoque = obter_info_estoque_materia_prima(materia_prima_id)
            salvar_ou_atualizar_materia_prima(materia_prima_nome, estoque, materia_prima_id)
        else:
            pass
    except:
        print('sem materia prima ')

def obter_info_estoque_materia_prima(product_id):
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





def salvar_ou_atualizar_produto(nome, product_id, preco, category, subcategoria, estoque, image_path, descricao, marca):
    obj, created = Produto.objects.update_or_create(
        id=product_id,
        defaults={
            'name': nome,
            'id': product_id,
            'description': descricao,
            'price': preco,
            'category': category,
            'subcategory': subcategoria,
            'stock': estoque,
            'image': image_path,
            'marca': marca
        }
    )
    print(obj, created)


def salvar_ou_atualizar_variacao(produtopai, produto, estoque, nome_simplificado, gasto, unidade):
    print('salvando variacao')
    dicionario = nome_simplificado
    nome_simplificado = ' '.join([str(chave) + ' ' + str(valor) for chave, valor in dicionario.items()])

    # Aqui você pode obter o objeto MateriaPrima correspondente ao ID da matéria-prima
    try:
        materia_prima = gasto[0]['item']['id_produto']
        materia_prima = MateriaPrima.objects.get(id=materia_prima)
        print(materia_prima)
    except:
        materia_prima = None

    print('Materia Prima 2', materia_prima)
    try:
        gasto = gasto[0]['item']['quantidade']
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
                  'gasto': gasto,
                  'materia_prima': materia_prima,
                  'unidade': unidade
                  }
    )


def salvar_ou_atualizar_materia_prima(materia_prima_nome, estoque, materia_prima_id):
    print("salvando materia prima")
    print("Nome materia prima" , materia_prima_nome)
    print("Estoque materia prima", estoque)
    print("ID materia prima", materia_prima_id)
    MateriaPrima.objects.update_or_create(
        id=materia_prima_id,

        defaults={'id': materia_prima_id,
                  'name': materia_prima_nome,
                  'stock': estoque,
                  }
    )














import json
import hmac
import hashlib
from django.http import HttpResponseBadRequest, HttpResponse
from xflavors.settings import TINY_ERP_API_KEY
from django.views.decorators.csrf import csrf_exempt







@csrf_exempt
def tiny_rastreio(request):
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    try:
        payload = json.loads(request.body.decode("utf-8"))
        print(payload)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    # Verifica a autenticidade do webhook
    secret = TINY_ERP_API_KEY
    # signature = request.headers.get("X-Tiny-Signature")
    # if not signature:
    #     return HttpResponseBadRequest("Assinatura não encontrada")
    # expected_signature = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    # if not hmac.compare_digest(signature, expected_signature):
    #     return HttpResponseBadRequest("Assinatura inválida")

    # Processa o evento de código de rastreio
    if payload['tipo'] == 'rastreio':
        print(payload)
        dados = payload['dados']
        codigo = dados['codigo']
        # Aqui você pode obter mais informações sobre o envio
        # ...

        # Crie uma resposta HTTP com o status de sucesso
        response_data = {
            'success': True
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
    else:
        return HttpResponse(json.dumps({'error': 'Falha ao decodificar JSON'}), status=400,
                            content_type="application/json")
