from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from avise.views import aviso_estoque, mudar_aviso

# from avise.views import
app_name = 'avise'

urlpatterns = [

    path('aviso_estoque/', aviso_estoque, name='aviso_estoque'),
    path('mudar_aviso/', mudar_aviso, name='mudar_aviso'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



