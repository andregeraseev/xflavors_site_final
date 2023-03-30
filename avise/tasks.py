# tasks.py

from celery import shared_task
from produtos.models import Produto
from avise.models import AvisoEstoque
from avise.views import check_aviso_estoque

@shared_task
def check_aviso_estoque_task():
    avisos = AvisoEstoque.objects.filter(notificado=False)
    quantidade = 0
    for aviso in avisos:
        check_aviso_estoque(aviso, quantidade)