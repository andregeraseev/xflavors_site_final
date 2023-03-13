# Generated by Django 4.1.7 on 2023-02-27 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0005_produto_marca'),
    ]

    operations = [
        migrations.CreateModel(
            name='MateriaPrima',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('stock', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='variation',
            name='materia_prima',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='produtos.materiaprima'),
        ),
    ]
