from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def tiny_webhook_stock_update(request):
    print("ESTOQUEEEEE")
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    # Processa o evento de atualização de estoque
    print('ATUALIZANDO ESTOQUE')
    if payload['tipo'] == 'estoque':
        print('Estoque')

        try:
            estoque = payload['dados']
            print(estoque)
            id_mapeamento = estoque['idMapeamento']
            print(id_mapeamento)
            estoque_atual = estoque['saldo']
            print(estoque_atual)
            id_produto = estoque['idProduto']
            print(id_produto)

            # Faça algo com os dados de atualização de estoque, por exemplo, atualizar o estoque na sua plataforma

            # Retorna uma resposta de sucesso
            return HttpResponse(status=200)

        except Exception as e:
            # Trata o erro aqui e retorna uma resposta HTTP com o status 400 e uma mensagem de erro apropriada
            return HttpResponseBadRequest("Erro ao processar evento de atualização de estoque: {}".format(str(e)))

    else:
        return HttpResponseBadRequest("Tipo de evento desconhecido")