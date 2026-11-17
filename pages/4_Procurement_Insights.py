import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from translations import get_language, format_money, format_number

st.set_page_config(
    page_title="Procurement Insights",
    page_icon="🔎",
    layout="wide",
)

if "app_language" in st.session_state:
    st.session_state["_language_choice"] = st.session_state["app_language"]
lang = get_language()

TEXT = {
    "pl": {
        "title": "Wykrywanie problemów zakupowych",
        "intro": "Automatyczna analiza odchyleń, terminowości, jakości i cen materiałów",
        "min_orders": "Minimalna liczba transakcji na dostawcę",
        "late_limit": "Próg opóźnionych dostaw (%)",
        "quality_limit": "Próg problemów jakościowych (%)",
        "budget_limit": "Próg przekroczenia budżetu (%)",
        "alerts": "Sygnały ostrzegawcze dotyczące dostawców",
        "price": "Zmiany cen materiałów: 2025 vs 2026",
        "price_limit": "Minimalny wzrost ceny (%)",
        "period": "Liczba transakcji w każdym roku (minimum)",
        "supplier": "Dostawca", "orders": "Transakcje",
        "spend": "Zakupy (PLN)", "late": "Opóźnione dostawy (%)",
        "quality": "Problemy jakościowe (%)", "variance": "Odchylenie budżetowe (%)",
        "flags": "Wykryte sygnały", "late_flag": "Opóźnienia",
        "quality_flag": "Jakość", "budget_flag": "Budżet",
        "material": "Materiał", "currency": "Waluta",
        "count_2025": "Transakcje 2025", "count_2026": "Transakcje 2026",
        "price_2025": "Cena jedn. 2025", "price_2026": "Cena jedn. 2026",
        "change": "Zmiana ceny (%)", "none": "Brak wyników dla tych progów.",
        "download": "Pobierz wyniki CSV", "db_error": "Błąd odczytu bazy",
        "kpi_suppliers": "Dostawcy z sygnałami",
        "kpi_materials": "Materiały ze wzrostem cen",
        "note": "Dane wyłącznie demonstracyjne. Sygnał to przekroczenie ustalonego progu, a nie potwierdzenie przyczyny problemu.",
        "method": "Ceny porównujemy dla tego samego kodu materiału i tej samej waluty. Średnie ceny są ważone zakupioną ilością. To porównanie lat, nie analiza wpływu kursu walutowego. Terminowość i jakość liczone są jako udział transakcji.",
    },
    "en": {
        "title": "Procurement Issue Detection",
        "intro": "Automated analysis of variances, deliveries, quality and material prices",
        "min_orders": "Minimum transactions per supplier",
        "late_limit": "Late delivery threshold (%)",
        "quality_limit": "Quality issue threshold (%)",
        "budget_limit": "Over-budget threshold (%)",
        "alerts": "Supplier warning signals",
        "price": "Material price changes: 2025 vs 2026",
        "price_limit": "Minimum price increase (%)",
        "period": "Minimum transactions in each year",
        "supplier": "Supplier", "orders": "Transactions",
        "spend": "Spend (PLN)", "late": "Late deliveries (%)",
        "quality": "Quality issues (%)", "variance": "Budget variance (%)",
        "flags": "Warning signals", "late_flag": "Delivery delays",
        "quality_flag": "Quality", "budget_flag": "Budget",
        "material": "Material", "currency": "Currency",
        "count_2025": "2025 transactions", "count_2026": "2026 transactions",
        "price_2025": "2025 unit price", "price_2026": "2026 unit price",
        "change": "Price change (%)", "none": "No results match these thresholds.",
        "download": "Download results as CSV", "db_error": "Database read error",
        "kpi_suppliers": "Suppliers flagged",
        "kpi_materials": "Materials with price increases",
        "note": "Synthetic demonstration data only. A warning indicates a threshold breach, not a proven root cause.",
        "method": "Prices are compared for the same material ID and currency. Average unit prices are weighted by purchased quantity. This is a year-on-year comparison, not an FX impact analysis. Delivery and quality metrics are transaction-based.",
    },
    "da": {
        "title": "Identifikation af indkøbsproblemer",
        "intro": "Automatisk analyse af afvigelser, levering, kvalitet og materialepriser",
        "min_orders": "Minimum antal transaktioner pr. leverandør",
        "late_limit": "Grænse for forsinkede leveringer (%)",
        "quality_limit": "Grænse for kvalitetsproblemer (%)",
        "budget_limit": "Grænse for budgetoverskridelse (%)",
        "alerts": "Advarselssignaler for leverandører",
        "price": "Ændringer i materialepriser: 2025 vs. 2026",
        "price_limit": "Mindste prisstigning (%)",
        "period": "Minimum antal transaktioner i hvert år",
        "supplier": "Leverandør", "orders": "Transaktioner",
        "spend": "Indkøb (PLN)", "late": "Forsinkede leveringer (%)",
        "quality": "Kvalitetsproblemer (%)", "variance": "Budgetafvigelse (%)",
        "flags": "Advarselssignaler", "late_flag": "Forsinkelser",
        "quality_flag": "Kvalitet", "budget_flag": "Budget",
        "material": "Materiale", "currency": "Valuta",
        "count_2025": "Transaktioner 2025", "count_2026": "Transaktioner 2026",
        "price_2025": "Enhedspris 2025", "price_2026": "Enhedspris 2026",
        "change": "Prisændring (%)", "none": "Ingen resultater opfylder grænserne.",
        "download": "Download resultater som CSV", "db_error": "Fejl ved læsning af databasen",
        "kpi_suppliers": "Leverandører med advarsler",
        "kpi_materials": "Materialer med prisstigninger",
        "note": "Kun syntetiske demonstrationsdata. En advarsel viser, at en grænse er overskredet, ikke en dokumenteret årsag.",
        "method": "Priser sammenlignes for samme materiale-ID og valuta. Gennemsnitlige enhedspriser vægtes efter indkøbt mængde. Dette er en sammenligning mellem år, ikke en valutakursanalyse. Levering og kvalitet beregnes pr. transaktion.",
    },
}
t = TEXT[lang]

@st.cache_data(show_spinner=False)
def load_transactions():
    db_path = PROJECT_DIR / "procurement_demo.db"
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        return pd.read_sql_query("SELECT * FROM procurement_transactions", conn)

try:
    df = load_transactions()
except (sqlite3.Error, OSError, pd.errors.DatabaseError) as error:
    st.error(f"{t['db_error']}: {error}")
    st.stop()

st.title(t["title"])
st.caption(t["intro"])

c1, c2 = st.columns(2)
with c1:
    min_orders = st.slider(t["min_orders"], 10, 100, 30, 5)
    late_limit = st.slider(t["late_limit"], 0, 100, 60, 5)
with c2:
    quality_limit = st.slider(t["quality_limit"], 0, 30, 6, 1)
    budget_limit = st.slider(t["budget_limit"], 0, 20, 3, 1)

# Jeden wiersz = jedna transakcja. Dodatnia wariancja oznacza większy koszt.
supplier_data = df.groupby(["supplier_id", "supplier_name"], as_index=False).agg(
    transactions=("transaction_id", "count"),
    spend_pln=("actual_value_pln", "sum"),
    budget_pln=("budget_value_pln", "sum"),
    variance_pln=("variance_pln", "sum"),
    late_pct=("on_time", lambda x: 100 * (1 - x.mean())),
    quality_pct=("quality_issue", lambda x: 100 * x.mean()),
)
supplier_data["budget_pct"] = (
    100 * supplier_data["variance_pln"] /
    supplier_data["budget_pln"].where(supplier_data["budget_pln"] != 0)
).fillna(0)

supplier_data = supplier_data[supplier_data["transactions"] >= min_orders].copy()

def supplier_flags(row):
    result = []
    if row["late_pct"] >= late_limit:
        result.append(t["late_flag"])
    if row["quality_pct"] >= quality_limit:
        result.append(t["quality_flag"])
    if row["budget_pct"] >= budget_limit:
        result.append(t["budget_flag"])
    return ", ".join(result)

supplier_data["signals"] = supplier_data.apply(supplier_flags, axis=1)
alerts = supplier_data[supplier_data["signals"] != ""].copy()
alerts = alerts.sort_values(["variance_pln", "late_pct"], ascending=False)

# Porównujemy ceny na tych samych materiałach i w tych samych walutach.
price_data = df.copy()
price_data["year"] = pd.to_datetime(price_data["order_date"]).dt.year
price_data = price_data[price_data["year"].isin([2025, 2026])]
price_data = price_data[price_data["quantity"] > 0].copy()
price_data["price_times_qty"] = price_data["actual_unit_price"] * price_data["quantity"]

annual = price_data.groupby(
    ["material_id", "material_name", "currency", "year"], as_index=False
).agg(
    transactions=("transaction_id", "count"),
    total_qty=("quantity", "sum"),
    total_price_qty=("price_times_qty", "sum"),
)
annual["unit_price"] = annual["total_price_qty"] / annual["total_qty"]

counts = annual.pivot_table(
    index=["material_id", "material_name", "currency"],
    columns="year", values="transactions", fill_value=0
)
prices = annual.pivot_table(
    index=["material_id", "material_name", "currency"],
    columns="year", values="unit_price"
)

price_limit = st.slider(t["price_limit"], 0, 30, 5, 1)
minimum_year = st.slider(t["period"], 2, 20, 5, 1)

both = counts.index.intersection(prices.index)
result = pd.DataFrame(index=both)
for year in [2025, 2026]:
    result[f"count_{year}"] = counts.reindex(both).get(year, 0)
    result[f"price_{year}"] = prices.reindex(both).get(year)
result = result.reset_index()
result = result[
    (result["count_2025"] >= minimum_year)
    & (result["count_2026"] >= minimum_year)
    & (result["price_2025"] > 0)
].copy()
result["change_pct"] = 100 * (
    result["price_2026"] / result["price_2025"] - 1
)
price_alerts = result[result["change_pct"] >= price_limit].sort_values(
    "change_pct", ascending=False
)

st.divider()
a, b = st.columns(2)
a.metric(t["kpi_suppliers"], format_number(len(alerts), lang, 0))
b.metric(t["kpi_materials"], format_number(len(price_alerts), lang, 0))

st.subheader(t["alerts"])
if alerts.empty:
    st.info(t["none"])
else:
    supplier_display = alerts[[
        "supplier_name", "transactions", "spend_pln",
        "late_pct", "quality_pct", "budget_pct", "signals"
    ]].rename(columns={
        "supplier_name": t["supplier"], "transactions": t["orders"],
        "spend_pln": t["spend"], "late_pct": t["late"],
        "quality_pct": t["quality"], "budget_pct": t["variance"],
        "signals": t["flags"],
    }).round(2)
    st.dataframe(supplier_display, hide_index=True, width="stretch")
    st.download_button(
        t["download"], supplier_display.to_csv(index=False).encode("utf-8-sig"),
        file_name="supplier_alerts.csv", mime="text/csv",
        key="download_suppliers",
    )

st.subheader(t["price"])
if price_alerts.empty:
    st.info(t["none"])
else:
    price_display = price_alerts[[
        "material_id", "material_name", "currency", "count_2025",
        "count_2026", "price_2025", "price_2026", "change_pct"
    ]].rename(columns={
        "material_id": "ID", "material_name": t["material"],
        "currency": t["currency"], "count_2025": t["count_2025"],
        "count_2026": t["count_2026"], "price_2025": t["price_2025"],
        "price_2026": t["price_2026"], "change_pct": t["change"],
    }).round(2)
    st.dataframe(price_display, hide_index=True, width="stretch")
    st.download_button(
        t["download"], price_display.to_csv(index=False).encode("utf-8-sig"),
        file_name="material_price_alerts.csv", mime="text/csv",
        key="download_prices",
    )

st.caption(t["method"])
st.caption(t["note"])
