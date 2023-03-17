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
# def mercado_pago_webhook(request):
#     mp = mercadopago.SDK(os.getenv('MERCADOLIVRETOKEN'))
#     # Verifique se o request é válido
#     if not request.body:
#         return HttpResponse(status=400)
#
#     # Analise o JSON recebido
#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return HttpResponse(status=400)
#
#     # Verifique se existe um 'id' no JSON recebido
#     if 'id' not in data:
#         return HttpResponse(status=400)
#
#     # Obtenha o recurso da notificação usando a API do Mercado Pago
#     resource = mp.get(f"/v1/payments/{data['id']}")
#
#     # Verifique se a resposta contém um objeto 'response'
#     if 'response' not in resource:
#         return HttpResponse(status=400)
#
#     # Obtenha o 'status' e o 'order_id' da resposta
#     payment_status = resource['response']['status']
#     order_id = resource['response']['order']['id']
#
#     # Atualize o status do Pedido com base no status do pagamento
#     if payment_status == 'approved':
#         try:
#             pedido = Pedido.objects.get(mercado_pago_id=order_id)
#             pedido.status = 'Pago'
#             pedido.save()
#         except Pedido.DoesNotExist:
#             return HttpResponse(status=404)
#
#     # Retorne uma resposta com status 200 para confirmar o recebimento da notificação
#     return HttpResponse(status=200)
@csrf_exempt
@require_POST
def mercado_pago_webhook(request):
    print("WEBHOOKING MERCADO PAGO")
    mp = mercadopago.SDK(os.getenv('MERCADOLIVRETOKEN'))
    if not request.body:
        print(1)
        return JsonResponse({'error': 'Request body is empty.'}, status=400)

    try:
        print(2)
        data = json.loads(request.body)
        print(data)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

    if 'data' not in data or 'id' not in data['data']:
        print(3)
        return JsonResponse({'error': 'Missing data or id in the request.'}, status=400)

    if 'type' not in data:
        print(4)
        return JsonResponse({'error': 'Missing type in the request.'}, status=400)

    if data['type'] != 'payment':
        print(5)
        return JsonResponse({'error': 'Invalid type. Only "payment" type is supported.'}, status=400)

    resource = mp.get(f"/v1/payments/{data['data']['id']}")

    if 'response' not in resource:
        print(6)
        return JsonResponse({'error': 'Missing response object in the API response.'}, status=400)

    payment_status = resource['response']['status']

    order_id = resource['response']['order']['id']

    if payment_status == 'approved':
        try:
            pedido = Pedido.objects.get(mercado_pago_id=order_id)
            pedido.status = 'Pago'
            pedido.save()
        except Pedido.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)

    return JsonResponse({'success': 'Notification received and processed.'}, status=200)