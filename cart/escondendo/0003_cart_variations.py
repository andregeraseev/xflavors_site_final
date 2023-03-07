# Generated by Django 4.1.6 on 2023-02-13 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0003_variation_produto_variations'),
        ('cart', '0002_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='variations',
            field=models.ManyToManyField(blank=True, related_name='carts', to='produtos.variation'),
        ),
    ]