from django.db import models


class GeneralSetting(models.Model):
    name = models.CharField(
        default="",
        max_length=254,
        blank=True,
    )

    description = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    parameter = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )

    def __str__(self):
        return f"General Setting: {self.name}"

    class Meta:
        verbose_name = "General Setting"
        verbose_name_plural = "General Settings"
        ordering = ('id', 'name', 'description', 'parameter', 'updated_date', 'created_date')


class FooterSetting(models.Model):
    name = models.CharField(
        default="",
        max_length=254,
        blank=True,
    )

    description = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    parameter = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    link = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )

    def __str__(self):
        return f"Footer Setting: {self.name}"

    class Meta:
        verbose_name = "Footer Setting"
        verbose_name_plural = "Footer Settings"
        ordering = ('id', 'name', 'description', 'parameter', 'link', 'updated_date', 'created_date')


class PricingSetting(models.Model):
    name = models.CharField(
        default="",
        max_length=25,
        blank=True,
    )

    parameter = models.CharField(
        default="",
        max_length=25,
        blank=True
    )

    price = models.CharField(
        default="",
        max_length=25,
        blank=True
    )

    feat1 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    feat2 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    feat3 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    feat4 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    feat5 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    feat6 = models.CharField(
        default="",
        max_length=50,
        blank=True
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    def __str__(self):
        return f"Pricing Setting: {self.name}"

    class Meta:
        verbose_name = "Pricing Setting"
        verbose_name_plural = "Pricing Settings"
        ordering = ('id', 'name', 'parameter', 'price', 'updated_date')


class FaqSetting(models.Model):
    name = models.CharField(
        default="",
        max_length=25,
        blank=True,
    )

    question = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    answer = models.CharField(
        default="",
        max_length=254,
        blank=True
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    def __str__(self):
        return f"Faq Setting: {self.name}"

    class Meta:
        verbose_name = "Faq Setting"
        verbose_name_plural = "Faq Settings"
        ordering = ('id', 'name', 'question', 'answer', 'updated_date')
