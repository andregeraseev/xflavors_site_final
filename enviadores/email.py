from django.core.mail import send_mail

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def enviar_email_confirmacao(destinatario, nome):
    assunto = 'Confirmação de Cadastro'
    # mensagem = f'Olá {nome}, \n\nObrigado por se cadastrar no nosso site. Seu cadastro foi confirmado com sucesso!'
    remetente = 'xflavors@gmail.com'

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/Bem_vindo.html', {'nome': nome})
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()

    # send_mail(assunto, html_content, remetente, [destinatario], fail_silently=False)


def enviar_email_pedido_criado(destinatario, nome, pedido_id):
    print('enviado email')
    assunto = 'Pedido Criado'
    mensagem = f'Olá {nome}, \n\nSeu pedido #{pedido_id} foi criado com sucesso.'
    remetente = 'xflavors@gmail.com'
    # send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/pedido.html', {'nome': nome,'pedido_id':pedido_id })
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()

def enviar_email_rastreio(destinatario, nome, pedido_id, rastreio):
    print('enviado email rastreio')
    assunto = 'Pedido Criado'
    mensagem = f'Olá {nome}, \n\nSeu pedido #{pedido_id} foi criado com sucesso.'
    remetente = 'xflavors@gmail.com'
    # send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/pedido.html', {'nome': nome,'pedido_id':pedido_id, "rastreio": rastreio })
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()



# # Define os dados para enviar o e-mail
# subject = 'Assunto do e-mail'
# from_email = 'email@exemplo.com'
# to_email = ['destinatario1@exemplo.com', 'destinatario2@exemplo.com']
#
# # Define o conteúdo do e-mail em HTML e texto puro
# html_content = render_to_string('seu_template.html', {'variavel': 'valor'})
# text_content = strip_tags(html_content)
#
# # Cria a mensagem
# msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
# msg.attach_alternative(html_content, "text/html")
#
# # Envia o e-mail
# msg.send()