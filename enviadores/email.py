from django.core.mail import send_mail

def enviar_email_confirmacao(destinatario, nome):
    assunto = 'Confirmação de Cadastro'
    mensagem = f'Olá {nome}, \n\nObrigado por se cadastrar no nosso site. Seu cadastro foi confirmado com sucesso!'
    remetente = 'xflavors@gmail.com'
    send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)


def enviar_email_pedido_criado(destinatario, nome, pedido_id):
    assunto = 'Pedido Criado'
    mensagem = f'Olá {nome}, \n\nSeu pedido #{pedido_id} foi criado com sucesso.'
    remetente = 'xflavors@gmail.com'
    send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)
