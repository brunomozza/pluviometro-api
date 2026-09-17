from django.urls import path

from .views import (
    PluviometrosView,
    LeiturasView,
    ResumoLeiturasView,
    LeiturasHojeView,
    HistoricoLeiturasView,
)


urlpatterns = [

    path(
        "pluviometros/",
        PluviometrosView.as_view(),
        name="pluviometros"
    ),

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
        "leituras/hoje/",
        LeiturasHojeView.as_view(),
        name="leituras-hoje"
    ),

    path(
        "leituras/historico/",
        HistoricoLeiturasView.as_view(),
        name="leituras-historico"
    ),

]
