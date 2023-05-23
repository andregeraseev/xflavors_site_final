from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include

from administracao.views import dashboard_adm, atualizar_status, adicionar_rastreamento, producao, enviar_tiny, \
    pedido_detail, imprimir_selecionados, adicionar_observacao, enviar_email_em_massa_view, dashboard_financeiro

app_name = 'administracao'

urlpatterns = [
path('dashboard_adm', dashboard_adm, name='dashboard_adm'),
path('atualizar_status', atualizar_status, name='atualizar_status'),
path('adicionar-rastreamento/', adicionar_rastreamento, name='adicionar_rastreamento'),
path('producao/', producao, name='producao'),
path('adicionar_observacao/', adicionar_observacao, name='adicionar_observacao'),
path('enviar_tiny/', enviar_tiny, name='enviar_tiny'),
path('pedido_detail/<int:pedido_id>', pedido_detail, name='pedido_detail'),
path('imprimir_selecionados/', imprimir_selecionados, name='imprimir_selecionados'),
path('dashboard_financeiro/', dashboard_financeiro, name='dashboard_financeiro'),

# email
path('enviar_email_em_massa/', enviar_email_em_massa_view, name='enviar_email_em_massa'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



