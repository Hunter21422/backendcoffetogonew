# loyalty/services.py

import hmac
import hashlib
import json
from urllib.parse import parse_qsl
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import LoyaltyProfile, LoyaltyCode, LoyaltyStamp


def validate_telegram_init_data(init_data: str, bot_token: str) -> tuple[bool, dict | str]:
    """
    Проверяет подлинность initData от Telegram Web App / Mini App.

    Возвращает:
        (True, dict с данными пользователя)  - если данные валидны
        (False, сообщение об ошибке)         - если проверка не пройдена
    """
    try:
        # 1. Разбираем параметры безопасным способом
        params = dict(parse_qsl(init_data))

        # 2. Получаем hash
        received_hash = params.pop('hash', None)
        if not received_hash:
            return False, "Отсутствует параметр hash"

        # 3. Формируем строку для проверки (все параметры кроме hash, отсортированные)
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(params.items())
        )

        # 4. Создаём секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        # 5. Вычисляем HMAC
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # 6. Сравниваем хэши (защита от timing attack)
        if not hmac.compare_digest(calculated_hash, received_hash):
            return False, "Неверный hash"

        # 7. Проверяем свежесть данных (24 часа)
        auth_date_str = params.get('auth_date')
        if not auth_date_str:
            return False, "Отсутствует auth_date"

        try:
            auth_date = int(auth_date_str)
        except ValueError:
            return False, "Неверный формат auth_date"

        auth_datetime = timezone.datetime.fromtimestamp(auth_date, tz=timezone.utc)
        if timezone.now() - auth_datetime > timedelta(hours=24):
            return False, "Данные устарели (более 24 часов)"

        # 8. Парсим поле user
        user_str = params.get('user')
        if not user_str:
            return False, "Отсутствует поле user"

        try:
            user_data = json.loads(user_str)
        except json.JSONDecodeError:
            return False, "Неверный формат JSON в поле user"

        return True, user_data

    except Exception as e:
        return False, f"Ошибка валидации: {str(e)}"


# ────────────────────────────────────────────────────────────────
#                  Остальная часть сервиса лояльности
# ────────────────────────────────────────────────────────────────

def _generate_unique_code(length=6, alphabet="0123456789"):
    """Генерация уникального цифрового кода"""
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        exists = LoyaltyCode.objects.filter(
            code=code,
            redeemed=False,
            expires_at__gt=timezone.now()
        ).exists()
        if not exists:
            return code


class LoyaltyService:
    """Сервис для работы с системой лояльности"""

    @staticmethod
    def get_or_create_profile(user):
        """Получить или создать профиль лояльности"""
        profile, _ = LoyaltyProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def generate_loyalty_code(user, expires_minutes=15):
        """Создать одноразовый код лояльности"""
        code = _generate_unique_code()
        expires_at = timezone.now() + timedelta(minutes=expires_minutes)

        loyalty_code = LoyaltyCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        return loyalty_code

    @staticmethod
    @transaction.atomic
    def redeem_loyalty_code(code_value):
        """Активировать код и начислить штамп"""
        try:
            code = LoyaltyCode.objects.select_for_update().get(code=code_value)
        except LoyaltyCode.DoesNotExist:
            return False, "Код не найден"

        if code.redeemed:
            return False, "Код уже использован"

        if not code.is_valid():
            return False, "Срок действия кода истёк"

        # Начисляем штамп
        profile = LoyaltyService.get_or_create_profile(code.user)
        max_stamps = getattr(settings, "LOYALTY_MAX_STAMPS", 6)

        if profile.stamps >= max_stamps:
            return False, f"Достигнут максимум штампов ({max_stamps})"

        profile.stamps = F('stamps') + 1
        profile.save(update_fields=['stamps'])

        # Помечаем код как использованный
        code.redeemed = True
        code.redeemed_at = timezone.now()
        # redeemed_by заполняется в view, если нужно
        code.save(update_fields=['redeemed', 'redeemed_at'])

        # Запись в историю
        LoyaltyStamp.objects.create(
            user=code.user,
            source="code",
            created_by=None  # или передать пользователя, если активировал бариста
        )

        profile.refresh_from_db()

        return True, {
            "detail": "Штамп успешно начислен",
            "stamps": profile.stamps,
            "max_stamps": max_stamps,
            "username": code.user.username
        }

    @staticmethod
    def get_user_loyalty_status(username):
        """Получить текущий статус лояльности по username"""
        User = get_user_model()
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None

        profile = LoyaltyService.get_or_create_profile(user)

        return {
            "username": user.username,
            "telegram_username": getattr(user, 'telegram_username', None),
            "stamps": profile.stamps,
            "max_stamps": getattr(settings, "LOYALTY_MAX_STAMPS", 6)
        }

    @staticmethod
    def get_user_stamp_history(user, limit=10):
        """История начисления штампов"""
        return LoyaltyStamp.objects.filter(user=user)\
                                   .order_by('-created_at')[:limit]
