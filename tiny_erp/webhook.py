from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import requests

from io import BytesIO
from produtos.models import Produto, Subcategory
import os
from urllib.parse import urlparse
from produtos.models import Category, Subcategory, Variation,MateriaPrima
import time
from xflavors.settings import MEDIA_ROOT
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
from requests.exceptions import RequestException


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
    id_mapeamento_tiny = payload["idMapeamento"]
    print("SKU Mapeamento:", payload["skuMapeamento"])
    sku_mapeamento_tiny = payload["skuMapeamento"]
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

    except:
        print("Sem Arvore de Categoria")
    print("Payload", payload)
    localizacao = payload["localizacao"]
    print("localizacao:",localizacao)
    nome = payload["nome"]
    print("nome:", nome)
    print(payload["precoPromocional"])
    preco_promocional = payload["precoPromocional"]
    preco = payload["preco"]
    estoque = payload["estoqueAtual"]
    product_id = payload["id"]
    descricao = payload["descricaoComplementar"]
    marca = payload["marca"] if "marca" in payload else "marca não especificada"
    category, subcategoria = categoria_subcategoria(payload)
    print("Categoria e subcategoria",category, subcategoria)
    image_path = salva_imagem(payload)
    print("image_path:", image_path)
    # print("Payload",payload)

    print("Classe do produto", payload['classeProduto'])
    if payload['classeProduto'] == "M":
        print("Materia Prima")
        salvar_ou_atualizar_materia_prima(nome, estoque, product_id, id_mapeamento_tiny, sku_mapeamento_tiny)
    else:
        print("Produto")
        salvar_ou_atualizar_produto(nome, product_id, preco, category, subcategoria, estoque, image_path, descricao,
                                    marca, localizacao,preco_promocional,id_mapeamento_tiny, sku_mapeamento_tiny)
    print("Variações:")
    for variacao in payload["variacoes"]:
        print("  ID:", variacao["id"])
        variacao_id = variacao["id"]
        print("tentando obter infomacao da varicao")
        print("  ID Mapeamento:", variacao["idMapeamento"])
        print("  SKU Mapeamento:", variacao["skuMapeamento"])
        id_mapeamento = variacao["idMapeamento"]
        sku_mapeamento = variacao["skuMapeamento"]
        obter_info_produto(variacao_id, produto_pai,sku_mapeamento,id_mapeamento)


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
    print("salvando imagem")

    if payload.get('classeProduto') == 'M':
        url_imagem = 'https://www.arteshowestruturas.com.br/wp-content/uploads/sites/699/2017/01/SEM-IMAGEM.jpg'
    else:
        url_imagem = None
        if 'anexos' in payload:
            for anexo in payload["anexos"]:
                if 'url' in anexo:
                    url_imagem = anexo["url"]
                    break
                else:
                    print("Chave 'url' não encontrada no anexo")
        else:
            print("Chave 'anexos' não encontrada no payload")

        if not url_imagem:
            url_imagem = 'https://www.arteshowestruturas.com.br/wp-content/uploads/sites/699/2017/01/SEM-IMAGEM.jpg'

    print("url_imagem", url_imagem)

    try:
        response = requests.get(url_imagem)
        response.raise_for_status()
    except RequestException as e:
        print(f"Erro ao fazer a requisição para a URL da imagem: {e}")
        return None

    try:
        with Image.open(BytesIO(response.content)) as img:
            width, height = img.size
            if width < tamanho_padrao[0] or height < tamanho_padrao[1]:
                img = img.resize(tamanho_padrao)
            else:
                img.thumbnail(tamanho_padrao)

            url_parts = urlparse(url_imagem)
            filename = os.path.basename(url_parts.path)

            with open(os.path.join(MEDIA_ROOT+"/products", filename), 'wb') as f:
                img.save(f)

            image_path = os.path.join('products', filename)
            return image_path
    except UnidentifiedImageError:
        print("Erro ao abrir a imagem. O arquivo pode estar corrompido ou ter um formato inválido.")
        return None
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None


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

        if payload['classeProduto'] == "M":
            pass
        else:
            category, created = Category.objects.get_or_create(name=category, description='categoria')
            subcategoria, created = Subcategory.objects.get_or_create(name=subcategoria, description='categoria',
                                                                      category=category)
    except:
        if payload['classeProduto'] == "M":
            pass
        else:
            category = 'Sem Categoria'
            subcategoria = 'Sem Subcategoria'
            category, created = Category.objects.get_or_create(name=category, description='categoria')
            subcategoria, created = Subcategory.objects.get_or_create(name=subcategoria, description='categoria',
                                                                      category=category)
    return category, subcategoria




def obter_info_produto(product_id, produtopai,sku_mapeamento,id_mapeamento):
    time.sleep(5)
    print("Obtendo Informacao do produto:", product_id)
    url = 'https://api.tiny.com.br/api2/produto.obter.php'
    token = TINY_ERP_API_KEY

    if not token:
        print("Erro: TINY_ERP_API_KEY não está configurado.")
        return

    params = {
        'token': token,
        'formato': 'json',
        'id': product_id,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar informações do produto: {e}")
        return

    if 'retorno' not in response.json():
        print("Campo 'retorno' não encontrado na resposta da API.")
        return

    produto = response.json()['retorno']

    if 'produto' not in produto:
        print("Campo 'produto' não encontrado no retorno da API.")
        return

    produto_info = produto['produto']

    gasto = produto_info.get('kit', [])
    materia_prima = gasto[0]['item']['id_produto'] if gasto else product_id

    estoque = 0
    nome_simplificado = produto_info.get('grade', '')

    unidade = produto_info.get('unidade')
    if unidade is None:
        print("Erro ao obter a unidade do produto.")
        return

    print("UNIDADE:", unidade)

    print("obtendo_materia_prima")
    obtendo_materia_prima(materia_prima)
    print('tentando salvar variacao')
    salvar_ou_atualizar_variacao(produtopai, produto, estoque, nome_simplificado, gasto, unidade,sku_mapeamento,id_mapeamento)




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





def salvar_ou_atualizar_produto(nome, product_id, preco, category, subcategoria, estoque, image_path, descricao, marca,localizacao,preco_promocional,id_mapeamento_tiny, sku_mapeamento_tiny):
    print("Nome", nome,
          "Id", product_id,
          "Preco", preco,
          "Categoria", category,
          "Subcategoria", subcategoria,
          "Estoque", estoque,
          "Image_path", image_path,
          "Descricao", descricao,
          "Marca", marca,
          "Localizacao",localizacao,
          "preco_promocional",preco_promocional)
    print("Criando/Atualizando produto")
    try:
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
                'marca': marca,
                'localizacao':localizacao,
                'preco_promocional':preco_promocional,
                "id_mapeamento_tiny": id_mapeamento_tiny,
                "sku_mapeamento_tiny" : sku_mapeamento_tiny
            }
        )
    except ValidationError as e:
        print(f"Erro de validação: {e}")
    except Exception as e:
        print(f"Erro inesperado ao atualizar ou criar Produto: {e}")
    print("Criado/Atualizado")
    print(obj, created)


def salvar_ou_atualizar_variacao(produtopai, produto, estoque, nome_simplificado, gasto, unidade,sku_mapeamento,id_mapeamento):
    print('salvando variacao')
    dicionario = nome_simplificado
    nome_simplificado = ' '.join([str(chave) + ' ' + str(valor) for chave, valor in dicionario.items()])

    # Aqui você pode obter o objeto MateriaPrima correspondente ao ID da matéria-prima
    try:
        materia_prima = gasto[0]['item']['id_produto']
        materia_prima = MateriaPrima.objects.get(id=materia_prima)
        print(materia_prima)
    except:
        if gasto == 0:
            materia_prima = MateriaPrima.objects.get(id=produto['produto']['id'])
        else:
            materia_prima = None

    print('Materia Prima 2', materia_prima)
    try:
        gasto = gasto[0]['item']['quantidade']
    except:
        gasto = 1
    print(gasto)

    pai = Produto.objects.get(id=produtopai)
    print("PRECO", produto['produto'])
    print("PRECO", produto['produto']['preco'])
    print("PRECOPROMOCIONAL", produto['produto']['preco_promocional'])
    preco_promocional = produto['produto']['preco_promocional']
    preco = produto['produto']['preco']



    try:
        Variation.objects.update_or_create(
            id=produto['produto']['id'],
            produto_pai=pai,
            defaults={'name': produto['produto']['nome'],
                      'price': preco,
                      'stock': estoque,
                      'nome_simplificado': nome_simplificado,
                      'gasto': gasto,
                      'materia_prima': materia_prima,
                      'unidade': unidade,
                      'preco_promocional':preco_promocional,
                      'id_mapeamento_tiny':id_mapeamento,
                      'sku_mapeamento_tiny': sku_mapeamento
                      }
        )
    except ValidationError as e:
        print(f"Erro de validação: {e}")
    except Exception as e:
        print(f"Erro inesperado ao atualizar ou criar Variacao: {e}")

def salvar_ou_atualizar_materia_prima(materia_prima_nome, estoque, materia_prima_id,id_mapeamento_tiny, sku_mapeamento_tiny):
    print("salvando materia prima")
    print("Nome materia prima" , materia_prima_nome)
    print("Estoque materia prima", estoque)
    print("ID materia prima", materia_prima_id)
    try:
        MateriaPrima.objects.update_or_create(
            id=materia_prima_id,

            defaults={'id': materia_prima_id,
                      'name': materia_prima_nome,
                      'stock': estoque,
                      "id_mapeamento_tiny":id_mapeamento_tiny,
                      "sku_mapeamento_tiny" : sku_mapeamento_tiny
                      }
        )
        print("Materia prima Salva ou atualizada")
    except ValidationError as e:
        print(f"Erro de validação: {e}")
    except Exception as e:
        print(f"Erro inesperado ao atualizar ou criar Materia Prima: {e}")













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
