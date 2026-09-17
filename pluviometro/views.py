from datetime import timedelta

from django.db.models import Max, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Leitura
from .serializers import LeituraSerializer

# ==========================================================
# GET /api/pluviometros/
# ==========================================================


class PluviometrosView(APIView):

    def get(self, request):

        dispositivos = (
            Leitura.objects
            .values("dispositivo")
            .distinct()
            .order_by("dispositivo")
        )

        return Response(dispositivos)


# ==========================================================
# GET /api/leituras/
# ==========================================================

class LeiturasView(APIView):

    def get(self, request):
        leituras = Leitura.objects.all().order_by("-data_hora")
        serializer = LeituraSerializer(leituras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeituraSerializer(data=request.data)

        if serializer.is_valid():
            leitura = serializer.save()
            return Response(
                LeituraSerializer(leitura).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ==========================================================
# GET /api/leituras/resumo/
# ==========================================================

class ResumoLeiturasView(APIView):

    def get(self, request):

        dispositivo = request.GET.get("dispositivo")

        if not dispositivo:
            return Response(
                {
                    "erro": "Informe o dispositivo."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        agora = timezone.now()

        inicio_dia = agora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        inicio_hora = agora - timedelta(hours=1)

        inicio_mes = agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        base = Leitura.objects.filter(
            dispositivo=dispositivo
        )

        hoje = base.filter(
            data_hora__gte=inicio_dia
        ).aggregate(
            total=Sum("chuva_mm")
        )

        ultima_hora = base.filter(
            data_hora__gte=inicio_hora
        ).aggregate(
            total=Sum("chuva_mm")
        )

        mes = base.filter(
            data_hora__gte=inicio_mes
        ).aggregate(
            total=Sum("chuva_mm")
        )

        total = base.aggregate(
            pulsos=Sum("pulsos"),
            chuva=Sum("chuva_mm"),
            ultima_leitura=Max("data_hora")
        )

        return Response(
            {
                "dispositivo": dispositivo,

                "chuva_hoje": float(
                    hoje["total"] or 0
                ),

                "chuva_ultima_hora": float(
                    ultima_hora["total"] or 0
                ),

                "chuva_mes": float(
                    mes["total"] or 0
                ),

                "pulsos": total["pulsos"] or 0,

                "chuva_total": float(
                    total["chuva"] or 0
                ),

                "ultima_leitura": total[
                    "ultima_leitura"
                ]
            }
        )


# ==========================================================
# GET /api/leituras/hoje/
# ==========================================================

class LeiturasHojeView(APIView):

    def get(self, request):

        dispositivo = request.GET.get("dispositivo")

        agora = timezone.now()

        inicio_dia = agora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        queryset = Leitura.objects.filter(
            data_hora__gte=inicio_dia
        )

        if dispositivo:
            queryset = queryset.filter(
                dispositivo=dispositivo
            )

        queryset = queryset.order_by(
            "-data_hora"
        )

        serializer = LeituraSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)


# ==========================================================
# GET /api/leituras/historico/
# ==========================================================

class HistoricoLeiturasView(APIView):

    def get(self, request):

        dispositivo = request.GET.get("dispositivo")

        queryset = Leitura.objects.all()

        if dispositivo:
            queryset = queryset.filter(
                dispositivo=dispositivo
            )

        queryset = queryset.order_by(
            "-data_hora"
        )

        serializer = LeituraSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)
