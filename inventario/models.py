from django.db import models
from usuarios.models import Usuario
# Create your models here.
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=256)
    stock_actual = models.IntegerField()

class Movimiento_stock(models.Model):
    tipo = models.CharField(max_length=10)
    fecha = models.DateField(auto_now_add=True)
    cantidad = models.IntegerField()
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='movimientos_stock_realizados')