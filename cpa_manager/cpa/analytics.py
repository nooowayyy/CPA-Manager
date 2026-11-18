from collections import defaultdict
from decimal import Decimal
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from .models import PerformanceRecord

ZERO = Decimal("0.00")

def safe_ratio(numerator, denominator):
    if not denominator:
        return None
    return (Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.01"))

def aggregate_metrics(records):
    totals = records.aggregate(spend=Sum("spend"), clicks=Sum("clicks"), conversions=Sum("conversions"), impressions=Sum("impressions"))
    spend = totals["spend"] or ZERO
    clicks = totals["clicks"] or 0
    conversions = totals["conversions"] or 0
    impressions = totals["impressions"] or 0
    return {
        "spend": spend, "clicks": clicks, "conversions": conversions, "impressions": impressions,
        "cpc": safe_ratio(spend, clicks), "cpa": safe_ratio(spend, conversions),
        "conversion_rate": (Decimal(conversions) * 100 / Decimal(clicks)).quantize(Decimal("0.01")) if clicks else None,
        "ctr": (Decimal(clicks) * 100 / Decimal(impressions)).quantize(Decimal("0.01")) if impressions else None,
    }

def build_dashboard_data(user, start_date=None, end_date=None):
    today = timezone.localdate()
    start_date = start_date or (today - timedelta(days=29))
    end_date = end_date or today
    qs = PerformanceRecord.objects.filter(user=user, date__gte=start_date, date__lte=end_date).select_related("campaign", "campaign__platform", "campaign__channel")
    totals = aggregate_metrics(qs)
    daily = defaultdict(lambda: {"spend": ZERO, "clicks": 0, "conversions": 0})
    for row in qs.values("date", "spend", "clicks", "conversions"):
        key = row["date"].isoformat()
        daily[key]["spend"] += row["spend"]
        daily[key]["clicks"] += row["clicks"]
        daily[key]["conversions"] += row["conversions"]
    daily_rows = []
    current_day = start_date
    while current_day <= end_date:
        day = current_day.isoformat()
        vals = daily.get(day, {"spend": ZERO, "clicks": 0, "conversions": 0})
        daily_rows.append({"date": day, "spend": float(vals["spend"]), "clicks": vals["clicks"], "conversions": vals["conversions"], "cpc": float(safe_ratio(vals["spend"], vals["clicks"])) if vals["clicks"] else None, "cpa": float(safe_ratio(vals["spend"], vals["conversions"])) if vals["conversions"] else None})
        current_day += timedelta(days=1)
    campaign_totals = defaultdict(lambda: {"id": None, "name": "", "integration_key": "", "external_id": "", "platform": None, "channel": None, "objective": "", "conversion_label": "Conversões", "spend": ZERO, "clicks": 0, "conversions": 0})
    for row in qs.values("campaign__id", "campaign__name", "campaign__integration_key", "campaign__external_id", "campaign__platform__name", "campaign__channel__name", "campaign__objective", "campaign__conversion_label", "spend", "clicks", "conversions"):
        item = campaign_totals[row["campaign__id"]]
        item["id"] = row["campaign__id"]
        item["name"] = row["campaign__name"]
        item["integration_key"] = row["campaign__integration_key"]
        item["external_id"] = row["campaign__external_id"]
        item["platform"] = row["campaign__platform__name"]
        item["channel"] = row["campaign__channel__name"]
        item["objective"] = row["campaign__objective"]
        item["conversion_label"] = row["campaign__conversion_label"]
        item["spend"] += row["spend"]
        item["clicks"] += row["clicks"]
        item["conversions"] += row["conversions"]
    campaigns = []
    for item in campaign_totals.values():
        campaigns.append({"id": item["id"], "name": item["name"], "integration_key": item["integration_key"], "external_id": item["external_id"], "platform": item["platform"], "channel": item["channel"], "objective": item["objective"], "conversion_label": item["conversion_label"], "spend": float(item["spend"]), "clicks": item["clicks"], "conversions": item["conversions"], "cpc": float(safe_ratio(item["spend"], item["clicks"])) if item["clicks"] else None, "cpa": float(safe_ratio(item["spend"], item["conversions"])) if item["conversions"] else None})
    campaigns.sort(key=lambda x: x["spend"], reverse=True)
    return {"start_date": start_date, "end_date": end_date, "totals": totals, "daily": daily_rows, "campaigns": campaigns, "record_count": qs.count()}
