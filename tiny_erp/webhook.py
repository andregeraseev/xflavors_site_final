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
        print(payload)
        produto = payload['dados']

        nome = produto['nome']
        print(nome)
        preco = produto['preco']
        print(preco)
        id = produto['id']
        print(id)
        idMapeamento = produto['idMapeamento']
        print(idMapeamento)
        skuMapeamento = produto['codigo']
        # aqui você pode adicionar mais informações do produto que deseja exibir

        # Crie uma resposta HTTP com os dados do produto
        response_data = {
            "mapeamentos": [{
                "mapeamento": {
                    'idMapeamento': idMapeamento,
                    'skuMapeamento': 'produto123',
                    'id': id,
                    'nome': nome,
                    'preco': preco,
                },
            }]
        }


    # Retorna uma resposta de sucesso
    return HttpResponse(status=200)