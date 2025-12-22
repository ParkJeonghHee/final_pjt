import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny



class KakaoRouteAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")

        if not origin or not destination:
            return Response(
                {"detail": "origin, destination이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = os.environ.get("KAKAO_MOBILITY_KEY")
        if not key:
            return Response(
                {"detail": "KAKAO_MOBILITY_KEY가 서버 환경변수에 설정되어 있지 않습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        url = "https://apis-navi.kakaomobility.com/v1/directions"
        headers = {"Authorization": f"KakaoAK {key}"}
        params = {"origin": origin, "destination": destination, "priority": "RECOMMEND"}

        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
        except requests.RequestException as e:
            return Response(
                {"detail": "Kakao Mobility 요청 중 네트워크 오류", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not r.ok:
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
        except ValueError:
            return Response(
                {"detail": "Kakao Mobility 응답이 JSON이 아닙니다.", "body": r.text[:500]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        routes = data.get("routes") or []
        if not routes:
            return Response({"path": [], "distance": None, "duration": None}, status=status.HTTP_200_OK)

        route0 = routes[0] if isinstance(routes[0], dict) else {}
        sections = route0.get("sections") or []
        section0 = sections[0] if sections and isinstance(sections[0], dict) else {}

        roads = section0.get("roads") or []

        path = []
        for road in roads:
            if not isinstance(road, dict):
                continue
            v = road.get("vertexes") or []
            for i in range(0, len(v) - 1, 2):
                path.append({"x": v[i], "y": v[i + 1]})

        summary = section0.get("summary") or {}
        route_summary = route0.get("summary") or {}

        distance = summary.get("distance") or route_summary.get("distance")
        duration = summary.get("duration") or route_summary.get("duration")

        return Response(
            {"path": path, "distance": distance, "duration": duration},
            status=status.HTTP_200_OK,
        )
import os, requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

KAKAO_MOBILITY_KEY = os.environ.get("KAKAO_MOBILITY_KEY")

class KakaoRouteAPIView(APIView):
    def get(self, request):
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")

        if not origin or not destination:
            return Response({"detail": "origin, destination이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://apis-navi.kakaomobility.com/v1/directions"
        headers = {"Authorization": f"KakaoAK {KAKAO_MOBILITY_KEY}"}
        params = {"origin": origin, "destination": destination}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()

        routes = data.get("routes", [])
        if not routes:
            return Response({"path": [], "distance": None, "duration": None}, status=status.HTTP_200_OK)

        sections = routes[0].get("sections", [])
        roads = sections[0].get("roads", []) if sections else []

        path = []
        for road in roads:
          v = road.get("vertexes", [])
          for i in range(0, len(v), 2):
            path.append({"x": v[i], "y": v[i+1]})

        summary = sections[0].get("summary", {}) if sections else {}
        return Response({
          "path": path,
          "distance": summary.get("distance"),
          "duration": summary.get("duration"),
        }, status=status.HTTP_200_OK)
