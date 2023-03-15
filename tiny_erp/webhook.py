from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

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
    print("ID Mapeamento:", payload["idMapeamento"])
    print("SKU Mapeamento:", payload["skuMapeamento"])
    print("Nome:", payload["nome"])
    print("Código:", payload["codigo"])
    print("Unidade:", payload["unidade"])
    print("Preço:", payload["preco"])
    print("Preço Promocional:", payload["precoPromocional"])
    print("NCM:", payload["ncm"])
    print("Origem:", payload["origem"])
    print("GTIN:", payload["gtin"])
    print("GTIN Embalagem:", payload["gtinEmbalagem"])
    print("Localização:", payload["localizacao"])
    print("Peso Líquido:", payload["pesoLiquido"])
    print("Peso Bruto:", payload["pesoBruto"])
    print("Estoque Mínimo:", payload["estoqueMinimo"])
    print("Estoque Máximo:", payload["estoqueMaximo"])
    print("ID Fornecedor:", payload["idFornecedor"])
    print("Código Fornecedor:", payload["codigoFornecedor"])
    print("Código Pelo Fornecedor:", payload["codigoPeloFornecedor"])
    print("Unidade Por Caixa:", payload["unidadePorCaixa"])
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
    print("Tipo Embalagem:", payload["tipoEmbalagem"])
    print("Altura Embalagem:", payload["alturaEmbalagem"])
    print("Largura Embalagem:", payload["larguraEmbalagem"])
    print("Comprimento Embalagem:", payload["comprimentoEmbalagem"])
    print("Diâmetro Embalagem:", payload["diametroEmbalagem"])
    print("Classe Produto:", payload["classeProduto"])
    print("ID Categoria:", payload["idCategoria"])
    print("Descrição Categoria:", payload["descricaoCategoria"])
    print("Descrição Árvore Categoria:", payload["descricaoArvoreCategoria"])

    print("Árvore Categoria:")
    for categoria in payload["arvoreCategoria"]:
        print("  ID:", categoria["id"])
        print("  ID Pai:", categoria["idPai"])
        print("  Descrição:", categoria["descricao"])
        print("  Descrição Completa:", categoria["descricaoCompleta"])
        print()

    print("Variações:")
    for variacao in payload["variacoes"]:
        print("  ID:", variacao["id"])
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

    print("SEO:")
    seo = payload["seo"]
    print("  Title:", seo["title"])
    print("  Description:", seo["description"])
    print("  Keywords:", seo["keywords"])
    print("  Link Vídeo:", seo["linkVideo"])
    print("  Slug:", seo["slug"])

    print("Kit:")
    for kit in payload["kit"]:
        print("  ID:", kit["id"])
        print("  Quantidade:", kit["quantidade"])

    print("Dias de Preparação:", payload["diasPreparacao"])




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
