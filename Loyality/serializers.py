# Loyality/serializers.py

import re
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import LoyaltyProfile, LoyaltyCode, LoyaltyStamp

User = get_user_model()


# =============================================================================
# Базовые сериализаторы пользователя
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Полный сериализатор пользователя (для себя, админа)"""
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'name',
            'telegram_id',
            'telegram_username',         # ← обязательно
            'is_staff',
            'is_barista',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserPublicSerializer(serializers.ModelSerializer):
    """Короткий публичный сериализатор (для списков, чужих профилей, барист)"""
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'telegram_username',         # ← добавлено, важно для поиска по TG
            'is_staff',
        ]
        read_only_fields = fields


# =============================================================================
# Лояльность
# =============================================================================

class LoyaltyProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = LoyaltyProfile
        fields = ['id', 'user', 'stamps', 'updated_at']
        read_only_fields = ['id', 'user', 'updated_at']


# =============================================================================
# Регистрация и аутентификация
# =============================================================================

class RegisterSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'employee_code')
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data.pop("employee_code", None)
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=4)


class BaristaTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        data["is_staff"] = bool(user.is_staff)
        if user.is_staff:
            if hasattr(user, "name"):
                data["name"] = user.name
            if hasattr(user, "employee_code"):
                data["employee_code"] = user.employee_code

        return data


# =============================================================================
# Профиль пользователя (PATCH/GET)
# =============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    recent_orders = serializers.JSONField(read_only=True, required=False)

    stamps = serializers.SerializerMethodField()
    max_stamps = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "phone",
            "recent_orders",
            "stamps",
            "max_stamps",
            "telegram_username",      # ← добавлено для совместимости
        ]
        extra_kwargs = {"username": {"read_only": True}}

    def get_stamps(self, obj):
        profile, _ = LoyaltyProfile.objects.get_or_create(user=obj)
        return int(profile.stamps or 0)

    def get_max_stamps(self, obj):
        return int(getattr(settings, "LOYALTY_MAX_STAMPS", 6))

    def validate_phone(self, value):
        if not value:
            return ""
        if not re.fullmatch(r"[0-9+()\- \s]{6,32}", value):
            raise serializers.ValidationError("Некорректный номер телефона.")
        return value

    def update(self, instance, validated_data):
        for field in ("name", "phone"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


# =============================================================================
# Короткий "me" с расширенной статистикой
# =============================================================================

class MeSerializer(serializers.ModelSerializer):
    stamps = serializers.SerializerMethodField()
    max_stamps = serializers.SerializerMethodField()
    codes_activated = serializers.SerializerMethodField()
    stamps_today = serializers.SerializerMethodField()
    stamps_week = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "is_staff",
            "is_barista",
            "stamps",
            "max_stamps",
            "codes_activated",
            "stamps_today",
            "stamps_week",
            "telegram_username",           # ← добавлено
        )

    def get_stamps(self, obj):
        profile, _ = LoyaltyProfile.objects.get_or_create(user=obj)
        return int(profile.stamps or 0)

    def get_max_stamps(self, obj):
        return int(getattr(settings, "LOYALTY_MAX_STAMPS", 6))

    def get_codes_activated(self, obj):
        # Если есть redeemed_by — используйте его
        return LoyaltyCode.objects.filter(redeemed=True, redeemed_by=obj).count()

    def get_stamps_today(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return LoyaltyStamp.objects.filter(
            created_at__date=today,
            created_by=obj
        ).count()

    def get_stamps_week(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        return LoyaltyStamp.objects.filter(
            created_at__gte=week_ago,
            created_by=obj
        ).count()


# Для обратной совместимости (если где-то используется старое имя)
UserProfilePatchSerializer = UserProfileSerializer
