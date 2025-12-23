import os
import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


class KakaoRouteAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")
        priority = request.query_params.get("priority", "RECOMMEND")  # 경로 옵션

        logger.info(f"[KakaoRoute] 요청: origin={origin}, destination={destination}, priority={priority}")

        if not origin or not destination:
            return Response(
                {"detail": "origin, destination이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # priority 값 검증 (카카오 Mobility API 지원 값)
        valid_priorities = ["RECOMMEND", "HIGH_SPEED", "MIN_TIME", "MIN_DISTANCE"]
        if priority not in valid_priorities:
            priority = "RECOMMEND"

        key = os.environ.get("KAKAO_MOBILITY_KEY")
        if not key:
            logger.error("[KakaoRoute] KAKAO_MOBILITY_KEY가 설정되지 않음")
            return Response(
                {"detail": "KAKAO_MOBILITY_KEY가 서버 환경변수에 설정되어 있지 않습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        url = "https://apis-navi.kakaomobility.com/v1/directions"
        headers = {"Authorization": f"KakaoAK {key}"}
        params = {
            "origin": origin,
            "destination": destination,
            "priority": priority,
        }

        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
        except requests.RequestException as e:
            logger.error(f"[KakaoRoute] 네트워크 오류: {str(e)}")
            return Response(
                {"detail": "Kakao Mobility 요청 중 네트워크 오류", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # 특정 경우 Kakao Mobility가 'invalid priority'로 400 응답을 반환할 수 있음.
        # 이 경우 우선순위를 안전한 기본값으로 재시도한다.
        if r.status_code == 400:
            try:
                body = r.json()
                msg = body.get("msg") or body.get("message") or ""
            except Exception:
                msg = r.text or ""

            if "invalid priority" in msg.lower() or "invalid priority" in (r.text or "").lower():
                logger.warning(f"[KakaoRoute] invalid priority detected in request, retrying with RECOMMEND. raw_msg={msg}")
                # 재시도: priority를 RECOMMEND로 교체
                params_retry = params.copy()
                params_retry["priority"] = "RECOMMEND"
                try:
                    r_retry = requests.get(url, headers=headers, params=params_retry, timeout=10)
                    logger.info(f"[KakaoRoute] 재시도 응답 상태: {r_retry.status_code}")
                    r = r_retry
                except requests.RequestException as e:
                    logger.error(f"[KakaoRoute] 재시도 중 네트워크 오류: {str(e)}")
                    return Response(
                        {"detail": "Kakao Mobility 요청 재시도 중 네트워크 오류", "error": str(e)},
                        status=status.HTTP_502_BAD_GATEWAY,
                    )

        if not r.ok:
            logger.error(f"[KakaoRoute] API 오류: status={r.status_code}")
            return Response(
                {
                    "detail": "Kakao Mobility API 요청 실패",
                    "status_code": r.status_code,
                    "body": r.text[:500],
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            data = r.json()
        except ValueError as e:
            logger.error(f"[KakaoRoute] JSON 파싱 실패: {str(e)}")
            return Response(
                {"detail": "Kakao Mobility 응답이 JSON이 아닙니다.", "body": r.text[:500]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        routes = data.get("routes") or []
        if not routes:
            logger.warning(f"[KakaoRoute] 경로 없음 (routes가 비어있음)")
            return Response(
                {"path": [], "distance": None, "duration": None, "priority": priority},
                status=status.HTTP_200_OK,
            )

        route0 = routes[0] if isinstance(routes[0], dict) else {}
        sections = route0.get("sections") or []
        section0 = sections[0] if sections and isinstance(sections[0], dict) else {}

        roads = section0.get("roads") or []

        path = []
        for road in roads:
            if not isinstance(road, dict):
                continue
            v = road.get("vertexes") or []
            # ✅ 모든 좌표 포함 (len(v) - 1 제거)
            for i in range(0, len(v), 2):
                if i + 1 < len(v):  # 안전 체크
                    path.append({"x": v[i], "y": v[i + 1]})

        summary = section0.get("summary") or {}
        route_summary = route0.get("summary") or {}

        distance = summary.get("distance") or route_summary.get("distance")
        duration = summary.get("duration") or route_summary.get("duration")

        logger.info(f"[KakaoRoute] 응답: distance={distance}, duration={duration}, path_count={len(path)}")

        return Response(
            {
                "path": path,
                "distance": distance,
                "duration": duration,
                "priority": priority,
            },
            status=status.HTTP_200_OK,
        )
