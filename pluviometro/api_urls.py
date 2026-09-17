from django.urls import path

from .views import (
    LeiturasView,
    ResumoLeiturasView,
    VolumePeriodoView,
    GraficoLeiturasView,
)


urlpatterns = [

    path(
        "leituras/",
        LeiturasView.as_view(),
        name="leituras"
    ),

    path(
        "leituras/resumo/",
        ResumoLeiturasView.as_view(),
        name="leituras-resumo"
    ),
    path(
        "leituras/periodo/",
        VolumePeriodoView.as_view(),
        name="leituras-periodo"
    ),
    path(
        "leituras/grafico/",
        GraficoLeiturasView.as_view(),
        name="leituras-grafico"
    ),
]