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
    avisos = AvisoEstoque.objects.filter(produto=product, notificado=False)
    if avisos.exists():
        for aviso in avisos:
            if product.variation:
                if product.variation.materia_prima.stock < quantidade:
                    send_email_aviso_estoque(aviso)
                    aviso.notificado = True
                    aviso.save()
            else:
                if product.stock < quantidade:
                    send_email_aviso_estoque(aviso)
                    aviso.notificado = True
                    aviso.save()




def send_email_aviso_estoque(aviso):

    subject = 'Produto em estoque'
    message = f"Olá {aviso.cliente.username}, o produto {aviso.produto.name} está em estoque novamente!"
    from_email = 'seu-email@provedor.com'
    recipient_list = [aviso.cliente.email]
    send_mail(subject, message, from_email, recipient_list)