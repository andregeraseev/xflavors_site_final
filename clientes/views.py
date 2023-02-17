from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

from cart.models import Cart
from .models import Cliente, EnderecoEntrega
from django.contrib.auth.models import User
from produtos.models import Produto




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'error': 'Usuário ou senha inválidos!'}
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')





def cadastro(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        cellphone = request.POST['cellphone']
        cpf = request.POST['cpf']
        password = request.POST['password']
        cep = request.POST['cep']
        street = request.POST['street']
        number = request.POST['number']
        city = request.POST['city']
        neighborhood = request.POST['neighborhood']
        state = request.POST['state']
        complement = request.POST['complement']

        user = User.objects.create_user(username=full_name, email=email, password=password)

        client = Cliente.objects.create(user=user, celular=cellphone, cpf=cpf)
        address = EnderecoEntrega.objects.create(cliente=client, cep=cep, rua=street, numero=number, cidade=city, bairro=neighborhood, estado=state, complemento=complement)

        client.address = address
        client.save()

        return redirect('cadastro')

    return render(request, 'cadastro.html')

    return redirect('cadastro')

    return render(request, 'cadastro.html')

