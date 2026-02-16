"""Location models for countries and provinces."""

from django.db import models


class Country(models.Model):
    """Country model with ISO 3166-1 alpha-2 code."""

    class Meta:
        verbose_name = "país"
        verbose_name_plural = "países"
        ordering = ["name"]  # noqa: RUF012

    code = models.CharField(max_length=2, unique=True, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Province(models.Model):
    """Province/State model linked to a country."""

    class Meta:
        verbose_name = "provincia"
        verbose_name_plural = "provincias"
        ordering = ["country", "name"]  # noqa: RUF012
        unique_together = ["country", "code"]  # noqa: RUF012

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="provinces",
    )
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}, {self.country.name}"
