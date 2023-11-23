from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from produtos.models import Produto, Variation
import json
import logging

logger = logging.getLogger('webhook')
@csrf_exempt
def tiny_webhook_price_update(request):
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    payload = json.loads(request.body)
    logger.info(f"payload recebido {payload}")
    # Valida o payload com base na estrutura fornecida
    required_fields = ['cnpj', 'idEcommerce', 'tipo', 'versao', 'dados']
    dados_fields = ['idMapeamento', 'skuMapeamento', 'nome', 'codigo', 'preco']

    for field in required_fields:
        if field not in payload:
            logger.error(f"Campo {field} não encontrado no payload")
            return HttpResponseBadRequest(f"Campo {field} não encontrado no payload")

    for field in dados_fields:
        if field not in payload['dados']:
            logger.error(f"Campo {field} não encontrado em dados")
            return HttpResponseBadRequest(f"Campo {field} não encontrado em dados")

    # Processa o payload e atualiza os modelos correspondentes
    try:
        if not payload['dados'].get('skuMapeamentoPai'):
            logger.info(f"mudando preco produto {payload['dados']['nome']}, de {payload['dados']['preco']} e"
                        f" {payload['dados'].get('precoPromocional', None)}")
            # Trata como um Produto
            produto, created = Produto.objects.get_or_create(sku_mapeamento_tiny=payload['dados']['skuMapeamento'])
            produto.name = payload['dados']['nome']
            produto.price = payload['dados']['preco']
            produto.preco_promocional = payload['dados'].get('precoPromocional', None)
            produto.save()
            # Retorna o status HTTP 200 para confirmar o recebimento
            return HttpResponse("Payload recebido com sucesso", status=200)

        else:

            # Trata como uma Variation
            try:

                variation, created = Variation.objects.get_or_create(sku_mapeamento_tiny=payload['dados']['skuMapeamento'])
                if created == False:
                    logger.info(f"mudando preco variacao {variation}, de {variation.price} e {variation.preco_promocional} para "
                                f"{payload['dados']['preco']} e {payload['dados'].get('precoPromocional', None)}")
                else:
                    logger.info(f"criando variacao ")

                variation.name = payload['dados']['nome']
                variation.price = payload['dados']['preco']
                variation.preco_promocional = payload['dados'].get('precoPromocional', None)
                # Aqui você pode definir outros campos da Variation, se necessário
                variation.save()
                # Retorna o status HTTP 200 para confirmar o recebimento
                return HttpResponse("Payload recebido com sucesso", status=200)

            except Exception as e:
                logger.error(f"Erro ao atualizar a variação com o payload {payload}. Detalhes: {str(e)}")
                return HttpResponseBadRequest(str(e))

    except Exception as e:
        logger.error(f"Erro ao atualizar o produto ou variação com o payload {payload}. Detalhes: {str(e)}")
        return HttpResponseBadRequest(str(e))

