from datetime import timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse_lazy
from django.db.models import Max, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.views.generic import ListView, DeleteView
from .models import Leitura
from .serializers import LeituraSerializer

# ==========================================================
# CONFIGURAÇÕES DE FUSO
# ==========================================================

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


# ==========================================================
# LISTAGEM DE LEITURAS
# ==========================================================

class ListaLeiturasView(ListView):

    model = Leitura
    template_name = "pluviometro/leituras/lista.html"
    context_object_name = "leituras"
    paginate_by = 50

    def get_queryset(self):
        dispositivo = self.request.GET.get("dispositivo")

        queryset = Leitura.objects.all().order_by("-data_hora")

        if dispositivo:
            queryset = queryset.filter(
                dispositivo=dispositivo
            )

        return queryset


# ==========================================================
# DELETE DE LEITURA
# ==========================================================

class DeleteLeituraView(DeleteView):

    model = Leitura
    template_name = (
        "pluviometro/leituras/"
        "confirmar_exclusao.html"
    )
    success_url = reverse_lazy("lista_leituras")

    def get_success_url(self):
        dispositivo = self.request.GET.get("dispositivo")

        if dispositivo:
            return f"{reverse_lazy('lista_leituras')}?dispositivo={dispositivo}"

        return reverse_lazy("lista_leituras")

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


from django.utils import timezone
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from zoneinfo import ZoneInfo

from .models import Leitura


FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


class VolumePeriodoView(APIView):

    def get(self, request):

        dispositivo = request.query_params.get("dispositivo")
        inicio = request.query_params.get("inicio")
        fim = request.query_params.get("fim")

        if not dispositivo:
            return Response(
                {"erro": "Informe o dispositivo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not inicio or not fim:
            return Response(
                {"erro": "Informe início e fim do período."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            inicio = datetime.fromisoformat(inicio)
            fim = datetime.fromisoformat(fim)

            # Define o fuso caso o datetime venha sem timezone
            if timezone.is_naive(inicio):
                inicio = inicio.replace(
                    tzinfo=FUSO_BRASIL
                )

            if timezone.is_naive(fim):
                fim = fim.replace(
                    tzinfo=FUSO_BRASIL
                )

        except ValueError:

            return Response(
                {"erro": "Formato de data inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inicio >= fim:

            return Response(
                {
                    "erro":
                    "A data inicial deve ser anterior à data final."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leituras = Leitura.objects.filter(
            dispositivo=dispositivo,
            data_hora__gte=inicio,
            data_hora__lt=fim
        )

        resultado = leituras.aggregate(
            total=Sum("chuva_mm")
        )

        total = resultado["total"] or 0

        return Response({
            "dispositivo": dispositivo,
            "inicio": inicio.astimezone(
                FUSO_BRASIL
            ).strftime("%d/%m/%Y %H:%M:%S"),

            "fim": fim.astimezone(
                FUSO_BRASIL
            ).strftime("%d/%m/%Y %H:%M:%S"),

            "chuva_mm": float(total),
            "quantidade_leituras": leituras.count(),
        })


from datetime import timedelta

from django.db.models import Sum
from django.db.models.functions import TruncHour, TruncDay
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Leitura


class GraficoLeiturasView(APIView):

    def get(self, request):

        dispositivo = request.query_params.get(
            "dispositivo",
            "PLUVIO-001"
        )

        periodo = request.query_params.get(
            "periodo",
            "24h"
        )

        agora = timezone.now()


        # ------------------------------------------
        # Define período
        # ------------------------------------------

        if periodo == "24h":

            inicio = agora - timedelta(hours=24)

            truncacao = TruncHour(
                "data_hora"
            )

        elif periodo == "7d":

            inicio = agora - timedelta(days=7)

            truncacao = TruncDay(
                "data_hora"
            )

        elif periodo == "30d":

            inicio = agora - timedelta(days=30)

            truncacao = TruncDay(
                "data_hora"
            )

        else:

            return Response(
                {
                    "erro":
                    "Período inválido."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        # ------------------------------------------
        # Consulta
        # ------------------------------------------

        dados = (
            Leitura.objects
            .filter(
                dispositivo=dispositivo,
                data_hora__gte=inicio,
                data_hora__lte=agora
            )
            .annotate(
                periodo=truncacao
            )
            .values("periodo")
            .annotate(
                chuva_mm=Sum("chuva_mm")
            )
            .order_by("periodo")
        )


        # ------------------------------------------
        # Formata resposta
        # ------------------------------------------

        resultado = []

        for item in dados:

            data = timezone.localtime(
                item["periodo"]
            )

            if periodo == "24h":

                label = data.strftime(
                    "%d/%m %H:%M"
                )

            else:

                label = data.strftime(
                    "%d/%m"
                )


            resultado.append({
                "periodo": label,
                "chuva_mm": float(
                    item["chuva_mm"] or 0
                )
            })


        return Response({
            "dispositivo": dispositivo,
            "periodo": periodo,
            "dados": resultado
        })

def dashboard(request):
    return render(
        request,
        "pluviometro/dashboard.html"
    )