# Generated by Django 4.1.7 on 2023-03-04 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_alter_order_id_alter_pedido_id_alter_pedidoitem_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidoitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
        ),
    ]