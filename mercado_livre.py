from django.shortcuts import render
import requests
import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect



def cria_preferencia(request, pedido):
    sdk = mercadopago.SDK("TEST-8706125782635153-030613-57f1bae5989eaa33fd181cdbba332e14-609318871")
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
            "success": "http://localhost:8000/success",
            "failure": "http://localhost:8000/failure",
            "pending": "http://localhost:8000/pending"
        },
        'redirect_urls': {
            "success": "http://localhost:8000/success",
            "failure": "http://localhost:8000/failure",
            "pending": "http://localhost:8000/pending"
        },
        "external_reference": id_pedido,
        "auto_return" : "approved"


    }


    preference_response = sdk.preference().create(preference_data)
    print(preference_response)
    preference = preference_response["response"]

    return preference['init_point']
    # Redirecione o usuário para a página de pagamento do Mercado Pago

