from django.shortcuts import render

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import FinProduct, FinProductOption

# Create your views here.

DEPOSIT_URL = "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
SAVING_URL  = "https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"


class ProductSyncView(APIView):
    def post(self, request):
        api_key = settings.FIN_API_KEY

        created_products = 0
        created_options = 0

        for product_type, url in [("DEPOSIT", DEPOSIT_URL), ("SAVING", SAVING_URL),]:
            params = {
                "auth": api_key,
                "topFinGrpNo": "020000",
                "pageNo": 1,
            }

            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            payload = r.json()

            result = payload.get("result", {})
            base_list = result.get("baseList", [])
            option_list = result.get("optionList", [])

            product_map = {}

            # baseList 저장(상품)
            for b in base_list:
                fin_prdt_cd = b.get("fin_prdt_cd")
                if not fin_prdt_cd:
                    continue

                obj, created = FinProduct.objects.get_or_create(
                    product_type=product_type,
                    fin_prdt_cd=fin_prdt_cd,
                    defaults={
                        "kor_co_nm": b.get("kor_co_nm", ""),
                        "fin_prdt_nm": b.get("fin_prdt_nm", ""),
                    }
                )

                # 이미 있으면 회사/상품명 최신값으로 업데이트
                if not created:
                    new_kor = b.get("kor_co_nm", obj.kor_co_nm)
                    new_nm = b.get("fin_prdt_nm", obj.fin_prdt_nm)
                    if obj.kor_co_nm != new_kor or obj.fin_prdt_nm != new_nm:
                        obj.kor_co_nm = new_kor
                        obj.fin_prdt_nm = new_nm
                        obj.save()

                if created:
                    created_products += 1

                product_map[fin_prdt_cd] = obj

            # optionList 저장(옵션)
            for o in option_list:
                fin_prdt_cd = o.get("fin_prdt_cd")
                product = product_map.get(fin_prdt_cd)
                if not product:
                    continue

                save_trm_raw = o.get("save_trm")
                save_trm = int(save_trm_raw) if str(save_trm_raw).isdigit() else None

                _, created = FinProductOption.objects.get_or_create(
                    product=product,
                    save_trm=save_trm,
                    intr_rate_type_nm=o.get("intr_rate_type_nm"),
                    rsrv_type_nm=o.get("rsrv_type_nm"),    # 적금일 때만 값 있음
                    intr_rate=o.get("intr_rate"),
                    intr_rate2=o.get("intr_rate2"),
                )

                if created:
                    created_options += 1

        return Response(
            {
                "message": "sync success",
                "created_products": created_products,
                "created_options": created_options,
            },
            status=status.HTTP_200_OK
        )
