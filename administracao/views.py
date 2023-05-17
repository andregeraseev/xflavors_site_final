# administracao/views.py
from django.db.models.functions import Trunc, TruncDay
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



from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.contrib import messages
from .forms import EmailEmMassaForm
from clientes.models import Cliente

@staff_member_required
def enviar_email_em_massa_view(request):
    if request.method == 'POST':
        form = EmailEmMassaForm(request.POST)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            corpo = form.cleaned_data['corpo']
            clientes = Cliente.objects.filter(propaganda=True, cpf=36944557878)

            for cliente in clientes:
                # Carregar o template de email
                corpo_html = render_to_string('emails/email_em_massa.html', {
                    'nome': cliente.user.username,
                    'assunto': assunto,
                    'corpo': corpo
                })

                email = EmailMultiAlternatives(
                    subject=assunto,
                    body=corpo_html,  # Usar o template HTML como corpo do email
                    from_email='xflavors@gmail.com',
                    to=[cliente.user.email]
                )
                email.attach_alternative(corpo_html, "text/html")
                email.send()

            messages.success(request, f'Email enviado com sucesso para {len(clientes)} clientes.')
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
