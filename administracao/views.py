# administracao/views.py
from django.db.models.functions import Trunc, TruncDay, Concat
from django.shortcuts import render
from django.db.models import Sum
from django.template.loader import render_to_string

from pedidos.models import Pedido
import pandas as pd
from datetime import datetime, timedelta
from tiny_erp.envia_pedido import enviar_pedido_para_tiny
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest


from smtplib import SMTPException
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.contrib import messages
from .forms import EmailEmMassaForm
from clientes.models import Cliente
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


@staff_member_required
def enviar_email_em_massa_view(request):
    if request.method == 'POST':
        form = EmailEmMassaForm(request.POST)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            corpo = form.cleaned_data['corpo']
            clientes_ids = form.cleaned_data['clientes']

            clientes = Cliente.objects.filter(id__in=clientes_ids)

            total_enviados = 0
            for cliente in clientes:
                # Carregar o template de email
                corpo_html = render_to_string('emails/email_em_massa.html', {
                    'nome': cliente.user.username,
                    'assunto': assunto,
                    'corpo': corpo
                })

                try:
                    # Valida o email antes de tentar enviar
                    validate_email(cliente.user.email)
                except ValidationError:
                    messages.error(request, f'Endereço de email inválido: {cliente.user.email}')
                    continue

                email = EmailMultiAlternatives(
                    subject=assunto,
                    body=corpo_html,  # Usar o template HTML como corpo do email
                    from_email='xflavors@gmail.com',
                    to=[cliente.user.email]
                )
                email.attach_alternative(corpo_html, "text/html")
                try:
                    email.send()
                    total_enviados += 1
                except SMTPException as e:
                    messages.error(request, f'Erro ao enviar email para {cliente.user.email}: {str(e)}')

            messages.success(request, f'Email enviado com sucesso para {total_enviados} clientes.')
        else:
            messages.error(request, 'Erro ao enviar o email. Verifique os dados informados.')
    else:
        form = EmailEmMassaForm()

    return render(request, 'administracao/enviar_email_em_massa.html', {'form': form})



@staff_member_required
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

@staff_member_required
def imprimir_selecionados(request):
    if request.method == 'POST':
        ids = json.loads(request.POST['pedidos_id'])
        ids = list(map(int, ids)) # converte os ids para inteiros
        pedidos = Pedido.objects.filter(id__in=ids) # utiliza id__in para filtrar pelos ids
        context = {'pedidos': []}
        for pedido in pedidos:
            itens = pedido.itens.all().order_by('product__localizacao', 'product__name')
            localizacoes = []
            for item in itens:
                if item.product.localizacao not in localizacoes:
                    localizacoes.append(item.product.localizacao)
            context['pedidos'].append({'pedido': pedido, 'itens': itens, 'localizacoes': localizacoes})
            # print(context)
        return render(request, 'administracao/imprimir_selecionados.html', context)
    else:
        return HttpResponseBadRequest('Método não permitido')


@staff_member_required
def pedido_detail(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    itens = pedido.itens.all().order_by('product__localizacao', 'product__name')

    localizacoes = []
    for item in itens:
        if item.product.localizacao not in localizacoes:
            localizacoes.append(item.product.localizacao)

    context = {'pedido': pedido, 'itens': itens, 'localizacoes':localizacoes}
    return render(request, 'administracao/pedido_detail.html', context)

@staff_member_required
def enviar_tiny(request):
    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        pedido = Pedido.objects.get(id=pedido_id)

        enviar_pedido_para_tiny(pedido)
        return HttpResponse("OK")
    else:
        return HttpResponse("Método não permitido")


@staff_member_required
@csrf_exempt
def atualizar_status(request):

    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        novo_status = request.POST.get("novo_status")
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.atualizar_status(novo_status)

        if pedido.status=='Pago':
            enviar_pedido_para_tiny(pedido)


        return HttpResponse("OK")
    else:
        return HttpResponse("Método não permitido")

@staff_member_required
def adicionar_rastreamento(request):
    # print('adicionando rastreio')
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        rastreamento = request.POST.get('rastreamento')
        # print(rastreamento)
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.rastreamento = rastreamento
            pedido.atualizar_status("Enviado")
            pedido.save()
            return JsonResponse({'status': 'success'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Pedido não encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Método inválido'})



@staff_member_required
def adicionar_observacao(request):
    # print('adicionando rastreio')
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        observacao = request.POST.get('observacao')
        # print(rastreamento)
        try:
            pedido = Pedido.objects.get(id=pedido_id)

            pedido.adicionar_observacao_interna(observacao)
            pedido.save()
            return JsonResponse({'status': 'success'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Pedido não encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Método inválido'})




@staff_member_required
def producao(request):
    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.mudar_producao()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})

import calendar
from django.utils import timezone
import datetime


from .forms import SelecionarPeriodoForm

from datetime import date, timedelta

from .forms import SelecionarPeriodoForm

from django.db.models import Sum
from django.shortcuts import render

from pedidos.models import Pedido
from produtos.models import Category
from .forms import SelecionarPeriodoForm

from django.db.models import Sum
from django.shortcuts import render

from pedidos.models import Pedido, PedidoItem
from produtos.models import Category
from .forms import SelecionarPeriodoForm

from django.db.models import Sum
from django.shortcuts import render

from pedidos.models import Pedido, PedidoItem
from produtos.models import Category
from .forms import SelecionarPeriodoForm
from django.db.models import F, ExpressionWrapper, DecimalField

# views.py
from django.db.models import Sum, F, Case, When, DecimalField
from django.shortcuts import render
from django.db.models import Value, CharField

from django.db.models import ExpressionWrapper, F, DecimalField, CharField, Sum, When, Case
from django.db.models.functions import Round

@staff_member_required
def dashboard_financeiro(request):
    vendas_por_periodo = None
    vendas_detalhadas = []
    total_vendas = 0
    total_frete = 0
    total_subtotal = 0

    if request.method == 'POST':
        form = SelecionarPeriodoForm(request.POST)
        if form.is_valid():
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']
            category = form.cleaned_data['category']

            vendas_por_periodo = Pedido.objects.filter(data_pedido__range=[data_inicial, data_final])

            if category:
                vendas_por_periodo = vendas_por_periodo.filter(itens__product__category=category)

            total_vendas = vendas_por_periodo.aggregate(total_vendas=Round(Sum('total'), 2))['total_vendas'] or 0
            total_frete = vendas_por_periodo.aggregate(total_frete=Round(Sum('valor_frete'), 2))['total_frete'] or 0

            itens_pedidos = PedidoItem.objects.filter(pedido__in=vendas_por_periodo)
            vendas_detalhadas = itens_pedidos.values(
                'pedido__data_pedido',
                'product__name',
                'variation__name',
                'quantity',
            ).annotate(
                subtotal=Case(
                    When(variation__price__gt=0, then=Round(F('variation__price') * F('quantity'), 2)),
                    default=Round(F('product__price') * F('quantity'), 2),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )

            total_subtotal = vendas_detalhadas.aggregate(total_subtotal=Round(Sum('subtotal'), 2))['total_subtotal'] or 0

        vendas_por_mes = Pedido.objects.filter(
            data_pedido__range=[data_inicial, data_final]
        ).annotate(
            data_periodo=ExpressionWrapper(
                F('data_pedido') + ' - ' + F('data_pedido'),
                output_field=CharField()
            )
        ).values(
            'data_periodo'
        ).annotate(
            total_vendas=Round(Sum('total'), 2),
            total_subtotal=Round(Sum('subtotal'), 2),
            total_frete=Round(Sum('valor_frete'), 2)
        )

    else:
        form = SelecionarPeriodoForm()


    context = {
        'form': form,
        'vendas_detalhadas': vendas_detalhadas,
        'total_vendas': total_vendas,
        'total_frete': total_frete,
        'total_subtotal': total_subtotal,
        'vendas_por_mes': vendas_por_mes
    }
    return render(request, 'administracao/dashboard_financeiro.html', context)









