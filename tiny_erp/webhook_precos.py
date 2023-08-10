from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from produtos.models import Produto, Variation
import json

@csrf_exempt
def tiny_webhook_price_update(request):
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    payload = json.loads(request.body)

    # Valida o payload com base na estrutura fornecida
    required_fields = ['cnpj', 'idEcommerce', 'tipo', 'versao', 'dados']
    dados_fields = ['idMapeamento', 'skuMapeamento', 'nome', 'codigo', 'preco']

    for field in required_fields:
        if field not in payload:
            return HttpResponseBadRequest(f"Campo {field} não encontrado no payload")

    for field in dados_fields:
        if field not in payload['dados']:
            return HttpResponseBadRequest(f"Campo {field} não encontrado em dados")

    # Processa o payload e atualiza os modelos correspondentes
    try:
        if not payload['dados'].get('skuMapeamentoPai'):
            # Trata como um Produto
            produto, created = Produto.objects.get_or_create(codigo=payload['dados']['codigo'])
            produto.name = payload['dados']['nome']
            produto.price = payload['dados']['preco']
            produto.preco_promocional = payload['dados'].get('precoPromocional', None)
            produto.save()
        else:
            # Trata como uma Variation
            variation, created = Variation.objects.get_or_create(sku=payload['dados']['skuMapeamento'])
            variation.name = payload['dados']['nome']
            variation.price = payload['dados']['preco']
            variation.promotional_price = payload['dados'].get('precoPromocional', None)
            # Aqui você pode definir outros campos da Variation, se necessário
            variation.save()
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    # Retorna o status HTTP 200 para confirmar o recebimento
    return HttpResponse("Payload recebido com sucesso", status=200)
