import os

from django.shortcuts import render
import requests
import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect



def cria_preferencia(request, pedido):
    sdk = mercadopago.SDK(os.getenv('MERCADOLIVRETOKEN'))
    frete = int(pedido.valor_frete)
    id_pedido = pedido.id
    itens = []
    for item in pedido.itens.all():
        if item.variation:
            nome_item = item.variation.name
        else:
            nome_item = item.product.name

        item_price = float(item.price)

        itens.append( {

            "title": nome_item,
            "quantity": item.quantity,
            "unit_price": item_price,

        })

    print(itens, 'ITENSSSS')

    preference_data = {
        "items": itens,
        "shipments": {
                "cost": frete,
                "mode": "not_specified",
            },

        "back_urls": {
            "success": "https://xflavors.pythonanywhere.com//success",
            "failure": "https://xflavors.pythonanywhere.com//failure",
            "pending": "https://xflavors.pythonanywhere.com//pending"
        },
        'redirect_urls': {
            "success": "https://xflavors.pythonanywhere.com//success",
            "failure": "https://xflavors.pythonanywhere.com//failure",
            "pending": "https://xflavors.pythonanywhere.com//pending"
        },
        "external_reference": id_pedido,
        "auto_return" : "approved"


    }


    preference_response = sdk.preference().create(preference_data)
    print(preference_response)
    preference = preference_response["response"]

    return preference['init_point']
    # Redirecione o usuário para a página de pagamento do Mercado Pago

