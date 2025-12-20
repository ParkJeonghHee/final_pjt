from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    # 프로필 기본 정보
    nickname = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    # 포트폴리오 정보
    total_assets = models.BigIntegerField(null=True, blank=True)
    income = models.BigIntegerField(null=True, blank=True)

    # 가입한 상품 목록
    joined_products = models.ManyToManyField(
        "products.FinProduct",
        blank=True,
        related_name='joined_users',
    )