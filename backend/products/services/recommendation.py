from django.db.models import Max
from products.models import FinProduct


def decide_priority_type(user):
    """
    상품 유형 우선순위 결정
    """
    if (
        user.age is not None
        and user.age <= 29
        and user.income is not None
        and user.income >= 250
        and user.total_assets is not None
        and user.total_assets >= 1000
    ):
        return "SAVING"
    return "DEPOSIT"


def build_candidates(user, limit=30):
    """
    1) 상품 유형 결정
    2) 가입 상품 제외
    3) 최고 우대금리 기준 후보군 추출
    """
    priority_type = decide_priority_type(user)

    joined_ids = user.joined_products.values_list("id", flat=True)

    qs = (
        FinProduct.objects
        .filter(product_type=priority_type)
        .exclude(id__in=joined_ids)
        .annotate(
            max_intr_rate2=Max("options__intr_rate2"),
            max_intr_rate=Max("options__intr_rate"),
        )
        .order_by("-max_intr_rate2", "-max_intr_rate")
    )

    return priority_type, qs[:limit]


def pick_top(candidates, top_k=3):
    """
    후보군 중 상위 N개 선택
    """
    result = []
    for p in candidates[:top_k]:
        result.append({
            "id": p.id,
            "name": p.fin_prdt_nm,
            "bank": p.kor_co_nm,
            "max_rate": p.max_intr_rate,
            "max_rate2": p.max_intr_rate2,
        })
    return result
