from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

BASE_URL = "https://finlife.fss.or.kr/finlifeapi/"
LOAN_ENDPOINTS = {
    "mortgage": "mortgageLoanProductsSearch.json",
    "renthouse": "rentHouseLoanProductsSearch.json",
}


def parse_rate(value):
    if value is None:
        return None
    if isinstance(value, str):
        raw = value.strip()
        if raw in ("", "-"):
            return None
        raw = raw.replace("%", "").replace(",", "")
        try:
            return float(raw)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_prdt_type(option):
    for key in ("prdt_type_nm", "prdt_type", "lend_rate_type_nm"):
        val = option.get(key)
        if val:
            return str(val)
    return ""


def is_online_join(join_way):
    text = str(join_way or "").lower()
    return any(key in text for key in ["인터넷", "모바일", "스마트", "online", "app", "비대면"])


def fetch_loan_products(category):
    endpoint = LOAN_ENDPOINTS.get(category)
    if not endpoint:
        raise ValueError("invalid category")

    params = {
        "auth": settings.FIN_API_KEY,
        "topFinGrpNo": "020000",
        "pageNo": 1,
    }

    res = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
    res.raise_for_status()
    payload = res.json()
    result = payload.get("result", {})

    base_list = result.get("baseList", []) or []
    option_list = result.get("optionList", []) or []

    product_map = {}
    for base in base_list:
        fin_prdt_cd = base.get("fin_prdt_cd")
        if not fin_prdt_cd:
            continue
        product_map[fin_prdt_cd] = {
            "fin_prdt_cd": fin_prdt_cd,
            "kor_co_nm": base.get("kor_co_nm", ""),
            "fin_prdt_nm": base.get("fin_prdt_nm", ""),
            "join_way": base.get("join_way", ""),
            "loan_category": category,
            "options": [],
        }

    for opt in option_list:
        fin_prdt_cd = opt.get("fin_prdt_cd")
        if fin_prdt_cd in product_map:
            product_map[fin_prdt_cd]["options"].append(opt)

    normalized = []
    for product in product_map.values():
        options = product["options"]

        mins = []
        maxs = []
        avgs = []
        prdt_types = []

        for opt in options:
            min_rate = parse_rate(opt.get("lend_rate_min"))
            max_rate = parse_rate(opt.get("lend_rate_max"))
            avg_rate = parse_rate(opt.get("lend_rate_avg"))

            if min_rate is not None:
                mins.append(min_rate)
            if max_rate is not None:
                maxs.append(max_rate)
            if avg_rate is not None:
                avgs.append(avg_rate)

            prdt_type = normalize_prdt_type(opt)
            if prdt_type:
                prdt_types.append(prdt_type)

        product["lend_rate_min"] = min(mins) if mins else None
        product["lend_rate_max"] = max(maxs) if maxs else None
        product["lend_rate_avg"] = sum(avgs) / len(avgs) if avgs else None
        product["prdt_type"] = "/".join(sorted(set(prdt_types))) if prdt_types else ""

        normalized.append(product)

    return normalized


class LoanProductListView(APIView):
    def get(self, request):
        category = request.GET.get("category", "mortgage").lower()
        if category not in LOAN_ENDPOINTS:
            return Response({"detail": "invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            items = fetch_loan_products(category)
        except requests.RequestException:
            return Response({"detail": "failed to fetch loan products"}, status=status.HTTP_502_BAD_GATEWAY)

        bank = request.GET.get("bank")
        q = request.GET.get("q")
        prdt_type = request.GET.get("prdt_type")
        join_way = request.GET.get("join_way")

        if bank and bank != "전체":
            items = [p for p in items if p.get("kor_co_nm") == bank]

        if q:
            items = [p for p in items if q.lower() in str(p.get("fin_prdt_nm", "")).lower()]

        if prdt_type:
            items = [p for p in items if prdt_type in str(p.get("prdt_type", ""))]

        if join_way == "online":
            items = [p for p in items if is_online_join(p.get("join_way"))]
        elif join_way == "offline":
            items = [p for p in items if p.get("join_way") and not is_online_join(p.get("join_way"))]

        return Response(items, status=status.HTTP_200_OK)


class LoanProductDetailView(APIView):
    def get(self, request, fin_prdt_cd):
        category = request.GET.get("category", "mortgage").lower()
        if category not in LOAN_ENDPOINTS:
            return Response({"detail": "invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            items = fetch_loan_products(category)
        except requests.RequestException:
            return Response({"detail": "failed to fetch loan products"}, status=status.HTTP_502_BAD_GATEWAY)

        product = next((p for p in items if p.get("fin_prdt_cd") == fin_prdt_cd), None)
        if not product:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(product, status=status.HTTP_200_OK)


def get_min_rate(product):
    direct = parse_rate(product.get("lend_rate_min"))
    if direct is not None:
        return direct

    options = product.get("options") or []
    mins = []
    for opt in options:
        rate = parse_rate(opt.get("lend_rate_min"))
        if rate is not None:
            mins.append(rate)
    return min(mins) if mins else None


class LoanRecommendView(APIView):
    def post(self, request):
        all_items = []

        for category in LOAN_ENDPOINTS.keys():
            try:
                items = fetch_loan_products(category)
            except requests.RequestException:
                continue

            for p in items:
                min_rate = get_min_rate(p)
                if min_rate is None:
                    continue
                all_items.append({
                    "fin_prdt_cd": p.get("fin_prdt_cd"),
                    "fin_prdt_nm": p.get("fin_prdt_nm"),
                    "kor_co_nm": p.get("kor_co_nm"),
                    "category": category,
                    "min_rate": min_rate,
                    "max_rate": parse_rate(p.get("lend_rate_max")),
                })

        if not all_items:
            return Response({
                "recommended": [],
                "summary": "추천 가능한 대출상품이 없습니다."
            }, status=status.HTTP_200_OK)

        all_items.sort(key=lambda x: (x["min_rate"], x["max_rate"] or float("inf")))
        picked = all_items[:3]

        recommended = []
        for item in picked:
            label = "주택담보대출" if item["category"] == "mortgage" else "전세자금대출"
            reason = (
                f"{label} 상품 중 최저 금리가 낮은 상품입니다. "
                f"현재 최저 금리는 {item['min_rate']:.2f}% 수준입니다."
            )
            recommended.append({
                "fin_prdt_cd": item["fin_prdt_cd"],
                "name": item["fin_prdt_nm"],
                "bank": item["kor_co_nm"],
                "category": item["category"],
                "reason": reason,
            })

        return Response({
            "recommended": recommended,
            "summary": "금리 기준으로 대출상품을 추천했습니다."
        }, status=status.HTTP_200_OK)
