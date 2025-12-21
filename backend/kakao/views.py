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
