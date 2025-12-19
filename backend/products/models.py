from django.db import models

# Create your models here.
class FinProduct(models.Model):
    class ProductType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "예금"
        SAVING = "SAVING", "적금"
    
    product_type = models.CharField(max_length=10, choices=ProductType.choices)

    kor_co_nm = models.CharField(max_length=100)    # 금융회사명
    fin_prdt_nm = models.CharField(max_length=200)  # 상품명
    fin_prdt_cd = models.CharField(max_length=50)   # 상품코드 (고유키 역할)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["product_type", "fin_prdt_cd"],
                name="unique_producttype_finprdtcd"
            )
        ]
    
    def __str__(self):
        return f"[{self.product_type}] {self.kor_co_nm} - {self.fin_prdt_nm}"
    
class FinProductOption(models.Model):
    product = models.ForeignKey(FinProduct, on_delete=models.CASCADE, related_name="options")

    fin_prdt_cd = models.CharField(max_length=50)
    save_trm = models.PositiveIntegerField(null=True, blank=True)   # 기간 (개월)
    intr_rate_type_nm = models.CharField(max_length=50, null=True, blank=True)  # 금리 유형명
    intr_rate = models.FloatField(null=True, blank=True)    # 기본 금리
    intr_rate2 = models.FloatField(null=True, blank=True)   # 우대 금리

    rsrv_type_nm = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["product", "save_trm", "intr_rate", "intr_rate2", "rsrv_type_nm"],
                name="unique_option_per_product"
            )
        ]

    def __str__(self):
        return f"{self.product.fin_prdt_nm} / {self.save_trm}m"