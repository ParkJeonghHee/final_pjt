from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime

# Create your views here.

ASSET_FILE = {
    "gold": "Gold_prices.xlsx",
    "silver": "Silver_prices.xlsx",
}

def parse_ymd(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()


class MetalSeriesAPIView(APIView):
    def get(self, request):
        asset = request.query_params.get("asset", "gold").lower()
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if asset not in ASSET_FILE:
            return Response(
                {"detail": "asset은 gold 또는 silver만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 날짜 파싱
        try:
            start_date = parse_ymd(start) if start else None
            end_date = parse_ymd(end) if end else None
        except ValueError:
            return Response(
                {"detail": "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # start > end
        if start_date and end_date and start_date > end_date:
            return Response(
                {"detail": "시작일이 종료일보다 이후일 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 엑셀 파일 로드
        file_path = settings.BASE_DIR / "data" / ASSET_FILE[asset]
        try:
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            return Response(
                {"detail": f'데이터 파일을 찾을 수 없습니다.: {file_path}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        required_cols = {"Date", "Close/Last"}
        if not required_cols.issubset(set(df.columns)):
            return Response(
                {"detail": "엑셀 컬럼이 예상과 다릅니다. (Date, Close/Last 필요)"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        df = df[["Date", "Close/Last"]].copy()
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

        df["Close/Last"] = (
            df["Close/Last"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df["Close/Last"] = pd.to_numeric(df["Close/Last"], errors="coerce")

        df = df.dropna(subset = ["Close/Last"])

        if start_date:
            df = df[df["Date"] >= start_date]
        if end_date:
            df = df[df["Date"] <= end_date]

        df = df.sort_values("Date")

        series = [
            {"date": d.isoformat(), "price": float(p)}
            for d, p in zip(df["Date"], df["Close/Last"])
        ]
        
        return Response(
            {
                "asset": asset,
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
                "count": len(series),
                "series": series,
            },
            status=status.HTTP_200_OK
        )