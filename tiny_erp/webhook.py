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
    except json.JSONDecodeError:
        print('falha')
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    # Verifica a autenticidade do webhook
    secret = TINY_ERP_API_KEY  # Substitua com o seu token secreto
    signature = request.headers.get("X-Tiny-Signature")
    if not signature:
        print('Assinatura não encontrada')
        return HttpResponseBadRequest("Assinatura não encontrada")
    expected_signature = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        print('Assinatura inválida')
        return HttpResponseBadRequest("Assinatura inválida")

    # Processa o evento de produto
    event_type = payload.get("event_type")
    print('event_type')
    if event_type == "inclusao_produto":
        # Lê as informações do produto
        produto = payload.get("produto")
        nome = produto.get("nome")
        preco = produto.get("preco")
        # Faça o que quiser com as informações do produto, como salvá-las em um banco de dados

    # Retorna uma resposta de sucesso
    return HttpResponse(status=200)