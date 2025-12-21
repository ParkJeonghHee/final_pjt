from rest_framework import serializers
from .models import FinProduct, FinProductOption


class FinProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinProductOption
        fields = ["id",
                  "save_trm", 
                  "intr_rate_type_nm", 
                  "rsrv_type_nm", 
                  "intr_rate", 
                  "intr_rate2"]


class FinProductListSerializer(serializers.ModelSerializer):
    options = FinProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FinProduct
        fields = ["id", 
                  "product_type", 
                  "kor_co_nm", 
                  "fin_prdt_cd", 
                  "fin_prdt_nm", 
                  "options"]


class FinProductDetailSerializer(serializers.ModelSerializer):
    options = FinProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FinProduct
        fields = ["id", 
                  "product_type", 
                  "kor_co_nm", 
                  "fin_prdt_cd", 
                  "fin_prdt_nm", 
                  "options"]