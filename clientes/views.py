from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

from cart.models import Cart
from pedidos.models import Pedido
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


def dashboard(request):
    cliente = Cliente.objects.get(user=request.user)
    enderecos = EnderecoEntrega.objects.filter(cliente=cliente)
    pedidos = Pedido.objects.filter(user=request.user)
    context = {'cliente': cliente, 'enderecos': enderecos, 'pedidos':pedidos}
    return render(request, 'dashboard.html', context)


from django.shortcuts import render, redirect
from pedidos.forms import EnderecoEntregaForm

def adicionar_endereco_dashboard(request):
    if request.method == 'POST':
        cliente = Cliente.objects.get(user=request.user)
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')

        endereco = EnderecoEntrega.objects.create(
            cliente=cliente,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep
        )
        endereco.save()

        return redirect('dashboard')

    return render(request, 'adicionar_endereco_dashboard.html')


from django.http import JsonResponse

def alterar_celular(request):
    if request.method == 'POST':
        celular = request.POST.get('celular')
        cliente = Cliente.objects.get(user=request.user)
        cliente.celular = celular
        cliente.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})



def editar_endereco_dashboard(request):
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')

        try:
            endereco = EnderecoEntrega.objects.get(id=endereco_id)
            endereco.rua = rua
            endereco.numero = numero
            endereco.complemento = complemento
            endereco.bairro = bairro
            endereco.cidade = cidade
            endereco.estado = estado
            endereco.cep = cep
            endereco.save()
            # messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('dashboard')
        except EnderecoEntrega.DoesNotExist:
            # messages.error(request, 'Endereço não encontrado.')
            return redirect('dashboard')



    endereco_id = request.GET.get('endereco_id')
    endereco = get_object_or_404(EnderecoEntrega, pk=endereco_id, cliente=request.user.cliente)
    return render(request, 'editar_endereco_dashboard.html', {'endereco': endereco})