from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

from enviadores.email import enviar_email_rastreio
from pedidos.models import Pedido
from produtos.models import Produto, Subcategory
from produtos.models import Category, Subcategory, Variation,MateriaPrima


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


    # Processa o evento de código de rastreio
    "AQUIIIIIII"
    if payload['tipo'] == 'rastreio':
        print(payload)
        dados = payload['dados']
        codigo = dados['codigoRastreio']
        pedido_id = dados['idPedidoEcommerce']
        print(codigo)
        # Aqui você pode obter mais informações sobre o envio
        # ...

        # Crie uma resposta HTTP com o status de sucesso
        response_data = {
            'success': True
        }

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.rastreamento = codigo
            pedido.status = 'Enviado'
            pedido.save()
        except:
            return HttpResponse(json.dumps({'error': 'Erro ao rastreio no pedido salvar pedido'}), status=400,
                                content_type="application/json")

        try:
            destinatario = pedido.user.email
            nome= pedido.user.username
            rastreio = pedido.rastreamento
            enviar_email_rastreio(destinatario, nome, pedido_id, rastreio)
        except:
            print("erro ao enviar email")


        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
    else:
        return HttpResponse(json.dumps({'error': 'Falha ao decodificar JSON'}), status=400,
                            content_type="application/json")