# Generated by Django 4.1.7 on 2023-02-27 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0004_remove_produto_variations_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='marca',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
