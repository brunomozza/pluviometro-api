from rest_framework import serializers

from .models import Leitura


class LeituraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leitura
        fields = [
            "id",
            "dispositivo",
            "pulsos",
            "chuva_mm",
            "data_hora",
        ]
        read_only_fields = [
            "id",
            "data_hora",
        ]
