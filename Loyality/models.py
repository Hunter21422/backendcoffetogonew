# Loyality/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Кастомная модель пользователя с поддержкой Telegram и барист.
    """
    name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")
    is_barista = models.BooleanField(default=False)

    employee_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        default=None
    )

    # === ПОЛЯ ДЛЯ TELEGRAM ===
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )  # ← уникальный @username из Telegram

    # Переопределяем related_name, чтобы избежать конфликтов с auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    def __str__(self):
        if self.telegram_username:
            return f"@{self.telegram_username}"
        if self.telegram_id:
            return f"TG_{self.telegram_id}"
        return self.username or f"User_{self.id}"


class LoyaltyProfile(models.Model):
    """
    Профиль лояльности: сколько штампов у пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty_profile",
    )
    stamps = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль лояльности"
        verbose_name_plural = "Профили лояльности"

    def __str__(self):
        return f"{self.user} — {self.stamps} штамп(ов)"

    def add_stamp(self, count=1):
        """Начислить штампы с учётом лимита."""
        max_stamps = getattr(settings, "LOYALTY_MAX_STAMPS", 6)
        if self.stamps >= max_stamps:
            return False
        self.stamps = min(self.stamps + count, max_stamps)
        self.save(update_fields=["stamps", "updated_at"])
        return True

    def reset_stamps(self):
        """Сбросить штампы."""
        self.stamps = 0
        self.save(update_fields=["stamps", "updated_at"])


class LoyaltyCode(models.Model):
    """
    Одноразовый код на штамп(ы) с TTL.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty_codes"
    )
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activated_codes"
    )

    class Meta:
        verbose_name = "Код лояльности"
        verbose_name_plural = "Коды лояльности"

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at and not self.redeemed

    def is_used(self) -> bool:
        return self.redeemed

    def __str__(self):
        status = "✓" if self.redeemed else "✗"
        return f"{self.code} → {self.user} [{status}]"


class LoyaltyStamp(models.Model):
    """
    История начисления штампов (по одному на запись).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="loyalty_stamps",
        on_delete=models.CASCADE
    )
    source = models.CharField(
        max_length=32,
        blank=True,
        default="code"
    )  # code, manual, manual_barista, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="given_stamps"
    )

    class Meta:
        verbose_name = "Штамп лояльности"
        verbose_name_plural = "Штампы лояльности"
        ordering = ["-created_at"]

    def __str__(self):
        by = f" by {self.created_by}" if self.created_by else ""
        return f"Штамп для {self.user} [{self.source}]{by} — {self.created_at:%Y-%m-%d %H:%M}"
