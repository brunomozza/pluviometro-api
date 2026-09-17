from django.db import models


class Leitura(models.Model):
    dispositivo = models.CharField(max_length=50)
    pulsos = models.IntegerField()
    chuva_mm = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.dispositivo} - "
            f"{self.chuva_mm} mm - "
            f"{self.data_hora}"
        )
