import time
import logging
from datetime import date, timedelta
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


ECOS_URL = "https://ecos.bok.or.kr/api/KeyStatisticList/{key}/json/kr/1/200"
ECOS_ITEM_URL = "https://ecos.bok.or.kr/api/StatisticItemList/{key}/json/kr/1/200/{stat_code}/{cycle}"
ECOS_SEARCH_URL = (
    "https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/200/"
    "{stat_code}/{cycle}/{start}/{end}/{item_code}"
)
_CACHE = {"ts": 0, "data": None}
_TTL = 600
_HISTORY_CACHE = {}
_HISTORY_TTL = 900
logger = logging.getLogger(__name__)


def _parse_value(row):
    for key in ("DATA_VALUE", "DATA_VALUE1", "DATA_VALUE2", "DATA_VALUE3", "DATA_VALUE4"):
        val = row.get(key)
        if val is None:
            continue
        try:
            return float(str(val).replace(",", ""))
        except ValueError:
            continue
    return None


def _row_text(row):
    parts = []
    for key in (
        "KEYSTAT_NAME",
        "STAT_NAME",
        "ITEM_NAME1",
        "ITEM_NAME2",
        "ITEM_NAME3",
        "ITEM_NAME4",
        "ITEM_NAME",
        "CLASS_NAME",
    ):
        val = row.get(key)
        if val:
            parts.append(str(val))
    return " ".join(parts).lower()


def _find_value(rows, patterns):
    for row in rows:
        text = _row_text(row)
        if any(p in text for p in patterns):
            value = _parse_value(row)
            if value is not None:
                return value
    return None


def _fetch_key_stats():
    api_key = getattr(settings, "BOK_API_KEY", "")
    if not api_key:
        logger.warning("BOK_API_KEY not set")
        return {"error": "BOK_API_KEY not set", "rows": []}

    url = ECOS_URL.format(key=api_key)
    logger.info("Fetching BOK ECOS key statistics")
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    payload = res.json()
    result = payload.get("RESULT")
    if result and result.get("CODE") not in (None, "INFO-000"):
        return {
            "error": f"{result.get('CODE')}: {result.get('MESSAGE')}",
            "rows": [],
            "result": result,
        }

    rows = payload.get("KeyStatisticList", {}).get("row", []) or []
    return {"rows": rows, "result": result}


def _fetch_stat_items(api_key, stat_code, cycle):
    url = ECOS_ITEM_URL.format(key=api_key, stat_code=stat_code, cycle=cycle)
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    payload = res.json()
    rows = payload.get("StatisticItemList", {}).get("row", []) or []
    return rows


def _fetch_fx_items(api_key):
    return _fetch_stat_items(api_key, "731Y001", "D")


def _find_item_code(rows, name_patterns):
    for row in rows:
        name = str(row.get("ITEM_NAME") or "")
        if any(p in name for p in name_patterns):
            return row.get("ITEM_CODE")
    return None


def _fetch_fx_value(api_key, item_code):
    if not item_code:
        return None
    today = date.today()
    start = (today - timedelta(days=120)).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")
    url = ECOS_SEARCH_URL.format(
        key=api_key,
        stat_code="731Y001",
        cycle="D",
        start=start,
        end=end,
        item_code=item_code,
    )
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    payload = res.json()
    result = payload.get("RESULT")
    if result and result.get("CODE") not in (None, "INFO-000"):
        return None
    rows = payload.get("StatisticSearch", {}).get("row", []) or []
    if not rows:
        return None
    last = rows[-1]
    return _parse_value(last)


def _find_key_stat_row(rows, patterns):
    for row in rows:
        text = _row_text(row)
        if any(p in text for p in patterns):
            return row
    return None


def _pick_stat_code(row):
    if not row:
        return None
    for key in ("STAT_CODE", "STAT_CODE1"):
        val = row.get(key)
        if val:
            return val
    return None


def _pick_item_code(row):
    if not row:
        return None
    for key in ("ITEM_CODE1", "ITEM_CODE2", "ITEM_CODE3", "ITEM_CODE4", "ITEM_CODE"):
        val = row.get(key)
        if val:
            return val
    return None


def _pick_cycle(row):
    if not row:
        return "D"
    cycle = row.get("CYCLE")
    return cycle or "D"


def _format_ecos_range(target_date, cycle):
    if cycle == "D":
        return target_date.strftime("%Y%m%d")
    if cycle == "M":
        return target_date.strftime("%Y%m")
    if cycle == "Q":
        quarter = (target_date.month - 1) // 3 + 1
        return f"{target_date.year}Q{quarter}"
    if cycle == "Y":
        return target_date.strftime("%Y")
    return target_date.strftime("%Y%m%d")


def _format_ecos_time(value, cycle):
    if not value:
        return ""
    text = str(value)
    if cycle == "D" and len(text) == 8:
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"
    if cycle == "M" and len(text) >= 6:
        return f"{text[:4]}-{text[4:6]}-01"
    if cycle == "Q":
        if "Q" in text:
            year = text[:4]
            quarter = text[-1]
        else:
            year = text[:4]
            quarter = text[4:5]
        month = {"1": "01", "2": "04", "3": "07", "4": "10"}.get(quarter, "01")
        return f"{year}-{month}-01"
    if cycle == "Y" and len(text) >= 4:
        return f"{text[:4]}-01-01"
    return text


def _fetch_stat_series(api_key, stat_code, cycle, item_code, start_date, end_date):
    if not (api_key and stat_code and item_code):
        return []
    start = _format_ecos_range(start_date, cycle)
    end = _format_ecos_range(end_date, cycle)
    url = ECOS_SEARCH_URL.format(
        key=api_key,
        stat_code=stat_code,
        cycle=cycle,
        start=start,
        end=end,
        item_code=item_code,
    )
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    payload = res.json()
    result = payload.get("RESULT")
    if result and result.get("CODE") not in (None, "INFO-000"):
        return []
    rows = payload.get("StatisticSearch", {}).get("row", []) or []
    series = []
    for row in rows:
        value = _parse_value(row)
        time_value = _format_ecos_time(row.get("TIME"), cycle)
        if value is None or not time_value:
            continue
        series.append({"date": time_value, "value": value})
    return series


def _fetch_base_rate_series(api_key, rows, start_date, end_date):
    base_row = _find_key_stat_row(rows, ["기준금리"])
    stat_code = _pick_stat_code(base_row)
    item_code = _pick_item_code(base_row)
    cycle = _pick_cycle(base_row)
    series = _fetch_stat_series(api_key, stat_code, cycle, item_code, start_date, end_date)
    if series:
        return series
    try:
        items = _fetch_stat_items(api_key, "722Y001", "D")
    except requests.RequestException:
        return []
    return _fetch_stat_series(api_key, "722Y001", "D", _find_item_code(items, ["기준금리"]), start_date, end_date)


def _fetch_bond_3y_series(api_key, rows, start_date, end_date):
    bond_row = _find_key_stat_row(
        rows,
        ["국고채수익률(3년)", "국고채(3년)", "국채 3년", "국고채 3년", "3년 국고채"],
    )
    stat_code = _pick_stat_code(bond_row)
    item_code = _pick_item_code(bond_row)
    cycle = _pick_cycle(bond_row)
    return _fetch_stat_series(api_key, stat_code, cycle, item_code, start_date, end_date)


class MarketSummaryView(APIView):
    def get(self, request):
        now = time.time()
        cached = _CACHE.get("data")
        if cached and now - _CACHE["ts"] < _TTL and not request.query_params.get("debug"):
            return Response(cached, status=status.HTTP_200_OK)

        try:
            result = _fetch_key_stats()
            rows = result.get("rows", [])
        except requests.RequestException:
            return Response({"detail": "failed to fetch BOK data"}, status=status.HTTP_502_BAD_GATEWAY)

        api_key = getattr(settings, "BOK_API_KEY", "")
        fx_detail = ""
        usd = None
        jpy = None

        if api_key:
            try:
                fx_items = _fetch_fx_items(api_key)
                usd_code = _find_item_code(fx_items, ["원/미국달러", "원/달러"])
                jpy_code = _find_item_code(fx_items, ["원/일본엔", "원/엔"])
                usd = _fetch_fx_value(api_key, usd_code)
                jpy = _fetch_fx_value(api_key, jpy_code)
            except requests.RequestException:
                fx_detail = "failed to fetch FX data"
        else:
            fx_detail = "BOK_API_KEY not set"

        base_rate = _find_value(rows, ["기준금리"])
        bond_3y = _find_value(rows, ["국고채수익률(3년)", "국고채(3년)", "국채 3년", "국고채 3년", "3년 국고채"])

        data = {
            "usd_krw": usd,
            "jpy_krw_100": jpy,
            "base_rate": base_rate,
            "bond_3y": bond_3y,
            "source": "BOK-ECOS",
        }

        if result.get("error"):
            data["detail"] = result["error"]
        elif fx_detail:
            data["detail"] = fx_detail

        _CACHE["ts"] = now
        _CACHE["data"] = data

        if request.query_params.get("debug"):
            data["rows"] = rows
            data["result"] = result.get("result")

        return Response(data, status=status.HTTP_200_OK)


class MarketHistoryView(APIView):
    def get(self, request):
        api_key = getattr(settings, "BOK_API_KEY", "")
        if not api_key:
            return Response({"detail": "BOK_API_KEY not set"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            years = int(request.query_params.get("years", 3))
        except ValueError:
            years = 3
        years = max(1, min(years, 20))

        cache_key = f"years:{years}"
        cached = _HISTORY_CACHE.get(cache_key)
        now = time.time()
        if cached and now - cached["ts"] < _HISTORY_TTL:
            return Response(cached["data"], status=status.HTTP_200_OK)

        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)

        try:
            result = _fetch_key_stats()
            rows = result.get("rows", [])
        except requests.RequestException:
            return Response({"detail": "failed to fetch BOK data"}, status=status.HTTP_502_BAD_GATEWAY)

        detail = {}

        try:
            fx_items = _fetch_fx_items(api_key)
            usd_code = _find_item_code(fx_items, ["원/미국달러", "원/달러"])
            jpy_code = _find_item_code(fx_items, ["원/일본엔", "원/엔"])
        except requests.RequestException:
            fx_items = []
            usd_code = None
            jpy_code = None
            detail["fx"] = "failed to fetch FX items"

        series = {
            "usd_krw": [],
            "jpy_krw_100": [],
            "base_rate": [],
            "bond_3y": [],
        }

        try:
            series["usd_krw"] = _fetch_stat_series(api_key, "731Y001", "D", usd_code, start_date, end_date)
            series["jpy_krw_100"] = _fetch_stat_series(api_key, "731Y001", "D", jpy_code, start_date, end_date)
        except requests.RequestException:
            detail["fx"] = "failed to fetch FX series"

        try:
            series["base_rate"] = _fetch_base_rate_series(api_key, rows, start_date, end_date)
            series["bond_3y"] = _fetch_bond_3y_series(api_key, rows, start_date, end_date)
        except requests.RequestException:
            detail["rates"] = "failed to fetch rate series"

        if result.get("error"):
            detail["key_stats"] = result["error"]

        data = {
            "range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "years": years,
            },
            "series": series,
            "detail": detail,
        }

        _HISTORY_CACHE[cache_key] = {"ts": now, "data": data}

        return Response(data, status=status.HTTP_200_OK)
