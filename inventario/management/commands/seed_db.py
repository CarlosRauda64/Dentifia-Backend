import random
from django.core.management.base import BaseCommand
from django.db import transaction
from inventario.models import Insumo, Movimiento_stock

class Command(BaseCommand):
    help = 'Limpia y puebla las tablas de Insumos y Movimientos de stock con datos de ejemplo.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Limpiando datos de Insumos y Movimientos de stock...'))
        Movimiento_stock.objects.all().delete()
        Insumo.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Tablas de inventario limpiadas.'))

        self.stdout.write('Creando nuevos datos de ejemplo...')

        # --- Crear Insumos de ejemplo ---
        insumos_data = [
            {'nombre': 'Guantes de Nitrilo', 'descripcion': 'Caja de 100 unidades, sin látex.'},
            {'nombre': 'Mascarillas Quirúrgicas', 'descripcion': 'Paquete de 50 mascarillas de 3 capas.'},
            {'nombre': 'Amalgama Dental', 'descripcion': 'Cápsulas de amalgama de plata, 50 unidades.'},
            {'nombre': 'Resina Compuesta', 'descripcion': 'Jeringa de 4g, color A2.'},
            {'nombre': 'Anestesia Local', 'descripcion': 'Cartuchos de lidocaína al 2% con epinefrina.'},
        ]
        
        insumos_creados = []
        for data in insumos_data:
            insumo = Insumo.objects.create(**data)
            insumos_creados.append(insumo)
            self.stdout.write(f'Creado Insumo: {insumo.nombre}')

        # --- Crear Movimientos de Stock de ejemplo ---
        for i in range(15): # Crear 15 movimientos aleatorios
            insumo_aleatorio = random.choice(insumos_creados)
            tipo_movimiento = random.choice(['entrada', 'salida'])
            cantidad = random.randint(5, 50)

            # Lógica para actualizar el stock inicial del insumo
            if tipo_movimiento == 'entrada':
                insumo_aleatorio.stock_actual += cantidad
                self.stdout.write(f'Entrada de {cantidad} para {insumo_aleatorio.nombre}. Nuevo stock: {insumo_aleatorio.stock_actual}')
            
            elif tipo_movimiento == 'salida':
                if insumo_aleatorio.stock_actual == 0:
                     # Si no hay stock, forzamos una entrada primero para este insumo
                    cantidad_entrada = random.randint(50, 100)
                    insumo_aleatorio.stock_actual += cantidad_entrada
                    insumo_aleatorio.save()
                    Movimiento_stock.objects.create(
                        tipo='entrada',
                        cantidad=cantidad_entrada,
                        insumo=insumo_aleatorio,
                        usuario=None,
                        nombre_usuario="Sistema (Inicial)",
                        rol_usuario="Seeder"
                    )
                    self.stdout.write(f'Stock inicializado para {insumo_aleatorio.nombre} con {cantidad_entrada} unidades.')

                # Ahora procesamos la salida
                if insumo_aleatorio.stock_actual >= cantidad:
                    insumo_aleatorio.stock_actual -= cantidad
                    self.stdout.write(f'Salida de {cantidad} de {insumo_aleatorio.nombre}. Nuevo stock: {insumo_aleatorio.stock_actual}')
                else:
                    # Si aún no hay suficiente, se omite la salida para no tener stock negativo
                    self.stdout.write(self.style.WARNING(f'Stock insuficiente para la salida de {cantidad} de {insumo_aleatorio.nombre}. Se omite movimiento.'))
                    continue
            
            insumo_aleatorio.save()

            # Crear el registro del movimiento
            Movimiento_stock.objects.create(
                tipo=tipo_movimiento,
                cantidad=cantidad,
                insumo=insumo_aleatorio,
                usuario=None, # El campo permite nulos, así que no asociamos usuario
                nombre_usuario="Sistema",
                rol_usuario="Seeder"
            )

        self.stdout.write(self.style.SUCCESS('¡Base de datos de inventario poblada con éxito!'))