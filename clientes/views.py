from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.utils import timezone
from clientes.brevo import create_brevo_contact
from avise.models import AvisoEstoque
from cart.models import Cart
from enviadores.email import enviar_email_confirmacao

from pedidos.models import Pedido
from .models import Cliente, EnderecoEntrega
from django.contrib.auth.models import User
from produtos.models import Produto, Favorito
import logging
logger = logging.getLogger('clientes')


def login_view(request):
    try:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            logger.info(f'Tentativa de login com email: {email}')

            # Procura um usuário com o email informado
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
                logger.warning(f'Usuário com email {email} não encontrado')

            # Autentica o usuário com o email e a senha informados
            if user is not None:
                user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f'Usuário {user.username} autenticado com sucesso')

                # Atualiza last_login do Cliente
                cliente = Cliente.objects.get(user=request.user)
                cliente.last_login = timezone.now()
                cliente.save()
                logger.info(f'Last login atualizado para o usuário {user.username}')

                return redirect('home')
            else:
                context = {'error': 'Email ou senha inválidos!'}
                logger.warning(f'Falha na autenticação para o email {email}')
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html')
    except Exception as e:
        logger.error(f'Erro inesperado na view de login: {str(e)}')
        raise


def logout_view(request):
    user = request.user
    logout(request)
    logger.info(f"Usuário {user} fez logout.")
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
    # print('verificando email')
    if request.method == 'POST':
        # print('Verificação email metodo POST')

        email = request.POST.get('email', None)
        # print(email)
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
        logger.info('Início do processo de cadastro cliente.')

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
        test = request.POST.get('test', False)

        # Verifica se já existe um usuário com o e-mail fornecido
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            logger.warning(f'Tentativa de registro com e-mail já existente: {email}')
            return redirect('cadastro')

        user = User.objects.create_user(username=full_name, email=email, password=password)
        logger.info(f'Usuário {user.username} criado com sucesso.')
        client = Cliente.objects.create(user=user, celular=cellphone, cpf=cpf)
        address = EnderecoEntrega.objects.create(cliente=client, cep=cep, rua=street, numero=number, cidade=city, bairro=neighborhood, estado=state, complemento=complement)

        client.address = address
        user.save()
        client.save()


        # Autentica o usuário recém-criado

        # print('Usuario Criado',user)
        # envia um email de confirmacao
        try:
            if test == False:
                enviar_email_confirmacao(user.email, user.username)
            else:
                logger.debug('Modo de teste ativado. E-mail de confirmação não enviado.')
        except:
            logger.error(f'Erro ao enviar e-mail de confirmação para o usuário {user.username}, e-mail: {user.email}')
        try:
            if test == False:
                create_brevo_contact(client, address)
            else:
                logger.debug('Modo de teste ativado. Contato Brevo não criado.')
        except:
            logger.error(f'Erro ao enviar informações para Brevo para o cliente {client.id}')
        if user is not None:
            # Faz o login do usuário na sessão
            login(request, user)
            logger.info(f'Usuário {user.username} autenticado com sucesso.')


        return redirect('home')

    return render(request, 'cadastro.html')

    # return redirect('cadastro')
    #
    # return render(request, 'cadastro.html')

@login_required
def dashboard(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
        enderecos = EnderecoEntrega.objects.filter(cliente=cliente)
        pedidos = Pedido.objects.filter(user=request.user)
        avisos = AvisoEstoque.objects.filter(cliente=request.user,notificado=False)

        favorito, created = Favorito.objects.get_or_create(cliente=cliente)
        produtos_favoritos = favorito.produto.all()
        logger.info(f'O usuário {request.user.username} acessou o dashboard de usuário.')

        context = {'cliente': cliente, 'enderecos': enderecos, 'pedidos':pedidos, "avisos":avisos, "produtos_favoritos" : produtos_favoritos}
        return render(request, 'dashboard.html', context)
    except Exception as e:
        # Log de qualquer exceção que possa ocorrer durante a recuperação de dados
        logger.error(f'Erro ao acessar o dashboard de usuário {request.user.username}: {str(e)}')
        return render(request, 'error.html', {
            'message': 'Ocorreu um erro ao acessar o dashboard de usuário. Por favor, tente novamente mais tarde.'})


from django.shortcuts import render, redirect
from pedidos.forms import EnderecoEntregaForm

def adicionar_endereco_dashboard(request):

    if request.method == 'POST':
        logger.info(f'O usuário {request.user.username} tentando adicionar novo endereço.')
        try:
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
            logger.info(f'O usuário {request.user.username} adicionou um novo endereço.')
            return redirect('dashboard')

        except Exception as e:
            # Logando qualquer exceção que possa ocorrer durante a adição do endereço
            logger.error(f'Erro ao adicionar o endereço para o usuário {request.user.username}: {str(e)}')
            return render(request, 'error.html', {
                'message': 'Ocorreu um erro ao adicionar o endereço. Por favor, tente novamente mais tarde.'})

    return render(request, 'adicionar_endereco_dashboard.html')


from django.http import JsonResponse

def alterar_celular(request):
    if request.method == 'POST':
        try:
            celular = request.POST.get('celular')
            cliente = Cliente.objects.get(user=request.user)
            cliente.celular = celular
            cliente.save()
            logger.info(f'O usuário {request.user.username} alterou o número de celular para {celular}.')
            return JsonResponse({'success': True})
        except Exception as e:
            # Logando qualquer exceção que possa ocorrer durante a alteração do número de celular
            logger.error(f'Erro ao alterar o número de celular para o usuário {request.user.username}: {str(e)}')
            return JsonResponse({'success': False,
                                 'error': 'Ocorreu um erro ao alterar o número de celular. Por favor, tente novamente mais tarde.'})
    else:
        return JsonResponse({'success': False})

def alterar_cpf(request):

    if request.method == 'POST':
        try:
            cpf = request.POST.get('cpf')
            cliente = Cliente.objects.get(user=request.user)
            cliente.cpf = cpf
            cliente.save()
            logger.info(f'usuário {request.user.username} alterou CPF com sucesso')

            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f'Erro ao alterar o número do cpf para o usuário {request.user.username}: {str(e)}')
            return JsonResponse({'success': False , 'error':'erro ao alterar o número do cpf'})
    else:
        return JsonResponse({'success': False})


def toggle_propaganda(request):
    if request.method == 'POST':
        try:
            cliente = request.user.cliente
            cliente.toggle_propaganda()
            logger.info(f'usuário {request.user.username} alterou propaganda para {cliente.propaganda}')

            return JsonResponse({'propaganda': cliente.propaganda})
        except Exception as e:
            logger.error(f'Erro alterar propaganda {request.user.username}: {str(e)}')

    else:
        logger.error(f'Erro alterar propaganda do usuario {request.user.username} Método de requisição inválido')
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
            logger.info(f'usuário {request.user.username} alterou endereco {endereco} com sucesso')

            # messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('dashboard')
        except EnderecoEntrega.DoesNotExist:
            logger.error(f'Erro alterar endereco de {request.user.username} endereco nao existe')

            # messages.error(request, 'Endereço não encontrado.')
            return redirect('dashboard')
    else:
        logger.error(f'Erro alterar endereco do usuario {request.user.username} Método de requisição inválido')
        return JsonResponse({'error': 'Método de requisição inválido.'})

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
