from django.db import models

# Create your models here.

class Estacao(models.Model):
    codigo_ana = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código ANA"
    )

    nome = models.CharField(
        max_length=100
    )

    municipio = models.CharField(
        max_length=100
    )

    estado = models.CharField(
        max_length=2
    )

    rio = models.CharField(
        max_length=100
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    cota_atencao = models.FloatField()

    cota_alerta = models.FloatField()

    cota_inundacao = models.FloatField()

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Medicao(models.Model):

    estacao = models.ForeignKey(
        Estacao,
        on_delete=models.CASCADE,
        related_name="medicoes"
    )

    data_hora = models.DateTimeField()

    nivel = models.FloatField()

    vazao = models.FloatField(
        null=True,
        blank=True
    )

    chuva = models.FloatField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.estacao.nome} - {self.data_hora}"