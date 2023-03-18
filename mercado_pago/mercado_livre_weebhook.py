# SeuProjeto/views.py
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import mercadopago
import json

from pedidos.models import Pedido


# @csrf_exempt
# @require_POST
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
    sdk  = mercadopago.SDK(os.getenv('MERCADOLIVRETOKEN'))


    if not request.body:
        return JsonResponse({'error': 'Request body is empty.'}, status=400)

    try:
        data = json.loads(request.body)
        print("DATA",data)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

    if 'type' not in data or 'data' not in data or 'id' not in data['data']:
        return JsonResponse({'error': 'Missing required fields.'}, status=400)

    resource_type = data['type']
    print('resource_type', resource_type)
    resource_id = data['data']['id']
    print('resource_id',resource_id)
    if resource_type == 'payment':
        try:
            result = sdk.payment().get(resource_id)
            print('result', result)
            order_id = result['response']['order']['external_reference']
            print("ORDER_ID", order_id)
        except Exception as e:
            print(f"Erro ao buscar o pagamento: {e}")
            return JsonResponse({'error': 'Erro ao buscar o pagamento'}, status=500)




    elif resource_type == 'plan':
        plan = sdk.plan().get(resource_id)
        print('plan',plan)
    elif resource_type == 'subscription':
        subscription = sdk.subscription().get(resource_id)

    elif resource_type == 'point_integration_wh':
        # data contains the information related to the notification
        pass
    else:
        return JsonResponse({'error': 'Invalid resource type.'}, status=400)

    return JsonResponse({'success': 'Notification received and processed.'}, status=200)