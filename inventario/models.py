from django.db import models
from usuarios.models import Usuario

# Create your models here.
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=256)
    stock_actual = models.IntegerField(default=0)

class Movimiento_stock(models.Model):
    tipo = models.CharField(max_length=10)
    fecha = models.DateField(auto_now_add=True)
    cantidad = models.IntegerField()
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_stock_realizados')
    """ Campos manejados con Snapshot """
    nombre_usuario = models.CharField(max_length=150)
    rol_usuario = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)