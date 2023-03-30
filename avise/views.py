from django.core.mail import send_mail
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from clientes.models import Cliente
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
        print("user", user)
        produto = get_object_or_404(Produto, pk=produto_id)

        aviso = AvisoEstoque.objects.create(
            produto=produto,
            cliente=user,

        )

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})


def check_aviso_estoque(product, quantidade):
    print("ativando aviso")
    avisos = AvisoEstoque.objects.filter(produto=product, notificado=False)
    print(product)
    print(avisos,"AVISO")
    if avisos.exists():
        print("existe avisos")
        for aviso in avisos:
            print("aviso")
            if product.variation:
                print("product.variation")
                if product.variation.materia_prima.stock < quantidade:
                    send_email_aviso_estoque(aviso)
                    aviso.notificado = True
                    aviso.save()
            else:
                print("product")
                if product.stock < quantidade:
                    send_email_aviso_estoque(aviso)
                    aviso.notificado = True
                    aviso.save()




def send_email_aviso_estoque(aviso):
    print("ENVIANDO EMAIL", aviso)

    subject = 'Produto em estoque'
    message = f"Olá {aviso.cliente.username}, o produto {aviso.produto.name} está em estoque novamente!"
    print("Nome", aviso.cliente.username)
    print("PRODUTO", aviso.produto.name)
    from_email = 'xflavors@gmail.com'
    recipient_list = [aviso.cliente.email]
    send_mail(subject, message, from_email, recipient_list)