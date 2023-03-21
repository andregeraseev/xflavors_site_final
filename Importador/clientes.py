# views.py
import random
import string
from django.core.validators import validate_integer, ValidationError
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.edit import FormView
from .forms import ImportClientesForm
import csv
from clientes.models import Cliente, EnderecoEntrega
from django.contrib.auth.models import User
import requests
import time

class ImportClientesView(FormView):
    template_name = 'importacao/importar_clientes.html'
    form_class = ImportClientesForm
    success_url = 'http://127.0.0.1:8000/'



    def form_valid(self, form):
        file = form.cleaned_data['file']
        file_text = file.read().decode('utf-8')  # Abre o arquivo em modo texto
        reader = csv.reader(file_text.splitlines(), delimiter=',')
        next(reader)  # skip header row

        for row in reader:
            username = row[0]
            print("USERNAME",username)

            email = row[1]
            password = row[2]
            cpf = row[3]
            print("CPF", cpf)
            cep = row[4]

            try:
                validate_integer(cep)
            except ValidationError:
                messages.error(self.request, f"CEP inválido: {cep}")
                continue


            # endereco_info = obter_endereco_por_cep(cep)
            # if endereco_info is None:
            #     messages.error(self.request, f"Erro ao obter endereço para o CEP {cep}")
            #     continue




            # endereco, bairro, cidade, estado = endereco_info

            print("CEP",cep)
            # obter_endereco_por_cep(cep)
            numero = row[6]
            print("numero",numero)
            complemento = row[7]
            print("complemento",complemento)

            endereco = None
            bairro = None
            cidade = None
            estado = None


            if endereco == None:
                endereco = row[5]
            if bairro == None:
                bairro = row[8]
            if cidade == None:
                cidade = row[9]
            if estado == None:
                estado = row[10]
            celular = row[11]
            # print("endereco", endereco)
            # print("bairro", bairro)
            # print("cidade", cidade)
            # print("estado", estado)

            try:

                user = User.objects.get(username=username)
                print('username cadastrado')

                # Verifica se o email pertence ao usuário com o username igual
                if user.email != email:
                    print('Verificando se o email pertence ao usuário com o username igual')
                    # Adiciona uma letra aleatória ao final do username até encontrar um username único
                    while User.objects.filter(username=username).exists():
                        username += random.choice(string.ascii_lowercase)
                        print('modificando username para', username)
                    # Cria um novo usuário com as informações do CSV
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    print(user, 'Criado')

            except User.DoesNotExist:
                # Cria um novo usuário com as informações do CSV
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                print(user,'Criado')


            # Cria um novo objeto Cliente para o usuário
            cliente, created = Cliente.objects.update_or_create(user=user, cpf=cpf, celular=celular)

            endereco, created = EnderecoEntrega.objects.update_or_create(
                cliente=cliente,
                cep=cep,
                defaults={
                    'rua': endereco,
                    'numero': numero,
                    'bairro': bairro,
                    'cidade': cidade,
                    'estado': estado,
                    'complemento': complemento,
                }
            )


        return super().form_valid(form)

def obter_endereco_por_cep(cep):
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    # time.sleep(2)
    if response.status_code == 400:
        print(f"Erro ao obter endereço para o CEP {cep} aguardando 2 segundos para tentar novamente: {response.status_code}")
        # time.sleep(2)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            endereco = data['logradouro'] if 'logradouro' in data else None

            bairro = data['bairro'] if 'bairro' in data else None
            cidade = data['localidade'] if 'localidade' in data else None
            estado = data['uf'] if 'uf' in data else None
            return endereco, bairro, cidade, estado

        else:
            print(f"Erro ao obter endereço para o CEP {cep}: {response.status_code}")
            return None



    elif response.status_code == 200:
        data = response.json()


        endereco = data['logradouro']if 'logradouro' in data else None
        bairro = data['bairro'] if 'bairro' in data else None
        cidade = data['localidade'] if 'localidade' in data else None
        estado = data['uf'] if 'uf' in data else None



        return endereco, bairro, cidade, estado


    else:

        print(f"Erro ao obter endereço para o CEP {cep}: {response.status_code}")