# Generated by Django 4.1.6 on 2023-02-19 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0005_pedido_metodo_de_pagamento_pedido_subtotal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='metodo_de_pagamento',
            field=models.CharField(choices=[('Cartao', 'Cartao'), ('Pix', 'Pix'), ('Deposito', 'Deposito'), ('Pagseguro', 'Pagseguro')], default='Nao selecionado', max_length=20),
        ),
    ]
