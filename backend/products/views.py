from django.shortcuts import get_object_or_404

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import FinProduct, FinProductOption
from .serializers import FinProductListSerializer, FinProductDetailSerializer

from django.db.models import Prefetch, Max
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

DEPOSIT_URL = "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
SAVING_URL  = "https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"


class ProductSyncView(APIView):
    def post(self, request):
        created_products, created_options = sync_products()

        return Response(
            {
                "message": "sync success",
                "created_products": created_products,
                "created_options": created_options,
            },
            status=status.HTTP_200_OK,
        )


def sync_products():
    """Fetch products from external API and save to DB.

    Returns: (created_products, created_options)
    """
    api_key = settings.FIN_API_KEY

    created_products = 0
    created_options = 0

    for product_type, url in [("DEPOSIT", DEPOSIT_URL), ("SAVING", SAVING_URL)]:
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
                },
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
                rsrv_type_nm=o.get("rsrv_type_nm"),  # 적금일 때만 값 있음
                intr_rate=o.get("intr_rate"),
                intr_rate2=o.get("intr_rate2"),
            )

            if created:
                created_options += 1

    return created_products, created_options


class DepositListView(APIView):
    def get(self, request):
        # If DB empty, sync first
        if not FinProduct.objects.exists():
            try:
                sync_products()
            except Exception:
                pass
        bank = request.GET.get("bank")
        term = request.GET.get("term")
        q = request.GET.get("q")
        sort = request.GET.get("sort")

        qs = FinProduct.objects.filter(product_type="DEPOSIT")

        if bank and bank != '전체':
            qs = qs.filter(kor_co_nm = bank)
        
        if q:
            qs = qs.filter(fin_prdt_nm__icontains=q)

        if term:
            if term.isdigit():
                term = int(term)

            qs = qs.filter(options__save_trm=term).distinct()

        serializer = FinProductListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SavingListView(APIView):
    def get(self, request):
        # If DB empty, sync first
        if not FinProduct.objects.exists():
            try:
                sync_products()
            except Exception:
                pass
        bank = request.GET.get("bank")
        term = request.GET.get("term")
        q = request.GET.get("q")

        qs = FinProduct.objects.filter(product_type="SAVING")

        if bank and bank != "전체":
            qs = qs.filter(kor_co_nm = bank)
        
        if q:
            qs = qs.filter(fin_prdt_nm__icontains=q)
        
        if term:
            if term.isdigit():
                term = int(term)
            qs = qs.filter(options__save_trm=term).distinct()

        serializer = FinProductListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # If DB empty, sync first
        if not FinProduct.objects.exists():
            try:
                sync_products()
            except Exception:
                pass
        ptype = request.GET.get("type")          # DEPOSIT / SAVING
        bank = request.GET.get("bank")           # 은행명
        term = request.GET.get("term")           # 6/12/24/36
        q = request.GET.get("q")                 # 검색어(상품명)
        sort = request.GET.get("sort")           # rate2 / rate / name

        qs = FinProduct.objects.all()

        if ptype in ["DEPOSIT", "SAVING"]:
            qs = qs.filter(product_type=ptype)

        if bank and bank != "전체":
            qs = qs.filter(kor_co_nm=bank)

        if q:
            qs = qs.filter(fin_prdt_nm__icontains=q)

        if term and str(term).isdigit():
            qs = qs.filter(options__save_trm=int(term)).distinct()

        if sort == "rate2":
            qs = qs.annotate(max_rate2=Max("options__intr_rate2")).order_by("-max_rate2", "kor_co_nm", "fin_prdt_nm")
        elif sort == "rate":
            qs = qs.annotate(max_rate=Max("options__intr_rate")).order_by("-max_rate", "kor_co_nm", "fin_prdt_nm")
        elif sort == "name":
            qs = qs.order_by("fin_prdt_nm")
        else:
            qs = qs.order_by("kor_co_nm", "fin_prdt_nm")

        qs = qs.prefetch_related("options")

        serializer = FinProductListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(
            FinProduct.objects.prefetch_related('options'),
            pk=pk
        )

        data = FinProductDetailSerializer(product).data

        if request.user.is_authenticated:
            data["is_joined"] = request.user.joined_products.filter(pk=product.pk).exists()
        else:
            data["is_joined"] = False

        return Response(data, status=status.HTTP_200_OK)


class BankListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # If DB empty, sync first
        if not FinProduct.objects.exists():
            try:
                sync_products()
            except Exception:
                pass
        ptype = request.GET.get("type")  # DEPOSIT/SAVING(선택)
        qs = FinProduct.objects.all()
        if ptype in ["DEPOSIT", "SAVING"]:
            qs = qs.filter(product_type=ptype)

        banks = qs.values_list("kor_co_nm", flat=True).distinct().order_by("kor_co_nm")
        return Response(["전체"] + list(banks), status=status.HTTP_200_OK)


class ProductJoinView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(FinProduct, pk=pk)

        if request.user.joined_products.filter(id=product.id).exists():
            return Response({"message": "already joined"}, status=status.HTTP_200_OK)

        request.user.joined_products.add(product)
        return Response({"message": "joined", "product_id": product.id}, status=status.HTTP_201_CREATED)