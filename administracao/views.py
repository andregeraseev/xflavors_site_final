# administracao/views.py
from django.db.models.functions import Trunc, TruncDay
from django.shortcuts import render
from django.db.models import Sum
from pedidos.models import Pedido
import pandas as pd
from datetime import datetime, timedelta
from tiny_erp.envia_pedido import enviar_pedido_para_tiny

def dashboard_adm(request):
    today = datetime.now().date()
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)

    try:
        start_date = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d").date()
        end_date = (start_date + timedelta(days=30)).replace(day=1) - timedelta(days=1)
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today



    pedidos = Pedido.objects.filter(data_pedido__year=year, data_pedido__month=month).annotate(
        data_pedido_annotate=TruncDay('data_pedido')
    ).values('data_pedido_annotate').annotate(total=Sum('total'))

    pedidos = Pedido.objects.filter()


    context = {

        'pedidos': pedidos,
        'year': int(year),
        'month': int(month)
    }
    return render(request, 'administracao/dashboard_adm.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


@csrf_exempt
def atualizar_status(request):
    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        novo_status = request.POST.get("novo_status")
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.atualizar_status(novo_status)

        enviar_pedido_para_tiny(pedido)
        return HttpResponse("OK")
    else:
        return HttpResponse("Método não permitido")

@csrf_exempt
def adicionar_rastreamento(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        rastreamento = request.POST.get('rastreamento')
        print(rastreamento)
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.rastreamento = rastreamento
            pedido.save()
            return JsonResponse({'status': 'success'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Pedido não encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Método inválido'})