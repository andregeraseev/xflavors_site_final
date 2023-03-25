import requests
import json

import requests
import json

from xflavors.settings import TINY_ERP_API_KEY


def enviar_pedido_para_tiny(pedido):
    # Informações necessárias para criar o pedido no TinyERP

    empresa = 'xflavors'
    nome = pedido.user.username
    codigo_cliente = pedido.user.id
    telefone = pedido.user.cliente.celular
    email = pedido.user.email
    cpf = pedido.user.cliente.cpf
    total = float(pedido.total)
    id_pedido = pedido.id
    endereco = pedido.endereco_entrega.rua
    numero = pedido.endereco_entrega.numero
    complemento = pedido.endereco_entrega.complemento
    bairro = pedido.endereco_entrega.bairro
    cep =  pedido.endereco_entrega.cep
    cidade = pedido.endereco_entrega.cidade
    uf = pedido.endereco_entrega.estado
    forma_frete = "PAC CONTRATO AG (03298)" if pedido.frete == "PAC" else "SEDEX CONTRATO AG (03220)"
    observacao = pedido.observacoes
    if pedido.status == "Pago":
        status= "aprovado"
    else:
        status ="aberto"

    valor_frete= float(pedido.valor_frete)
    status_do_pedido= pedido.status




    # Monta a estrutura do pedido para enviar à API
    itens = []
    for item in pedido.itens.all():
        if item.variation:
            nome_item = item.variation.name
            id_item = item.variation.id
        else:
            nome_item = item.product.name
            id_item = item.id
        item_price = float(item.price)
        itens.append({"item":{
            "codigo": id_item,
            "id_produto": id_item,
            "descricao": nome_item,
            "quantidade": item.quantity,
            "valor_unitario": item_price,
            "unidade": "UN",
        }})

    pedido_data = {
  "pedido": {

    "cliente": {
      "codigo": codigo_cliente,
      "nome": nome,

      "tipo_pessoa": "F",
      "cpf_cnpj": cpf,

      "endereco": endereco,
      "numero": numero,
      "complemento": complemento,
      "bairro": bairro,
      "cep": cep,
      "cidade": cidade,
      "uf": uf,
      "fone": telefone,


    },
      "marcadores": [
          {
              "marcador": {
                  "descricao": "XFLAVORS"
              }
          },
      ],
    "endereco_entrega":{
        "nome_destinatario": nome,
        "cpf_cnpj": cpf,
        "endereco": endereco,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "uf": uf,
        "fone": telefone


    },

    "itens": itens,

      "valor_frete": valor_frete,
      "valor_desconto": "0",
      "numero_pedido_ecommerce": id_pedido,
      "situacao": status,
      "obs_internas": "XFLAVORS",
      "obs": observacao,
      "forma_envio": "c",
      "forma_frete": forma_frete,
      "id_ecommerce" : 11162,
  }
}

    # Envia o pedido para o TinyERP via API
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = TINY_ERP_API_KEY
    params = {
        'token': token,
        'formato': 'json',
        'pedido': json.dumps(pedido_data),
    }

    response = requests.post(url, params=params)

    try:
        json.dumps(pedido_data)
    except ValueError as e:
        print('Erro ao criar JSON do pedido:')
        print(str(e))
        return False
    print(params)
    # response = requests.post(url, json=pedido_data, headers=headers, params=params)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        status_processamento = response_data.get('retorno', {}).get('status_processamento')

        if status_processamento == '3':
            try:
                numero_pedido = response_data.get('retorno', {}).get('registros', {}).get('registro', {}).get('numero')
                pedido.numero_pedido_tiny = numero_pedido
                pedido.save()
                print(f'O número do pedido é {numero_pedido}')
                return True
            except:
                print("erro ao pegar o numero do pedido no tiny")
                return True
        else:
            print('Erro ao enviar pedido para o TinyERP')
            response_data = response.json()
            if response_data['retorno']['status'] == 'Erro':
                print(response_data['retorno']['registros'])
    return False

