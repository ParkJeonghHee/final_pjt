from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .gms_client import gms_chat_completion
from products.services.recommendation import build_candidates, pick_top

from .models import ChatMessage


def _format_candidates_for_prompt(top_list):
    """
    GPT에게 줄 후보 상품 목록 문자열.
    반드시 이 리스트 안에서만 고르도록 강제할 거라, 짧고 명확하게 준다.
    """
    lines = []
    for i, p in enumerate(top_list, start=1):
        # pick_top 반환 dict 기준
        lines.append(
            f"{i}. id={p['id']} | 은행={p['bank']} | 상품명={p['name']} | "
            f"최고우대금리={p['max_rate2']}% | 기본금리={p['max_rate']}%"
        )
    return "\n".join(lines)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    POST /api/chat/
    body:
    {
      "message": "사용자 입력",
      "history": [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
    }
    """
    message = (request.data.get("message") or "").strip()
    history = request.data.get("history") or []

    if not message:
        return Response({"ok": False, "reply": "메시지를 입력해 주세요."}, status=200)

    # 1) DB 기반 추천 후보 계산 (통제 영역)
    try:
        priority_type, candidates_qs = build_candidates(request.user, limit=30)
        top_products = pick_top(candidates_qs, top_k=3)  # dict list
    except Exception as e:
        # DB 추천 계산이 깨져도 챗봇은 최소한 동작하게
        priority_type = None
        top_products = []
        db_error = str(e)
    else:
        db_error = None

    # 후보가 없으면: 가이드만 + 안내문
    # 후보가 있으면: 가이드 + 실제상품 추천(후보 안에서만)

    # 2) GPT 프롬프트 구성

    # 유저 프로필(프롬프트에 넣어 대화 품질 올리기)
    u = request.user
    user_profile_text = (
        f"- 나이: {getattr(u, 'age', None)}\n"
        f"- 월소득: {getattr(u, 'income', None)}\n"
        f"- 총자산: {getattr(u, 'total_assets', None)}\n"
    )

    if top_products:
        candidates_text = _format_candidates_for_prompt(top_products)

        system_msg = {
            "role": "developer",
            "content": (
                "너는 Bankbook 서비스의 금융 상담 챗봇이다. 반드시 한국어로 답변한다.\n\n"

                "답변은 금융 상담사가 실제로 말하듯 자연스럽게 이어지는 설명형 문장으로 작성한다.\n"
                "형식적인 번호, 제목, 구분선([1], [2], 일반 가이드 등)은 절대 사용하지 않는다.\n\n"

                "답변 구성 원칙:\n"
                "- 먼저 사용자의 상황(직장인, 안정성, 원금 보장 등)을 1문장으로 간단히 요약한다.\n"
                "- 이어서 금융상품 선택 시 고려할 핵심 기준만 4~5문장 이내로 간결하게 설명한다.\n"
                "  (예: 예금/적금 선택, 만기 분산, 우대금리 조건, 중도해지 유의점, 예금자보호, 세후 수익)\n"
                "- 사용자가 대출을 요청한 경우에는 예금/적금 대신 대출 선택 기준을 3~5문장으로 설명한다.\n"
                "  (예: 고정/변동금리, LTV·DSR, 상환방식, 중도상환수수료, 비대면/영업점 가입)\n"
                "- 그 다음 문장에서 반드시 '이런 기준으로 보면' 또는 '이를 바탕으로 살펴보면'이라는 표현으로\n"
                "  자연스럽게 연결하여, 우리 서비스에 실제로 있는 상품을 추천한다.\n\n"

                "상품 추천 작성 규칙:\n"
                "- 아래 제공된 '후보 상품 목록' 안에서만 1~3개를 선택한다. (목록 밖 상품 언급 금지)\n"
                "- 여러 상품을 추천하는 경우, 각 상품 문단의 맨 앞에 반드시 구분 기호를 붙인다.\n"
                "  (예: '•', '-', '▶' 중 하나를 사용)\n"
                "- 각 상품은 줄바꿈하여 문단으로 구분해 한눈에 읽히게 작성한다.\n"
                "- 각 상품 문단에는 다음만 포함한다:\n"
                "  · 은행명 + 상품명 (첫 줄에서 명확히)\n"
                "  · 이 사용자에게 왜 적합한지 2~3문장으로 자세하지만 과하지 않게 설명\n"
                "  · 최고우대금리 수치만 숫자로 제시\n"
                "- '상세보기', '링크', URL 경로(/products/...)는 절대 언급하지 않는다.\n"
                "- 추천 기준은 '이미 가입한 상품을 제외하고, 우대금리 상위 후보군을 중심으로 선택했다'는 점을\n"
                "  문장 속에 자연스럽게 녹여 설명한다.\n\n"

                "대출 요청 처리 규칙:\n"
                "- 대출 상품은 후보 목록에 포함되어 있지 않으므로 특정 대출상품명 추천은 하지 않는다.\n"
                "- 대신 주택담보대출/전세자금대출 중 어떤 유형이 적합한지와 선택 기준을 설명하고,\n"
                "  필요한 조건(주택 보유 여부, 전세 여부, 희망 금리 유형, 상환방식)을 1~2문장으로 질문한다.\n\n"

                "마지막 문장에서는 사용자의 예치금액이나 희망 만기 등 추가 정보를 한 가지 질문으로 물어보며 대화를 이어간다.\n\n"

                f"사용자 정보:\n{user_profile_text}\n"
                f"우선순위 상품유형(알고리즘 결과): {priority_type}\n\n"
                "후보 상품 목록(이 안에서만 선택):\n"
                f"{candidates_text}\n"
            )
        }


    else:
        system_msg = {
            "role": "developer",
            "content": (
                "너는 Bankbook 서비스의 금융 챗봇이다. 반드시 한국어로 답변한다.\n"
                "사용자의 상황을 1~2문장으로 요약한 뒤,\n"
                "예금/적금 선택 기준, 기간 선택, 우대조건 확인, 중도해지/유동성, 예금자보호 등을\n"
                "5~8문장으로 설명하고, 마지막에 질문 1개를 반드시 한다.\n"
                "사용자가 대출을 요청하면 예금/적금 대신 대출 선택 기준(고정/변동, LTV·DSR, 상환방식, "
                "중도상환수수료, 가입채널)을 4~6문장으로 설명하고 질문 1개를 한다.\n\n"
                "추가로, 우리 서비스 DB에서 조건에 맞는 추천 상품이 없을 수 있음을 안내하라.\n"
                f"사용자 정보:\n{user_profile_text}\n"
            )
        }

    messages = [system_msg]

    # 3) 기존 대화 히스토리 이어붙이기
    for h in history:
        role = h.get("role")
        content = h.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()})

    messages.append({"role": "user", "content": message})

    # 4) GPT 호출
    try:
        data = gms_chat_completion(messages, model="gpt-5-nano")
        reply = data["choices"][0]["message"]["content"]

        if db_error and not top_products:
            reply += "\n\n(참고) DB 추천 후보 계산 중 오류가 발생했습니다. 추천 기능 설정을 확인해주세요."

        return Response({"ok": True, "reply": reply}, status=200)

    except Exception as e:
        if top_products:
            fallback = []
            fallback.append("[1] 일반 가이드")
            fallback.append(
                "안정성을 중시한다면 정기예금/적금 중 예금 비중을 높이고, 만기를 6개월/12개월로 분산해 리스크를 줄이는 것이 좋습니다. "
                "우대금리는 조건(급여이체/자동이체/카드실적 등)을 달성해야 반영되므로 본인 생활패턴에서 달성 가능한 조건인지 먼저 확인하세요. "
                "중도해지 가능성과 비상자금 규모를 고려해 유동성을 확보하면 선택이 쉬워집니다.\n"
                "추가 질문: 목표 만기(예: 6개월/1년/2년)와 중도해지 가능성이 어느 정도인가요?"
            )

            fallback.append("\n[2] 우리 서비스에 실제로 있는 상품 추천(DB 기반)")
            for p in top_products:
                fallback.append(
                    f"- {p['bank']} - {p['name']}\n"
                    f"  이유: 가입한 상품을 제외하고 우대금리 상위 후보군에서 선별되었습니다. "
                    f"  우대조건 달성 가능성이 있다면 안정적 운용에서 수익을 조금 더 끌어올릴 수 있습니다.\n"
                    f"  최고우대금리: {p['max_rate2']}%\n"
                    f"  상세보기: /products/{p['id']}"
                )

            return Response({"ok": True, "reply": "\n".join(fallback)}, status=200)

        return Response({
            "ok": False,
            "reply": "현재 챗봇 응답 생성에 실패했습니다. 잠시 후 다시 시도해주세요.",
            "error": str(e),
        }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def history(request):
    qs = ChatMessage.objects.filter(user=request.user).order_by("created_at")
    data = [{"role": m.role, "content": m.content} for m in qs]
    return Response({"ok": True, "history": data}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return Response({"ok": True}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    message = (request.data.get("message") or "").strip()
    if not message:
        return Response({"ok": False, "reply": "메시지를 입력해 주세요."}, status=200)

    N = 20
    prev = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:N]
    prev = list(reversed(prev))

    messages = [
        {
            "role": "developer",
            "content": (
                "너는 Bankbook 서비스의 금융 상담 챗봇이다. 반드시 한국어로 답변한다. "
                "번호/제목/대괄호 형식 금지. 여러 추천이면 각 상품은 '•'로 시작. "
                "대출 문의에는 고정/변동금리, LTV·DSR, 상환방식, 중도상환수수료, "
                "비대면/영업점 가입 기준을 포함해 안내하고, 특정 대출상품명은 단정적으로 추천하지 않는다."
            )
        }
    ]
    for m in prev:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": message})

    try:
        data = gms_chat_completion(messages, model="gpt-5-nano")  
        reply = data["choices"][0]["message"]["content"].strip()

        ChatMessage.objects.create(user=request.user, role="user", content=message)
        ChatMessage.objects.create(user=request.user, role="assistant", content=reply)

        return Response({"ok": True, "reply": reply}, status=200)

    except Exception as e:
        return Response({
            "ok": False,
            "reply": "현재 챗봇 응답 생성에 실패했습니다. 잠시 후 다시 시도해주세요.",
            "error": str(e),
        }, status=200)
