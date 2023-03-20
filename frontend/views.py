from django.shortcuts import render

def termos(request):
    return render(request, 'rodape/termos.html')

def envio(request):
    return render(request, 'rodape/envio.html')
