# Loyality/models.py — PostgreSQL-ready версия (2026)
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
class User(AbstractUser):
    """
    Кастомная модель пользователя с поддержкой Telegram и барист.
    """
    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=*("Имя")
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name=*("Телефон")
    )
    is_barista = models.BooleanField(
        default=False,
        verbose_name=_("Бариста")
    )
    employee_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Код сотрудника")
    )
    # Telegram-поля
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=*("Telegram ID")
    )
    telegram_username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        verbose_name=*("Telegram @username")
    )
    # Избегаем конфликтов с auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        verbose_name=*('группы')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        verbose_name=*('права пользователя')
    )
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        indexes = [
            models.Index(fields=['telegram_id'], name='user_telegram_id_idx'),
            models.Index(fields=['telegram_username'], name='user_telegram_username_idx'),
        ]
    def **str**(self):
        if self.telegram_username:
            return f"@{self.telegram_username}"
        if self.telegram_id:
            return f"TG_{self.telegram_id}"
        return self.username or f"User_{self.id}"
class LoyaltyProfile(models.Model):
    """
    Профиль лояльности: количество штампов пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty_profile",
        verbose_name=*("Пользователь")
    )
    stamps = models.PositiveIntegerField(
        default=0,
        verbose_name=*("Штампы")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Обновлено")
    )
    class Meta:
        verbose_name = _("Профиль лояльности")
        verbose_name_plural = _("Профили лояльности")
        indexes = [
            models.Index(fields=['user'], name='loyalty_profile_user_idx'),
        ]
    def **str**(self):
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
        related_name="loyalty_codes",
        verbose_name=*("Пользователь")
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=*("Код")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=*("Создан")
    )
    expires_at = models.DateTimeField(
        verbose_name=*("Истекает")
    )
    redeemed = models.BooleanField(
        default=False,
        verbose_name=*("Использован")
    )
    redeemed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=*("Использован в")
    )
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activated_codes",
        verbose_name=_("Использовал")
    )
    class Meta:
        verbose_name = _("Код лояльности")
        verbose_name_plural = _("Коды лояльности")
        indexes = [
            models.Index(fields=['code'], name='loyalty_code_code_idx'),
            models.Index(fields=['user'], name='loyalty_code_user_idx'),
        ]
    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at and not self.redeemed
    def is_used(self) -> bool:
        return self.redeemed
    def **str**(self):
        status = "✓" if self.redeemed else "✗"
        return f"{self.code} → {self.user} [{status}]"
class LoyaltyStamp(models.Model):
    """
    История начисления штампов (по одному на запись).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="loyalty_stamps",
        on_delete=models.CASCADE,
        verbose_name=*("Пользователь")
    )
    source = models.CharField(
        max_length=32,
        blank=True,
        default="code",
        verbose_name=*("Источник")
    )  # code, manual, manual_barista, etc.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=*("Создан")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="given_stamps",
        verbose_name=*("Начислил")
    )
    class Meta:
        verbose_name = _("Штамп лояльности")
        verbose_name_plural = _("Штампы лояльности")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user'], name='loyalty_stamp_user_idx'),
            models.Index(fields=['created_at'], name='loyalty_stamp_created_idx'),
        ]
    def **str**(self):
        by = f" by {self.created_by}" if self.created_by else ""
        return f"Штамп для {self.user} [{self.source}]{by} — {self.created_at:%Y-%m-%d %H:%M}"
