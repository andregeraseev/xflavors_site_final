# SeuProjeto/views.py
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import mercadopago
import json

from pedidos.models import Pedido


@csrf_exempt
@require_POST
def mercado_pago_webhook(request):
    mp = mercadopago.SDK(os.getenv('MERCADOLIVRETOKEN'))
    # Verifique se o request é válido
    if not request.body:
        return HttpResponse(status=400)

    # Analise o JSON recebido
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # Verifique se existe um 'id' no JSON recebido
    if 'id' not in data:
        return HttpResponse(status=400)

    # Obtenha o recurso da notificação usando a API do Mercado Pago
    resource = mp.get(f"/v1/payments/{data['id']}")

    # Verifique se a resposta contém um objeto 'response'
    if 'response' not in resource:
        return HttpResponse(status=400)

    # Obtenha o 'status' e o 'order_id' da resposta
    payment_status = resource['response']['status']
    order_id = resource['response']['order']['id']

    # Atualize o status do Pedido com base no status do pagamento
    if payment_status == 'approved':
        try:
            pedido = Pedido.objects.get(mercado_pago_id=order_id)
            pedido.status = 'Pago'
            pedido.save()
        except Pedido.DoesNotExist:
            return HttpResponse(status=404)

    # Retorne uma resposta com status 200 para confirmar o recebimento da notificação
    return HttpResponse(status=200)
