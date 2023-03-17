from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include

from administracao.views import dashboard_adm,atualizar_status,adicionar_rastreamento


app_name = 'administracao'

urlpatterns = [
path('dashboard_adm', dashboard_adm, name='dashboard_adm'),
path('atualizar_status', atualizar_status, name='atualizar_status'),
path('adicionar-rastreamento/', adicionar_rastreamento, name='adicionar_rastreamento'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



