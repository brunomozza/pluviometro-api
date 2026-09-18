from django.urls import path

from .views import (
    ListaLeiturasView,
    DeleteLeituraView,
    dashboard
)

urlpatterns = [
    path(
        "leituras/",
        ListaLeiturasView.as_view(),
        name="lista_leituras"
    ),

    path(
        "leituras/<int:pk>/excluir/",
        DeleteLeituraView.as_view(),
        name="delete_leitura"
    ),

    path(
        "",
        dashboard,
        name="dashboard"
    ),
]