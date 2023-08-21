from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from xflavors.settings import BASE_DIR
import os
@staff_member_required
def view_logs(request):
    log = os.path.join(BASE_DIR, 'logs/clients.log')
    print(log)
    with open(log) as file:
        logs = file.read()

    return HttpResponse("<pre>" + logs + "</pre>")