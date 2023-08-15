from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
Brevo_Api = os.getenv('Brevo_Api')
@receiver(post_save, sender=User)
def create_brevo_contact(sender, instance=None, created=False, **kwargs):
    print("BREVO")
    if created:
        print("Detalhes do usuário recém-criado:")
        for field in instance._meta.fields:
            field_name = field.name
            field_value = getattr(instance, field_name)
            print(f"{field_name}: {field_value}")

        # Dividir o username em primeiro nome e sobrenome
        full_name = instance.username.split(' ', 1)  # Dividir no primeiro espaço
        first_name = full_name[0]
        last_name = full_name[1] if len(full_name) > 1 else ''  # Usar a segunda parte, se existir

        print(f"Primeiro nome: {first_name}")
        print(f"Sobrenome: {last_name}")

        # Configure a chave API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = Brevo_Api

        # Crie uma instância da classe de API
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))


        # Defina os detalhes do contato usando os detalhes do usuário
        create_contact = sib_api_v3_sdk.CreateContact(
          email=instance.email,
          attributes={"NOME": first_name, "SOBRENOME": last_name},
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