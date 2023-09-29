# administracao/views.py
from django.db.models.functions import Trunc, TruncDay, Concat
from django.shortcuts import render
from django.db.models import Sum
from django.template.loader import render_to_string
import numpy as np
from pedidos.models import Pedido
import pandas as pd
from datetime import datetime, timedelta
from tiny_erp.envia_pedido import enviar_pedido_para_tiny
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.models import User
from produtos.models import Produto, MateriaPrima, Variation, Subcategory
from smtplib import SMTPException
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.contrib import messages
from .forms import EmailEmMassaForm
from clientes.models import Cliente
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from xflavors.settings import EMAIL_HOST_USER

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
                    from_email= EMAIL_HOST_USER,
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

        try:
            enviar_pedido_para_tiny(pedido)
            return JsonResponse({'success': True, 'message': f'Status do pedido {pedido_id} alterado para Pago', "status": "OK",})

        except Exception as e:
            print('erro ao enviar',e)
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "Metodo não permetido"})


@staff_member_required
@csrf_exempt
def atualizar_status(request):

    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        novo_status = request.POST.get("novo_status")
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.atualizar_status(novo_status)

        if pedido.status=='Pago':
            try:
                # enviar_pedido_para_tiny(pedido)
                return JsonResponse({'success': True, 'message':f'Status do {pedido_id} foi alterado para {pedido.status} ', "status": "OK",})
            except Exception as e:
                return JsonResponse({'success': False, 'erro': str(e)})


    else:
        return JsonResponse({'success': False, 'erro': "Metodo não permetido"})


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

from django.db.models import ExpressionWrapper, F, DecimalField, CharField, Sum, When, Case
from django.db.models.functions import Round

@staff_member_required
def dashboard_financeiro(request):
    vendas_por_periodo = None
    vendas_detalhadas = []
    total_vendas = 0
    total_frete = 0
    total_subtotal = 0
    vendas_por_mes = []

    if request.method == 'POST':
        form = SelecionarPeriodoForm(request.POST)
        if form.is_valid():
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']
            category = form.cleaned_data['category']
            subcategory = form.cleaned_data['subcategory']  # nova linha

            vendas_por_periodo = Pedido.objects.filter(data_pedido__range=[data_inicial, data_final],
                                                       status__in=['Pago', 'Enviado', 'Em trânsito', 'Entregue'])
            if category:
                vendas_por_periodo = vendas_por_periodo.filter(itens__product__category=category, status__in=['Pago', 'Enviado', 'Em trânsito', 'Entregue'])
            if subcategory:  # nova linha
                vendas_por_periodo = vendas_por_periodo.filter(itens__product__subcategory=subcategory, status__in=['Pago', 'Enviado', 'Em trânsito', 'Entregue'])

            total_vendas = vendas_por_periodo.aggregate(total_vendas=Round(Sum('total'), 2))['total_vendas'] or 0
            total_frete = vendas_por_periodo.aggregate(total_frete=Round(Sum('valor_frete'), 2))['total_frete'] or 0

            itens_pedidos = PedidoItem.objects.filter(pedido__in=vendas_por_periodo)

            if category:
                itens_pedidos = itens_pedidos.filter(product__category=category)

            if subcategory:  # nova linha
                itens_pedidos = itens_pedidos.filter(product__subcategory=subcategory)  # nova linha

            vendas_detalhadas = itens_pedidos.values(
                'pedido__id',
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


# views.py

import plotly.express as px
import plotly.offline as opy
from django.shortcuts import render
from pedidos.models import Pedido
from django.db.models import Sum, F
from django.utils import timezone
import json

from datetime import datetime
@staff_member_required
def sales_chart(request):
    message = ''
    value_type = 'total'  # Default value
    order_statuses = ['Pago', 'Enviado', 'Em trânsito', 'Entregue']  # Default statuses
    start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')  # Default start date
    end_date = timezone.now().strftime('%Y-%m-%d')  # Default end date

    if request.method == 'POST':
        start_date = request.POST.get('start_date', start_date)
        end_date = request.POST.get('end_date', end_date)
        if datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(start_date, '%Y-%m-%d'):
            message = 'A data final não pode ser menor que a data inicial.'
            end_date = start_date
        value_type = request.POST.get('value_type', 'total')  # Get the selected value type, default is 'total'
        # Get the selected order statuses, default is ['Pago', 'Enviado', 'Em trânsito', 'Entregue']
        order_statuses = request.POST.getlist('order_status', ['Pago', 'Enviado', 'Em trânsito', 'Entregue'])

    sales_by_date = Pedido.objects.filter(data_pedido__date__range=[start_date, end_date], status__in=order_statuses)

    # Use the selected value type for the aggregation
    sales_by_date = sales_by_date.annotate(date=F('data_pedido__date')).values('date').annotate(
        total=Sum(value_type)).order_by('date')

    # Store values in session
    request.session['start_date'] = start_date
    request.session['end_date'] = end_date
    request.session['value_type'] = value_type
    request.session['order_statuses'] = order_statuses


    if sales_by_date:
        # Convert queryset to pandas DataFrame
        df = pd.DataFrame.from_records(sales_by_date)

        # Create date range
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())

        # Reindex DataFrame to include all dates in the range
        df.set_index('date', inplace=True)
        df = df.reindex(date_range, fill_value=0).reset_index()

        fig = px.line(df, x='index', y='total')
        fig.update_layout(
            title=f"{value_type.capitalize()} de {start_date} a {end_date} no status {', '.join(order_statuses)}",
            xaxis_title="Data",
            yaxis_title=f"{value_type.capitalize()}",
            font=dict(
                size=12,
            )
        )
        plot_div = opy.plot(fig, output_type='div', include_plotlyjs=False)
    else:
        plot_div = ''
        message = 'Não há vendas no período selecionado.'

    # Create a table with more detailed data
    qs = Pedido.objects.filter(data_pedido__date__range=[start_date, end_date], status__in=order_statuses)
    df_detailed = pd.DataFrame(list(qs.values()))

    # Create a table with more detailed data
    qs = Pedido.objects.filter(data_pedido__date__range=[start_date, end_date], status__in=order_statuses)
    df_detailed = pd.DataFrame(list(qs.values()))

    if not df_detailed.empty:
        # Drop unnecessary columns
        columns_to_drop = ['endereco_entrega_id', 'data_atualizacao', 'comprovante', 'numero_pedido_tiny',
                           'mercado_pago_id', 'rastreamento', 'producao', 'observacoes',
                           'observacoes_internas', 'link_mercado_pago']
        # Check if columns exist before dropping
        columns_to_drop = [col for col in columns_to_drop if col in df_detailed.columns]
        df_detailed = df_detailed.drop(columns=columns_to_drop)

        df_detailed['data_pedido'] = df_detailed['data_pedido'].dt.strftime('%d/%m/%Y')

        # Add a row with the sum of the desired columns
        df_sum = df_detailed[['desconto', 'subtotal', 'total', 'valor_frete']].sum().to_frame().T
        df_sum = df_sum.rename(index={df_sum.index[-1]: 'TOTAL'})
        # Append the sum row to the DataFrame
        df_detailed = df_detailed.append(df_sum)

        # Replace NaN values with '-' in the entire DataFrame
        df_detailed = df_detailed.fillna('-')

        table_div = df_detailed.to_html(classes='table table-striped table-hover')
    else:
        table_div = 'Não há dados para exibir.'

    return render(request, "administracao/sales_chart.html", context={'plot_div': plot_div, 'table_div': table_div, 'message': message})

@staff_member_required
def download_sales_data(request):
    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')
    value_type = request.session.get('value_type')
    order_statuses = request.session.get('order_statuses')

    qs = Pedido.objects.filter(data_pedido__date__range=[start_date, end_date], status__in=order_statuses)
    df = pd.DataFrame(list(qs.values()))

    # Drop unnecessary columns
    columns_to_drop = ['endereco_entrega_id', 'data_atualizacao', 'comprovante', 'numero_pedido_tiny',
                       'mercado_pago_id', 'rastreamento', 'producao', 'observacoes',
                       'observacoes_internas', 'link_mercado_pago']
    # Check if columns exist before dropping
    columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=columns_to_drop)

    # Convert 'data_pedido' column to the correct format
    # df['data_pedido'] = df['data_pedido'].dt.strftime('%d/%m/%Y')

    # # Add a row with the sum of the desired columns
    # df_sum = df[['desconto', 'subtotal', 'total', 'valor_frete']].sum().to_frame().T
    # df_sum = df_sum.rename(index={df_sum.index[-1]: 'TOTAL'})
    # # Append the sum row to the DataFrame
    # df = df.append(df_sum)
    #
    # # Replace NaN values with '-' in the entire DataFrame
    # df = df.fillna('-')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_data.csv"'

    return response

@staff_member_required
def pedidos_clientes(request, user_id):
    user = User.objects.get(id=user_id)
    pedidos = Pedido.objects.filter(user_id=user_id)
    total = 0
    desconto = 0
    for pedido in pedidos:
        total += pedido.total
        if pedido.desconto:
            desconto += pedido.desconto




    context = {'user': user, 'pedidos': pedidos, 'desconto':desconto,'total':total }
    return render(request, 'administracao/pedidos_clientes.html', context)


def reestoque(request):
    from django.db.models import Q

    # Use os valores padrão a menos que sejam fornecidos pelo usuário
    product_stock_value = request.GET.get('product_stock')
    variation_stock_value = request.GET.get('variation_stock')

    product_stock_limit = int(product_stock_value) if product_stock_value else 5
    variation_stock_limit = int(variation_stock_value) if variation_stock_value else 10

    # Produtos que têm variações cujas matérias-primas têm estoque <= variation_stock_limit ou produtos com estoque <= product_stock_limit
    produtos = Produto.objects.filter(
        Q(variation__materia_prima__stock__lte=variation_stock_limit) |
        (Q(variation__isnull=True) & Q(stock__lte=product_stock_limit))
    ).distinct()

    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()

    return render(request, 'administracao/reestoque.html',
                  {'produtos': produtos, 'categories': categories, 'subcategories': subcategories})