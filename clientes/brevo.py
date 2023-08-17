from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from clientes.models import Cliente, EnderecoEntrega
import re
Brevo_Api = os.getenv('Brevo_Api')
# @receiver(post_save, sender=Cliente,)
def create_brevo_contact(client, address):
    print("BREVO")
    cliente = Cliente.objects.get(user__username=client)
    print("Detalhes do usuário recém-criado:")
    print("Cliente", client)
    print("Endereço:", address)


    # Dividir o username em primeiro nome e sobrenome
    full_name = cliente.user.username.split(' ', 1)  # Dividir no primeiro espaço
    first_name = full_name[0]
    last_name = full_name[1] if len(full_name) > 1 else ''  # Usar a segunda parte, se existir

    print(f"Primeiro nome: {first_name}")
    print(f"Sobrenome: {last_name}")




    cliente_id = cliente.id

    celular = cliente.celular
    try:
        celular_formatado = int(format_phone_number(celular))
    except:
        celular_formatado = None
    endereço = EnderecoEntrega.objects.get(cliente__id = cliente_id)
    print(endereço)
    CEP = endereço.cep
    CIDADE = endereço.cidade
    ESTADO = endereço.estado
    print("BREVO DADOS",
    celular,
    cliente,
    endereço,
    CEP,
    CIDADE,
    ESTADO)

    # Configure a chave API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = Brevo_Api

    # Crie uma instância da classe de API
    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))


    # Defina os detalhes do contato usando os detalhes do usuário
    create_contact = sib_api_v3_sdk.CreateContact(
      email=cliente.user.email,
      attributes={"NOME": first_name, "SOBRENOME": last_name ,"SMS":celular_formatado, "WHATSAPP":celular_formatado,"CEP":CEP,"CIDADE":CIDADE,"ESTADO":ESTADO },
      list_ids=[2], # ID(s) da lista a que o contato deve ser associado
      update_enabled=False
    )
    print(create_contact)

    try:
        # Crie o contato no Brevo
        api_instance.create_contact(create_contact)
    except ApiException as e:
        # Log ou trate o erro conforme necessário
        print("Exception when calling ContactsApi->create_contact: %s\n" % e)



def format_phone_number(phone_number):
    # Remova todos os caracteres não numéricos
    only_digits = re.sub(r'\D', '', phone_number)
    # Adicione o prefixo "+55" para o código do país do Brasil
    return '55' + only_digits



