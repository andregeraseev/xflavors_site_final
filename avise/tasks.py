# tasks.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xflavors.settings') # Substitua 'myproject.settings' pelo caminho correto para o seu arquivo de configurações
# django.setup()
from avise.models import AvisoEstoque
from avise.views import check_aviso_estoque


def check_aviso_estoque_task():
    print("Taks aviso disparada")
    avisos = AvisoEstoque.objects.filter(notificado=False)

    quantidade = 0
    for aviso in avisos:
        print("aviso")
        check_aviso_estoque(aviso, quantidade)

if __name__ == '__main__':
    check_aviso_estoque_task()