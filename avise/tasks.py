# tasks.py

from avise.models import AvisoEstoque
from avise.views import check_aviso_estoque


def check_aviso_estoque_task():
    avisos = AvisoEstoque.objects.filter(notificado=False)
    quantidade = 0
    for aviso in avisos:
        check_aviso_estoque(aviso, quantidade)

if __name__ == '__check_aviso_estoque_task__':
    check_aviso_estoque_task()