from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db.models import Max, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Leitura
from .serializers import LeituraSerializer

# ==========================================================
# CONFIGURAÇÕES DE FUSO
# ==========================================================

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


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
# POST /api/leituras/
# ==========================================================

class LeiturasView(APIView):

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

    def post(self, request):

        serializer = LeituraSerializer(
            data=request.data
        )

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
#
# Exemplo:
#
# /api/leituras/resumo/?dispositivo=PLUVIO-001
# ==========================================================

class ResumoLeiturasView(APIView):

    def get(self, request):

        dispositivo = request.GET.get(
            "dispositivo"
        )

        if not dispositivo:

            return Response(
                {
                    "erro": "Informe o dispositivo."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # HORA ATUAL EM SÃO PAULO
        # ==================================================

        agora = timezone.now()

        agora_local = timezone.localtime(
            agora,
            FUSO_BRASIL
        )

        # ==================================================
        # INÍCIO DO DIA
        # ==================================================

        inicio_dia_local = agora_local.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        inicio_dia = inicio_dia_local.astimezone(
            timezone.get_current_timezone()
        )

        # ==================================================
        # ÚLTIMA HORA
        # ==================================================

        inicio_hora = agora - timedelta(
            hours=1
        )

        # ==================================================
        # INÍCIO DO MÊS
        # ==================================================

        inicio_mes_local = agora_local.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        inicio_mes = inicio_mes_local.astimezone(
            timezone.get_current_timezone()
        )

        # ==================================================
        # BASE
        # ==================================================

        base = Leitura.objects.filter(
            dispositivo=dispositivo
        )

        # ==================================================
        # CHUVA HOJE
        # ==================================================

        hoje = base.filter(
            data_hora__gte=inicio_dia
        ).aggregate(
            total=Sum("chuva_mm")
        )

        # ==================================================
        # CHUVA ÚLTIMA HORA
        # ==================================================

        ultima_hora = base.filter(
            data_hora__gte=inicio_hora
        ).aggregate(
            total=Sum("chuva_mm")
        )

        # ==================================================
        # CHUVA NO MÊS
        # ==================================================

        mes = base.filter(
            data_hora__gte=inicio_mes
        ).aggregate(
            total=Sum("chuva_mm")
        )

        # ==================================================
        # TOTAL HISTÓRICO
        # ==================================================

        total = base.aggregate(
            pulsos=Sum("pulsos"),
            chuva=Sum("chuva_mm"),
            ultima_leitura=Max("data_hora")
        )

        # ==================================================
        # CONVERTER ÚLTIMA LEITURA
        # PARA AMERICA/SAO_PAULO
        # ==================================================

        ultima_leitura = total[
            "ultima_leitura"
        ]

        ultima_leitura_formatada = None

        if ultima_leitura:

            ultima_leitura_local = timezone.localtime(
                ultima_leitura,
                FUSO_BRASIL
            )

            ultima_leitura_formatada = (
                ultima_leitura_local.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            )

        # ==================================================
        # RESPOSTA
        # ==================================================

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

                "ultima_leitura":
                    ultima_leitura_formatada
            }
        )


# ==========================================================
# GET /api/leituras/hoje/
# ==========================================================

class LeiturasHojeView(APIView):

    def get(self, request):

        dispositivo = request.GET.get(
            "dispositivo"
        )

        agora = timezone.now()

        agora_local = timezone.localtime(
            agora,
            FUSO_BRASIL
        )

        inicio_dia_local = agora_local.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        inicio_dia = inicio_dia_local.astimezone(
            timezone.get_current_timezone()
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

        return Response(
            serializer.data
        )


# ==========================================================
# GET /api/leituras/historico/
# ==========================================================

class HistoricoLeiturasView(APIView):

    def get(self, request):

        dispositivo = request.GET.get(
            "dispositivo"
        )

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

        return Response(
            serializer.data
        )
