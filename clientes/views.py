from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.utils import timezone
from cart.models import Cart
from enviadores.email import enviar_email_confirmacao

from pedidos.models import Pedido
from .models import Cliente, EnderecoEntrega
from django.contrib.auth.models import User
from produtos.models import Produto




def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        # Procura um usuário com o email informado
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        # Autentica o usuário com o email e a senha informados
        if user is not None:
            user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)

            # Atualiza last_login do Cliente
            cliente = Cliente.objects.get(user=request.user)
            cliente.last_login = timezone.now()
            cliente.save()

            return redirect('home')
        else:
            context = {'error': 'Email ou senha inválidos!'}
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def verificar_cpf(request):
    # print("VERIFICANDO CPF")
    if request.method == 'POST':
        cpf = request.POST['cpf']
        existe = Cliente.objects.filter(cpf=cpf).exists()
        # print("CPF JA CADASTRADO")
        return JsonResponse({'existe': existe})
    else:
        return JsonResponse({'erro': 'Requisição inválida'})

from django.core.mail import send_mail

def verificar_email(request):
    print('aqui')
    if request.method == 'POST':
        print('eaqui')

        email = request.POST.get('email', None)
        print(email)
        if email:
            if User.objects.filter(email=email).exists():

                return JsonResponse({'success':True, 'existe': True})
            else:

                return JsonResponse({'success':True,'existe': False})
    return JsonResponse({'existe': False})


@csrf_exempt
def verificar_nome(request):

    if request.method == 'POST':
        name = request.POST.get('name')

        if User.objects.filter(username=name).exists():
            return JsonResponse({'existe': True})
        else:
            return JsonResponse({'existe': False})
    else:
        return JsonResponse({'error': 'Método não permitido'})

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

        # Verifica se já existe um usuário com o e-mail fornecido
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')

            return redirect('cadastro')

        user = User.objects.create_user(username=full_name, email=email, password=password)

        client = Cliente.objects.create(user=user, celular=cellphone, cpf=cpf)
        address = EnderecoEntrega.objects.create(cliente=client, cep=cep, rua=street, numero=number, cidade=city, bairro=neighborhood, estado=state, complemento=complement)

        client.address = address
        user.save()
        client.save()


        # Autentica o usuário recém-criado

        print(user)
        # envia um email de confirmacao
        enviar_email_confirmacao(user.email, user.username)

        if user is not None:
            # Faz o login do usuário na sessão
            login(request, user)


        return redirect('home')

    return render(request, 'cadastro.html')

    return redirect('cadastro')

    return render(request, 'cadastro.html')

@login_required
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

def alterar_cpf(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        cliente = Cliente.objects.get(user=request.user)
        cliente.cpf = cpf
        cliente.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


def toggle_propaganda(request):
    if request.method == 'POST':
        cliente = request.user.cliente
        cliente.toggle_propaganda()
        return JsonResponse({'propaganda': cliente.propaganda})
    else:
        return JsonResponse({'error': 'Método de requisição inválido.'})


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





@login_required
@require_POST
def excluir_endereco_dashboard(request):
    endereco_id = request.POST.get('endereco_id')
    try:
        endereco = EnderecoEntrega.objects.get(id=endereco_id, cliente=request.user.cliente)
        endereco.delete()
        return JsonResponse({'success': True})
    except EnderecoEntrega.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Endereço não encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
