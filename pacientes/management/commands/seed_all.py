import random
from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.db.utils import OperationalError

from usuarios.models import Usuario
from pacientes.models import Paciente
from citas.models import Cita, ESTADO_CHOICES
from facturacion.models import Factura, DetalleFactura
from inventario.models import Insumo, Movimiento_stock
from encuestas.models import Encuesta
from expediente.models import Expediente, FichaOrtodoncia, NotaProgresoOrto, Odontograma, OdontogramaVersion, OdontogramaDetalle


class Command(BaseCommand):
    help = 'Llena la base de datos con datos de ejemplo para todos los módulos y reportes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar todos los datos antes de crear nuevos',
        )

    def handle(self, *args, **options):
        # Limpiar datos fuera de la transacción atómica para evitar problemas
        if options['clear']:
            self.stdout.write(self.style.WARNING('Limpiando todos los datos...'))
            # Eliminar en orden inverso de dependencias, con manejo de errores si las tablas no existen
            
            modelos_a_limpiar = [
                ('OdontogramaDetalle', OdontogramaDetalle),
                ('OdontogramaVersion', OdontogramaVersion),
                ('Odontograma', Odontograma),
                ('NotaProgresoOrto', NotaProgresoOrto),
                ('FichaOrtodoncia', FichaOrtodoncia),
                ('Expediente', Expediente),
                ('DetalleFactura', DetalleFactura),
                ('Factura', Factura),
                ('Movimiento_stock', Movimiento_stock),
                ('Insumo', Insumo),
                ('Encuesta', Encuesta),
                ('Cita', Cita),
                ('Paciente', Paciente),
            ]
            
            for nombre, modelo in modelos_a_limpiar:
                try:
                    modelo.objects.all().delete()
                except OperationalError as e:
                    self.stdout.write(self.style.WARNING(f'  Tabla {nombre} no existe, se omite.'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Error al limpiar {nombre}: {e}'))
            
            # No eliminar usuarios para mantener el admin
            self.stdout.write(self.style.SUCCESS('Datos limpiados.'))

        # Crear datos dentro de una transacción atómica
        with transaction.atomic():
            self._crear_datos()

    def _crear_datos(self):

        self.stdout.write(self.style.SUCCESS('Iniciando seeder completo...'))

        # 1. Crear Usuarios (doctores, secretarias)
        self.stdout.write('\n=== Creando Usuarios ===')
        doctores = []
        secretarias = []
        
        # Crear doctores
        doctores_data = [
            {'usuario': 'dr.garcia', 'email': 'dr.garcia@dentifia.com', 'nombre': 'Carlos', 'apellido': 'García', 'rol': 'doctor'},
            {'usuario': 'dr.martinez', 'email': 'dr.martinez@dentifia.com', 'nombre': 'Ana', 'apellido': 'Martínez', 'rol': 'doctor'},
            {'usuario': 'dr.rodriguez', 'email': 'dr.rodriguez@dentifia.com', 'nombre': 'Luis', 'apellido': 'Rodríguez', 'rol': 'doctor'},
        ]
        
        for data in doctores_data:
            usuario, created = Usuario.objects.get_or_create(
                usuario=data['usuario'],
                defaults={
                    'email': data['email'],
                    'nombre': data['nombre'],
                    'apellido': data['apellido'],
                    'rol': data['rol'],
                }
            )
            if created:
                usuario.set_password('password123')
                usuario.save()
            doctores.append(usuario)
            self.stdout.write(f'  Doctor: {usuario.nombre} {usuario.apellido}')

        # Crear secretarias
        secretarias_data = [
            {'usuario': 'secretaria1', 'email': 'secretaria1@dentifia.com', 'nombre': 'María', 'apellido': 'López', 'rol': 'secretaria'},
            {'usuario': 'secretaria2', 'email': 'secretaria2@dentifia.com', 'nombre': 'Carmen', 'apellido': 'Sánchez', 'rol': 'secretaria'},
        ]
        
        for data in secretarias_data:
            usuario, created = Usuario.objects.get_or_create(
                usuario=data['usuario'],
                defaults={
                    'email': data['email'],
                    'nombre': data['nombre'],
                    'apellido': data['apellido'],
                    'rol': data['rol'],
                }
            )
            if created:
                usuario.set_password('password123')
                usuario.save()
            secretarias.append(usuario)
            self.stdout.write(f'  Secretaria: {usuario.nombre} {usuario.apellido}')

        # 2. Crear Pacientes
        self.stdout.write('\n=== Creando Pacientes ===')
        pacientes = []
        nombres_m = ['Juan', 'Carlos', 'Luis', 'Miguel', 'José', 'Pedro', 'Fernando', 'Roberto', 'Diego', 'Andrés']
        apellidos_m = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores']
        nombres_f = ['María', 'Ana', 'Carmen', 'Laura', 'Patricia', 'Sofía', 'Isabel', 'Elena', 'Mónica', 'Andrea']
        apellidos_f = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores']

        for i in range(30):  # Crear 30 pacientes
            es_mujer = random.choice([True, False])
            nombres_list = nombres_f if es_mujer else nombres_m
            apellidos_list = apellidos_f if es_mujer else apellidos_m
            
            nombre = random.choice(nombres_list)
            apellido = random.choice(apellidos_list)
            fecha_nac = date.today() - timedelta(days=random.randint(365*18, 365*70))
            dui = f"{random.randint(10000000, 99999999)}-{random.randint(0, 9)}"
            
            paciente = Paciente.objects.create(
                nombres=nombre,
                apellidos=apellido,
                dui=dui,
                fecha_nacimiento=fecha_nac,
                sexo='F' if es_mujer else 'M',
                telefono=f"2{random.randint(1000000, 9999999)}",
                celular=f"7{random.randint(10000000, 99999999)}",
                email=f"{nombre.lower()}.{apellido.lower()}@email.com",
                direccion=f"Col. {random.choice(['Centro', 'San Benito', 'Escalón', 'San Francisco', 'Merliot'])}",
                datos_medicos={
                    "alergias": random.choice(["Ninguna", "Penicilina", "Látex", ""]),
                    "medicamentos": random.choice(["Ninguno", "Aspirina", "Ibuprofeno", ""]),
                    "tomaMedicamento": random.choice([True, False]),
                }
            )
            pacientes.append(paciente)
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Creados {i + 1} pacientes...')

        self.stdout.write(self.style.SUCCESS(f'  Total pacientes creados: {len(pacientes)}'))

        # 3. Crear Citas
        self.stdout.write('\n=== Creando Citas ===')
        estados = [estado[0] for estado in ESTADO_CHOICES]
        citas = []
        
        for i in range(50):  # Crear 50 citas
            paciente = random.choice(pacientes)
            doctor = random.choice(doctores) if random.random() > 0.2 else None
            estado = random.choice(estados)
            
            # Fechas en el pasado y futuro
            dias_offset = random.randint(-60, 30)
            fecha_hora = timezone.now() + timedelta(days=dias_offset, hours=random.randint(8, 17))
            
            motivos = [
                "Limpieza dental",
                "Consulta general",
                "Dolor de muela",
                "Ortodoncia",
                "Extracción",
                "Endodoncia",
                "Blanqueamiento",
                "Revisión post-tratamiento",
            ]
            
            cita = Cita.objects.create(
                paciente=paciente,
                nombre_completo=paciente.nombre_completo,
                fecha_hora=fecha_hora,
                motivo=random.choice(motivos),
                doctor=doctor,
                estado=estado
            )
            citas.append(cita)
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Creadas {i + 1} citas...')

        self.stdout.write(self.style.SUCCESS(f'  Total citas creadas: {len(citas)}'))

        # 4. Crear Facturas y Detalles
        self.stdout.write('\n=== Creando Facturas ===')
        metodos_pago = ['Efectivo', 'Tarjeta', 'Transferencia', 'Cheque']
        estados_factura = ['Pagada', 'Pendiente', 'Cancelada']
        servicios = [
            {'descripcion': 'Limpieza dental', 'precio': 25.00},
            {'descripcion': 'Consulta general', 'precio': 30.00},
            {'descripcion': 'Extracción simple', 'precio': 40.00},
            {'descripcion': 'Endodoncia', 'precio': 150.00},
            {'descripcion': 'Ortodoncia mensual', 'precio': 80.00},
            {'descripcion': 'Blanqueamiento', 'precio': 200.00},
            {'descripcion': 'Resina dental', 'precio': 50.00},
            {'descripcion': 'Corona', 'precio': 300.00},
        ]

        facturas = []
        for i in range(25):  # Crear 25 facturas
            paciente = random.choice(pacientes)
            fecha_emision = date.today() - timedelta(days=random.randint(0, 90))
            metodo = random.choice(metodos_pago)
            estado = random.choice(estados_factura)
            
            # Crear factura
            idfactura = f"FAC-{fecha_emision.year}-{str(i+1).zfill(5)}"
            factura = Factura.objects.create(
                idfactura=idfactura,
                fecha_emision=fecha_emision,
                monto_total=0,  # Se calculará después
                metodo_pago=metodo,
                estado=estado,
                paciente=paciente
            )
            
            # Crear 1-4 detalles por factura
            num_detalles = random.randint(1, 4)
            monto_total = 0
            
            for j in range(num_detalles):
                servicio = random.choice(servicios)
                cantidad = random.randint(1, 3)
                precio_unitario = servicio['precio']
                subtotal = precio_unitario * cantidad
                monto_total += subtotal
                
                DetalleFactura.objects.create(
                    descripcion=servicio['descripcion'],
                    precio_unitario=precio_unitario,
                    cantidad=cantidad,
                    factura=factura
                )
            
            factura.monto_total = int(monto_total)
            factura.save()
            facturas.append(factura)
            if (i + 1) % 5 == 0:
                self.stdout.write(f'  Creadas {i + 1} facturas...')

        self.stdout.write(self.style.SUCCESS(f'  Total facturas creadas: {len(facturas)}'))

        # 5. Crear Insumos y Movimientos de Stock
        self.stdout.write('\n=== Creando Insumos y Movimientos ===')
        insumos_data = [
            {'nombre': 'Guantes de Nitrilo', 'descripcion': 'Caja de 100 unidades, sin látex.'},
            {'nombre': 'Mascarillas Quirúrgicas', 'descripcion': 'Paquete de 50 mascarillas de 3 capas.'},
            {'nombre': 'Amalgama Dental', 'descripcion': 'Cápsulas de amalgama de plata, 50 unidades.'},
            {'nombre': 'Resina Compuesta', 'descripcion': 'Jeringa de 4g, color A2.'},
            {'nombre': 'Anestesia Local', 'descripcion': 'Cartuchos de lidocaína al 2% con epinefrina.'},
            {'nombre': 'Agujas Descartables', 'descripcion': 'Caja de 100 agujas estériles.'},
            {'nombre': 'Algodón Estéril', 'descripcion': 'Paquete de 500 unidades.'},
            {'nombre': 'Hilo Dental', 'descripcion': 'Caja de 50 unidades.'},
        ]
        
        insumos = []
        for data in insumos_data:
            insumo, created = Insumo.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'descripcion': data['descripcion'], 'stock_actual': 0}
            )
            insumos.append(insumo)
            self.stdout.write(f'  Insumo: {insumo.nombre}')

        # Crear movimientos de stock
        secretaria = random.choice(secretarias) if secretarias else None
        for i in range(30):  # Crear 30 movimientos
            insumo = random.choice(insumos)
            tipo = random.choice(['entrada', 'salida'])
            cantidad = random.randint(5, 50)
            
            # Asegurar stock suficiente para salidas
            if tipo == 'salida' and insumo.stock_actual < cantidad:
                # Crear entrada primero
                insumo.stock_actual += cantidad + random.randint(10, 30)
                insumo.save()
                Movimiento_stock.objects.create(
                    tipo='entrada',
                    cantidad=cantidad + random.randint(10, 30),
                    insumo=insumo,
                    usuario=secretaria,
                    nombre_usuario=secretaria.nombre + ' ' + secretaria.apellido if secretaria else 'Sistema',
                    rol_usuario=secretaria.rol if secretaria else 'Sistema'
                )
            
            if tipo == 'entrada':
                insumo.stock_actual += cantidad
            else:
                insumo.stock_actual -= cantidad
            
            insumo.save()
            
            Movimiento_stock.objects.create(
                tipo=tipo,
                cantidad=cantidad,
                insumo=insumo,
                usuario=secretaria,
                nombre_usuario=secretaria.nombre + ' ' + secretaria.apellido if secretaria else 'Sistema',
                rol_usuario=secretaria.rol if secretaria else 'Sistema',
                fecha=date.today() - timedelta(days=random.randint(0, 60))
            )

        self.stdout.write(self.style.SUCCESS(f'  Total movimientos creados: 30'))

        # 6. Crear Encuestas
        self.stdout.write('\n=== Creando Encuestas ===')
        preguntas_predefinidas = [
            "¿Cómo calificaría la atención del doctor?",
            "¿Cómo calificaría la limpieza de las instalaciones?",
            "¿Recomendaría nuestra clínica a otras personas?",
            "¿Cómo calificaría el tiempo de espera?",
        ]
        
        opciones_respuestas = [
            ["Excelente", "Muy Buena", "Buena", "Regular", "Mala"],
            ["Excelente", "Muy Buena", "Buena", "Regular", "Mala"],
            ["Sí", "No estoy seguro", "No"],
            ["Excelente", "Muy Bueno", "Bueno", "Regular", "Malo"],
        ]

        for i in range(20):  # Crear 20 encuestas
            # Crear preguntas_respuestas
            preguntas_respuestas = {}
            for j, pregunta in enumerate(preguntas_predefinidas):
                respuesta = random.choice(opciones_respuestas[j])
                preguntas_respuestas[pregunta] = respuesta
            
            # Calcular nivel_satisfaccion promedio
            mapeo_valores = {
                'Excelente': 5, 'Muy Buena': 4, 'Muy Bueno': 4,
                'Buena': 3, 'Bueno': 3, 'Regular': 2,
                'Mala': 1, 'Malo': 1, 'Sí': 5,
                'No estoy seguro': 3, 'No': 1
            }
            
            valores = [mapeo_valores.get(resp, 3) for resp in preguntas_respuestas.values()]
            nivel_satisfaccion = round(sum(valores) / len(valores)) if valores else 3
            
            observaciones = random.choice([
                "", "Muy buena atención", "Excelente servicio",
                "Podría mejorar el tiempo de espera", "Todo perfecto"
            ])
            
            encuesta = Encuesta.objects.create(
                fecha=date.today() - timedelta(days=random.randint(0, 90)),
                observaciones=observaciones,
                nivel_satisfaccion=nivel_satisfaccion,
                preguntas_respuestas=preguntas_respuestas
            )
            if (i + 1) % 5 == 0:
                self.stdout.write(f'  Creadas {i + 1} encuestas...')

        self.stdout.write(self.style.SUCCESS(f'  Total encuestas creadas: 20'))

        # 7. Crear Expedientes y Fichas de Ortodoncia
        self.stdout.write('\n=== Creando Expedientes ===')
        expedientes = []
        try:
            pacientes_seleccionados = random.sample(pacientes, min(15, len(pacientes)))
            
            for i, paciente in enumerate(pacientes_seleccionados):
                try:
                    numero_expediente = f"EXP-{date.today().year}-{str(i+1).zfill(5)}"
                    expediente = Expediente.objects.create(
                        paciente=paciente,
                        numero_expediente=numero_expediente
                    )
                    expedientes.append(expediente)
                    
                    # Crear Ficha de Ortodoncia para algunos
                    if random.random() > 0.5:
                        try:
                            ficha = FichaOrtodoncia.objects.create(
                                expediente=expediente,
                                motivo_consulta_inicial=random.choice([
                                    "Dientes apiñados",
                                    "Mordida cruzada",
                                    "Sobremordida",
                                    "Espacios entre dientes",
                                ]),
                                diagnostico=random.choice([
                                    "Maloclusión clase I",
                                    "Maloclusión clase II",
                                    "Maloclusión clase III",
                                ]),
                                oclusion=random.choice(["Normal", "Cruzada", "Abierta"]),
                                mordida=random.choice(["Normal", "Profunda", "Abierta"]),
                                plan_tratamiento=random.choice([
                                    "Brackets metálicos 18 meses",
                                    "Brackets cerámicos 24 meses",
                                    "Invisalign 12 meses",
                                ]),
                                estado_tratamiento=random.choice(['activo', 'finalizado'])
                            )
                            
                            # Crear algunas notas de progreso
                            if random.random() > 0.3:
                                try:
                                    for nota_i in range(random.randint(1, 3)):
                                        NotaProgresoOrto.objects.create(
                                            ficha_ortodoncia=ficha,
                                            motivo_visita=random.choice([
                                                "Ajuste de brackets",
                                                "Revisión mensual",
                                                "Cambio de ligas",
                                            ]),
                                            observaciones_clinicas=random.choice([
                                                "Progreso satisfactorio",
                                                "Mejora notable",
                                                "Requiere ajuste",
                                            ]),
                                            procedimiento_realizado=random.choice([
                                                "Ajuste de arco",
                                                "Cambio de ligas",
                                                "Limpieza",
                                            ]),
                                            odontograma_snapshot=[],
                                            odontograma_comentarios=""
                                        )
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'  No se pudieron crear notas de progreso: {e}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'  No se pudo crear ficha de ortodoncia: {e}'))
                    
                    # Crear Odontograma para algunos expedientes
                    if random.random() > 0.4:
                        try:
                            odontograma, _ = Odontograma.objects.get_or_create(expediente=expediente)
                            
                            # Crear versiones del odontograma
                            for version_i in range(random.randint(1, 2)):
                                try:
                                    version = OdontogramaVersion.objects.create(
                                        odontograma=odontograma,
                                        comentario=random.choice([
                                            "Estado inicial",
                                            "Después de tratamiento",
                                            "Revisión",
                                        ])
                                    )
                                    
                                    # Crear algunos detalles
                                    piezas = random.sample(range(11, 48), random.randint(3, 8))
                                    caras = ['O', 'M', 'D', 'V', 'P']
                                    condiciones = ['Caries', 'Obturación', 'Corona', 'Sano']
                                    
                                    for pieza in piezas:
                                        cara = random.choice(caras)
                                        condicion = random.choice(condiciones)
                                        try:
                                            OdontogramaDetalle.objects.create(
                                                version=version,
                                                pieza_numero=pieza,
                                                cara=cara,
                                                condicion=condicion
                                            )
                                        except Exception as e:
                                            self.stdout.write(self.style.WARNING(f'  No se pudo crear detalle de odontograma: {e}'))
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'  No se pudo crear versión de odontograma: {e}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'  No se pudo crear odontograma: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  No se pudo crear expediente: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'  Total expedientes creados: {len(expedientes)}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  No se pudieron crear expedientes (tablas no existen): {e}'))

        self.stdout.write(self.style.SUCCESS('\n=== Seeder completado exitosamente ==='))
        self.stdout.write(self.style.SUCCESS(f'Resumen:'))
        self.stdout.write(f'  - Usuarios: {len(doctores) + len(secretarias)}')
        self.stdout.write(f'  - Pacientes: {len(pacientes)}')
        self.stdout.write(f'  - Citas: {len(citas)}')
        self.stdout.write(f'  - Facturas: {len(facturas)}')
        self.stdout.write(f'  - Insumos: {len(insumos)}')
        self.stdout.write(f'  - Encuestas: 20')
        self.stdout.write(f'  - Expedientes: {len(expedientes)}')

