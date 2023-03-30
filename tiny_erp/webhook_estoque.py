from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

from avise.views import check_aviso_estoque
from produtos.models import MateriaPrima, Produto

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
            # id_mapeamento = estoque['idMapeamento']
            # print(id_mapeamento)
            estoque_atual = estoque['saldo']
            print(estoque_atual)
            id_produto = estoque['idProduto']
            print(id_produto)



            # envia email em caso de reestoque
            check_aviso_estoque(id_produto, estoque_atual)


            # Tenta atualizar a MateriaPrima
            try:
                materia_prima = MateriaPrima.objects.get(id=id_produto)
                print(materia_prima.stock)
                materia_prima.stock = estoque_atual
                print(materia_prima.stock)
                materia_prima.save()
            except MateriaPrima.DoesNotExist:
                # Tenta atualizar o Produto se a MateriaPrima não for encontrada
                try:

                    produto = Produto.objects.get(id=id_produto)
                    produto.stock = estoque_atual
                    produto.save()


                except Produto.DoesNotExist:
                    return HttpResponse(status=200)

            # Retorna uma resposta de sucesso
            return HttpResponse(status=200)

            # Retorna uma resposta de sucesso
            return HttpResponse(status=200)

        except Exception as e:
            # Trata o erro aqui e retorna uma resposta HTTP com o status 400 e uma mensagem de erro apropriada
            return HttpResponseBadRequest("Erro ao processar evento de atualização de estoque: {}".format(str(e)))

    else:
        return HttpResponseBadRequest("Tipo de evento desconhecido")