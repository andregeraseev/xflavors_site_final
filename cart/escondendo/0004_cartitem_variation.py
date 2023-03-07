# Generated by Django 4.1.6 on 2023-02-13 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0003_variation_produto_variations'),
        ('cart', '0003_cart_variations'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='produtos.variation'),
        ),
    ]