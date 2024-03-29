from django.core.mail import send_mail
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from clientes.models import Cliente
from enviadores.email import send_email_aviso_estoque
from produtos.models import Produto
from .models import AvisoEstoque

@csrf_exempt
def aviso_estoque(request):
    print("AQUIIIII")
    if request.method == 'POST':
        print("e aqui1")
        produto_id = request.POST.get('product_id')
        print("produto_id", produto_id)
        user = request.user

        if user.is_anonymous:
            print("ANONIMO")
            return JsonResponse({'success': False, 'mensagem': 'Usuário precisa estar cadastrado e logado'})
        else:
            print("USUARIO AUTENTICADO")
            print("user", user)
            produto = get_object_or_404(Produto, pk=produto_id)

            aviso = AvisoEstoque.objects.create(
                produto=produto,
                cliente=user,

            )

            return JsonResponse({"success":True, 'status': 'ok', "aviso_adicionado":"Aviso cadastrado com sucesso"})
    return JsonResponse({'status': 'error'})


def check_aviso_estoque(aviso, quantidade):
    print("ativando aviso")

    produto = aviso.produto
    # produto = Produto.objects.filter(id=produto_id)
    print(produto)

    if produto:
        print("existe produtos")
        variation = produto.variation_set.first()
        if variation:
            print(variation)
            if variation.materia_prima.stock > quantidade:
                send_email_aviso_estoque(aviso)
                aviso.notificado = True
                aviso.save()

        else:
            print("AVISANDO product")
            if produto.stock > quantidade:
                send_email_aviso_estoque(aviso)
                aviso.notificado = True
                aviso.save()


def mudar_aviso(request):
    if request.method == 'POST':
        print("excluir aviso")
        aviso = request.POST.get('aviso_id')
        print(aviso)
        aviso = get_object_or_404(AvisoEstoque, id=aviso)
        aviso.notificado = True
        aviso.save()

        return JsonResponse({'success': True})
    return JsonResponse({'status': 'error'})

