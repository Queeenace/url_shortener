from django.db import models
import string
import random
from django.db.models import F
from django.contrib.auth.models import User 

class ShortenedURL(models.Model):
    original_url = models.URLField(
        unique=True, verbose_name="Оригинальная ссылка")
    short_code = models.CharField(
        max_length=10, unique=True, blank=True, verbose_name="Короткая ссылка")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    click_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество переходов")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortened_urls', null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        if not self.short_code:
            self.short_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code() -> str:
        length = 6
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(characters, k=length))
            if not ShortenedURL.objects.filter(short_code=code).exists():
                return code

    def increment_clicks(self) -> None:
        self.click_count = F('click_count') + 1
        self.save()

    def __str__(self) -> str:
        return f"{self.short_code} -> {self.original_url} (Переходов: {self.click_count})"