# Generated by Django 3.1.12 on 2023-02-24 19:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0003_auto_20230224_1612'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('produtos', '0001_initial'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.produto')),
                ('variation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='produtos.variation')),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Aguardando pagamento', 'Aguardando pagamento'), ('Em processamento', 'Em processamento'), ('Em trânsito', 'Em trânsito'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Aguardando pagamento', max_length=20)),
                ('data_pedido', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('frete', models.CharField(choices=[('Sedex', 'Sedex'), ('PAC', 'PAC')], default='Frete nao selecionado', max_length=20)),
                ('valor_frete', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metodo_de_pagamento', models.CharField(choices=[('Cartao', 'Cartao'), ('Pix', 'Pix'), ('Deposito', 'Deposito'), ('Pagseguro', 'Pagseguro')], default='Nao selecionado', max_length=20)),
                ('comprovante', models.FileField(blank=True, null=True, upload_to='comprovantes')),
                ('endereco_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.enderecoentrega')),
                ('itens', models.ManyToManyField(blank=True, default=1, to='pedidos.PedidoItem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-data_pedido',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('order_number', models.CharField(max_length=32, null=True)),
                ('date_ordered', models.DateTimeField(auto_now_add=True)),
                ('tracking_number', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.cart')),
                ('shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_address', to='clientes.enderecoentrega')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
