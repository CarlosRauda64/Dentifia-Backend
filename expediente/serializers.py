from rest_framework import serializers

from .models import (
    Expediente,
    FichaOrtodoncia,
    NotaProgresoOrto,
    Odontograma,
    OdontogramaVersion,
    OdontogramaDetalle,
)


class NotaProgresoOrtoSerializer(serializers.ModelSerializer):
    ficha_ortodoncia_numero_expediente = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NotaProgresoOrto
        fields = [
            "id",
            "ficha_ortodoncia",
            "ficha_ortodoncia_numero_expediente",
            "motivo_visita",
            "observaciones_clinicas",
            "procedimiento_realizado",
            "odontograma_snapshot",
            "odontograma_comentarios",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "ficha_ortodoncia_numero_expediente"]

    def get_ficha_ortodoncia_numero_expediente(self, obj):
        return obj.ficha_ortodoncia.expediente.numero_expediente


class FichaOrtodonciaSerializer(serializers.ModelSerializer):
    expediente_numero = serializers.CharField(
        source="expediente.numero_expediente", read_only=True
    )
    notas_progreso = NotaProgresoOrtoSerializer(many=True, read_only=True)

    class Meta:
        model = FichaOrtodoncia
        fields = [
            "id",
            "expediente",
            "expediente_numero",
            "motivo_consulta_inicial",
            "diagnostico",
            "oclusion",
            "mordida",
            "plan_tratamiento",
            "estado_tratamiento",
            "created_at",
            "notas_progreso",
        ]
        read_only_fields = ["id", "created_at", "expediente_numero", "notas_progreso"]


class OdontogramaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdontogramaDetalle
        fields = ["id", "pieza_numero", "cara", "condicion"]
        read_only_fields = ["id"]


class OdontogramaDetalleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdontogramaDetalle
        fields = ["pieza_numero", "cara", "condicion"]


class OdontogramaVersionSerializer(serializers.ModelSerializer):
    odontograma_numero_expediente = serializers.SerializerMethodField(read_only=True)
    detalles = OdontogramaDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = OdontogramaVersion
        fields = [
            "id",
            "odontograma",
            "odontograma_numero_expediente",
            "comentario",
            "created_at",
            "detalles",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "odontograma_numero_expediente",
            "detalles",
        ]

    def get_odontograma_numero_expediente(self, obj):
        return obj.odontograma.expediente.numero_expediente


class OdontogramaVersionCreateSerializer(serializers.ModelSerializer):
    detalles = OdontogramaDetalleWriteSerializer(many=True, write_only=True)

    class Meta:
        model = OdontogramaVersion
        fields = ["id", "odontograma", "comentario", "detalles", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles", [])
        version = OdontogramaVersion.objects.create(**validated_data)
        if detalles_data:
            OdontogramaDetalle.objects.bulk_create(
                OdontogramaDetalle(version=version, **detalle) for detalle in detalles_data
            )
        return version

    def to_representation(self, instance):
        return OdontogramaVersionSerializer(instance, context=self.context).data


class OdontogramaSerializer(serializers.ModelSerializer):
    expediente_numero = serializers.CharField(
        source="expediente.numero_expediente", read_only=True
    )
    versiones = OdontogramaVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Odontograma
        fields = ["id", "expediente", "expediente_numero", "created_at", "versiones"]
        read_only_fields = ["id", "created_at", "expediente_numero", "versiones"]


class ExpedienteSerializer(serializers.ModelSerializer):
    paciente_detalle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Expediente
        fields = ["id", "paciente", "numero_expediente", "created_at", "paciente_detalle"]
        read_only_fields = ["id", "created_at", "paciente_detalle"]

    def get_paciente_detalle(self, obj):
        paciente = obj.paciente
        return {
            "id": paciente.id,
            "nombres": paciente.nombres,
            "apellidos": paciente.apellidos,
            "nombre_completo": paciente.nombre_completo,
            "telefono": paciente.telefono,
            "celular": paciente.celular,
            "email": paciente.email,
        }


class ExpedienteDetailSerializer(ExpedienteSerializer):
    fichas_ortodoncia = FichaOrtodonciaSerializer(many=True, read_only=True)
    odontograma = OdontogramaSerializer(read_only=True)

    class Meta(ExpedienteSerializer.Meta):
        fields = ExpedienteSerializer.Meta.fields + [
            "fichas_ortodoncia",
            "odontograma",
        ]
        read_only_fields = ExpedienteSerializer.Meta.read_only_fields + [
            "fichas_ortodoncia",
            "odontograma",
        ]
