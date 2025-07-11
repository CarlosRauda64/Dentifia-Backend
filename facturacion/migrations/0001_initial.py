# Generated by Django 5.2.1 on 2025-06-24 04:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('idfactura', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('fecha_emision', models.DateField()),
                ('monto_total', models.DecimalField(decimal_places=0, max_digits=19)),
                ('metodo_pago', models.CharField(max_length=20)),
                ('estado', models.CharField(max_length=30)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='DetalleFactura',
            fields=[
                ('idDetalleFactura', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=50)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad', models.IntegerField()),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='facturacion.factura')),
            ],
        ),
    ]
