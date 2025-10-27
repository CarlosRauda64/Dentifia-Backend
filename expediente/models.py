from django.db import models

from pacientes.models import Paciente


class Expediente(models.Model):
	paciente = models.ForeignKey(
		Paciente,
		on_delete=models.CASCADE,
		related_name="expedientes",
	)
	numero_expediente = models.CharField(max_length=50, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.numero_expediente} - {self.paciente.nombre_completo}"

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["numero_expediente"]),
			models.Index(fields=["paciente"]),
		]


class FichaOrtodoncia(models.Model):
	class EstadoTratamiento(models.TextChoices):
		ACTIVO = "activo", "Activo"
		FINALIZADO = "finalizado", "Finalizado"

	expediente = models.ForeignKey(
		Expediente,
		on_delete=models.CASCADE,
		related_name="fichas_ortodoncia",
	)
	motivo_consulta_inicial = models.TextField()
	diagnostico = models.TextField()
	oclusion = models.CharField(max_length=100)
	mordida = models.CharField(max_length=100)
	plan_tratamiento = models.TextField()
	estado_tratamiento = models.CharField(
		max_length=15,
		choices=EstadoTratamiento.choices,
		default=EstadoTratamiento.ACTIVO,
	)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Ficha ortodoncia #{self.id} - {self.expediente.numero_expediente}"

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["expediente"]),
			models.Index(fields=["estado_tratamiento"]),
		]


class NotaProgresoOrto(models.Model):
	ficha_ortodoncia = models.ForeignKey(
		FichaOrtodoncia,
		on_delete=models.CASCADE,
		related_name="notas_progreso",
	)
	motivo_visita = models.TextField()
	observaciones_clinicas = models.TextField()
	procedimiento_realizado = models.TextField()
	odontograma_snapshot = models.JSONField(default=list, blank=True)
	odontograma_comentarios = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Nota {self.created_at:%Y-%m-%d} - Ficha {self.ficha_ortodoncia_id}"

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["ficha_ortodoncia"]),
			models.Index(fields=["created_at"]),
		]


class Odontograma(models.Model):
	expediente = models.OneToOneField(
		Expediente,
		on_delete=models.CASCADE,
		related_name="odontograma",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Odontograma {self.expediente.numero_expediente}"

	class Meta:
		ordering = ["-created_at"]
		indexes = [models.Index(fields=["expediente"])]


class OdontogramaVersion(models.Model):
	odontograma = models.ForeignKey(
		Odontograma,
		on_delete=models.CASCADE,
		related_name="versiones",
	)
	comentario = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Versión {self.id} - {self.odontograma.expediente.numero_expediente}"

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["odontograma"]),
			models.Index(fields=["created_at"]),
		]


class OdontogramaDetalle(models.Model):
	class Cara(models.TextChoices):
		O = "O", "Oclusal"
		M = "M", "Mesial"
		D = "D", "Distal"
		V = "V", "Vestibular"
		P = "P", "Palatina"
		GLOBAL = "GLOBAL", "Global"

	version = models.ForeignKey(
		OdontogramaVersion,
		on_delete=models.CASCADE,
		related_name="detalles",
	)
	pieza_numero = models.PositiveIntegerField()
	cara = models.CharField(max_length=7, choices=Cara.choices)
	condicion = models.CharField(max_length=50)

	def __str__(self):
		return (
			f"Pieza {self.pieza_numero} ({self.cara}) - "
			f"{self.version.odontograma.expediente.numero_expediente}"
		)

	class Meta:
		indexes = [
			models.Index(fields=["version"]),
			models.Index(fields=["pieza_numero"]),
		]
		unique_together = ("version", "pieza_numero", "cara", "condicion")
