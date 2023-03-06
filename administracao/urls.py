from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include

from administracao.views import dashboard_adm,atualizar_status


app_name = 'administracao'

urlpatterns = [
path('dashboard_adm', dashboard_adm, name='dashboard_adm'),
path('atualizar_status', atualizar_status, name='atualizar_status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



