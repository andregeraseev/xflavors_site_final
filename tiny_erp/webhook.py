import json
import hmac
import hashlib
from django.http import HttpResponseBadRequest, HttpResponse
from xflavors.settings import TINY_ERP_API_KEY
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def tiny_webhook(request):
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        print('deu errado')
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    try:
        print('lendo')
        payload = json.loads(request.body.decode("utf-8"))
        print(payload)
    except json.JSONDecodeError:
        print('falha')
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    # Verifica a autenticidade do webhook
    secret = TINY_ERP_API_KEY  # Substitua com o seu token secreto
    # signature = request.headers.get("X-Tiny-Signature")
    # if not signature:
    #     print('Assinatura não encontrada')
    #     return HttpResponseBadRequest("Assinatura não encontrada")
    # expected_signature = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    # if not hmac.compare_digest(signature, expected_signature):
    #     print('Assinatura inválida')
    #     return HttpResponseBadRequest("Assinatura inválida")


    # Processa o evento de produto
    if payload['tipo'] == 'produto':
        produto = payload['dados']

        nome = produto['nome']
        preco = produto['preco']
        id = produto['id']
        idMapeamento = produto['idMapeamento']
        skuMapeamento = produto['codigo']
        urlProduto = produto.get('urlProduto')
        urlImagem = produto.get('urlImagem')
        error = produto.get('error')

        response_data = {
            "mapeamentos": [{
                "mapeamento": {
                    "idMapeamento": idMapeamento,
                    "skuMapeamento": skuMapeamento,
                    "urlProduto": urlProduto,
                    "urlImagem": urlImagem,
                    "error": error
                },
            }]
        }

        return HttpResponse(json.dumps(response_data), content_type="application/json"), 200
    else:
        return HttpResponse(json.dumps({'error': 'Falha ao decodificar JSON'}), status=400,
                            content_type="application/json")
        # Retorna uma resposta de sucesso
    return HttpResponse(status=200)

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
