from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from avise.views import aviso_estoque

# from avise.views import
app_name = 'avise'

urlpatterns = [

    path('aviso_estoque/', aviso_estoque, name='aviso_estoque'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



