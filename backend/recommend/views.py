# recommend/views.py

import json
from django.db.models import Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openai import OpenAI

from products.models import FinProduct, FinProductOption

client = OpenAI()  # OPENAI_API_KEY 환경변수 사용


# ---------------- utils ----------------
def normalize_joined_ids(raw):
    if raw is None:
        return []
    if hasattr(raw, "values_list"):
        return list(raw.values_list("id", flat=True))
    if isinstance(raw, list):
        out = []
        for x in raw:
            if isinstance(x, int):
                out.append(x)
            elif isinstance(x, str) and x.isdigit():
                out.append(int(x))
            elif isinstance(x, dict) and "id" in x:
                try:
                    out.append(int(x["id"]))
                except:
                    pass
        return out
    return []


def pick_product_type(age, income, total_assets):
    # 기본: 예금
    if age is None or income is None or total_assets is None:
        return FinProduct.ProductType.DEPOSIT

    try:
        age_i = int(age)
        income_i = int(income)
        assets_i = int(total_assets)
    except:
        return FinProduct.ProductType.DEPOSIT

    # age <= 29 & income >= 250만 & total_assets >= 1000만 → 적금 고려
    if age_i <= 29 and income_i >= 2_500_000 and assets_i >= 10_000_000:
        return FinProduct.ProductType.SAVING

    return FinProduct.ProductType.DEPOSIT


def build_top30_candidates(joined_ids, target_type, limit=30):
    base_qs = FinProduct.objects.exclude(id__in=joined_ids).filter(product_type=target_type)

    agg = (
        FinProductOption.objects
        .filter(product__in=base_qs)
        .values("product_id")
        .annotate(max_intr_rate2=Max("intr_rate2"))
        .order_by("-max_intr_rate2")[:limit]
    )

    top_ids = [row["product_id"] for row in agg if row.get("product_id") is not None]

    if not top_ids:
        fallback = list(base_qs.values("id", "product_type", "kor_co_nm", "fin_prdt_nm")[:limit])
        return fallback

    products = list(
        FinProduct.objects.filter(id__in=top_ids)
        .values("id", "product_type", "kor_co_nm", "fin_prdt_nm")
    )
    pmap = {p["id"]: p for p in products}
    candidates = [pmap[i] for i in top_ids if i in pmap]

    rate_map = {row["product_id"]: float(row["max_intr_rate2"] or 0) for row in agg}
    for c in candidates:
        c["max_intr_rate2"] = rate_map.get(c["id"], 0)

    return candidates


def strengthen_reason_if_too_short(reason: str, product_name: str, target_type: str) -> str:
    """
    OpenAI가 가끔 reason을 너무 짧게 주는 경우가 있어서,
    최소 2~3문장 느낌으로 서버에서 보강하는 안전장치.
    """
    r = (reason or "").strip()
    if len(r) >= 60:
        return r

    # 짧으면 템플릿으로 확장
    return (
        f"{r} "
        f"이 상품({product_name})은(는) 현재 조건에서 우선 추천되는 {target_type} 유형이며, "
        f"금리 수준과 안정성을 함께 고려했을 때 무난한 선택입니다. "
        f"특히 가입하지 않은 상품 중에서 후보군 상위에 있는 상품이라 비교 우선순위가 높습니다."
    ).strip()


# ---------------- main view ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_product(request):
    user = request.user
    profile = getattr(user, "profile", None)

    age = getattr(profile, "age", None)
    income = getattr(profile, "income", None)
    total_assets = getattr(profile, "total_assets", None)

    joined_raw = getattr(profile, "joined_products", [])
    joined_ids = normalize_joined_ids(joined_raw)

    # Step 1) 우선순위 결정
    target_type = pick_product_type(age, income, total_assets)

    # Step 2) 후보군 축소 (intr_rate2 최대값 기준 상위 30개)
    candidates = build_top30_candidates(joined_ids, target_type, limit=30)

    if not candidates:
        return Response({
            "recommended": [],
            "summary": "추천 가능한 미가입 상품이 없습니다. (이미 대부분 가입했거나 DB 데이터가 부족합니다.)"
        }, status=200)

    payload = {
        "user_profile": {
            "age": age,
            "income": income,
            "total_assets": total_assets,
            "joined_products": joined_ids,
        },
        "algorithm": {
            "priority": "기본은 예금(DEPOSIT). 단, age<=29 & income>=250만 & total_assets>=1000만이면 적금(SAVING) 고려",
            "candidate_filter": "미가입 제외 + 선택 상품종류만 + 옵션 intr_rate2 최대값 계산 + 우대금리 상위 30개 후보",
            "recommend_count": "1~3개",
            "fallback": "추천 불가 시 summary에 대체 문구"
        },
        "candidates": candidates
    }

    # ✅ 변경 1) reason 길게(최소 2~3문장) + 근거 2개 이상 강제
    system = (
        "너는 금융상품 추천 도우미다. "
        "반드시 candidates 목록 안에서만 1~3개를 추천해야 한다. "
        "각 추천의 reason은 최소 2~3문장으로 작성하고, "
        "아래 근거 중 최소 2가지 이상을 포함해 구체적으로 설명하라: "
        "(1) 금리/우대금리 수준, (2) 안정성(원금 손실 위험 낮음), (3) 사용자 정보(나이/소득/자산) 적합성, "
        "(4) 후보군 상위(우대금리 상위 30개)라는 점. "
        "출력은 반드시 아래 JSON 하나로만 하라.\n"
        "{"
        "\"recommended\": [{\"id\": 0, \"name\": \"상품명\", \"reason\": \"추천 이유\"}], "
        "\"summary\": \"요약/대체문구\""
        "}"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw = completion.choices[0].message.content
        data = json.loads(raw)

    except Exception as e:
        return Response({
            "recommended": [],
            "summary": f"OpenAI 추천 생성 중 오류가 발생했습니다. ({type(e).__name__}: {str(e)})"
        }, status=200)

    recommended = data.get("recommended") or []
    summary = data.get("summary") or ""

    if len(recommended) == 0:
        if not summary:
            summary = "현재 정보로는 추천이 어렵습니다. 소득/자산/나이 정보를 입력해 주세요."
        return Response({"recommended": [], "summary": summary}, status=200)

    cleaned = []
    for r in recommended:
        try:
            pid = int(r.get("id"))
            name = str(r.get("name") or "").strip()
            reason = str(r.get("reason") or "").strip()

            if pid and name and reason:
                # ✅ 변경 2) 혹시 reason이 짧으면 서버에서 자동 보강
                reason = strengthen_reason_if_too_short(reason, name, target_type)
                cleaned.append({"id": pid, "name": name, "reason": reason})
        except:
            continue

    if len(cleaned) == 0:
        return Response({
            "recommended": [],
            "summary": "추천 결과 파싱에 실패했습니다. 다시 시도해 주세요."
        }, status=200)

    if not summary:
        summary = f"미가입 {target_type} 상품 중 우대금리 상위 30개 후보에서 추천했습니다."

    return Response({"recommended": cleaned, "summary": summary}, status=200)
