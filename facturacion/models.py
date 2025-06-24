from django.db import models

class Factura(models.Model):
    idfactura = models.CharField(primary_key=True, max_length=30)
    fecha_emision = models.DateField()
    monto_total = models.DecimalField(max_digits=19, decimal_places=0)
    metodo_pago = models.CharField(max_length=20)
    estado = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Factura {self.idfactura} - {self.monto_total} {self.estado}"

class DetalleFactura(models.Model):
    idDetalleFactura = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # cambio aquí
    cantidad = models.IntegerField()
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="detalles")  # cambio aquí


    def __str__(self):
        return f"{self.descripcion} x{self.cantidad} - {self.facturaidfactura_id}"
