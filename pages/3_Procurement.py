
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from translations import (
    get_language,
    format_money,
    format_number,
    format_percent,
)

st.set_page_config(
    page_title="Procurement Analytics",
    page_icon="📦",
    layout="wide",
)

if "app_language" in st.session_state:
    st.session_state["_language_choice"] = (
        st.session_state["app_language"]
    )

lang = get_language()

TEXT = {
    "pl": {
        "title": "Analiza zakupów i dostawców",
        "intro": "Controlling zakupów na danych demonstracyjnych",
        "period": "Okres zamówień",
        "supplier": "Dostawca",
        "category": "Kategoria materiałowa",
        "currency": "Waluta",
        "all": "Wszystkie",
        "spend": "Wartość zakupów",
        "variance": "Odchylenie od budżetu",
        "transactions": "Transakcje",
        "suppliers": "Dostawcy",
        "ontime": "Dostawy terminowe",
        "quality": "Problemy jakościowe",
        "delay": "Średnie opóźnienie (dni)",
        "trend": "Zakupy w kolejnych miesiącach",
        "ranking": "10 największych dostawców",
        "categories": "Wydatki według kategorii",
        "supplier_table": "Wyniki dostawców",
        "transactions_table": "Transakcje",
        "download": "Pobierz wybrane transakcje (CSV)",
        "month": "Miesiąc",
        "no_data": "Brak transakcji dla wybranych filtrów.",
        "db_error": "Problem z bazą zakupową",
        "note": (
            "Dane syntetyczne. Odchylenie to wartość zakupów "
            "minus budżet. Wynik dodatni oznacza przekroczenie "
            "budżetu. Kwoty w PLN według kursów zapisanych w bazie."
        ),
    },
    "en": {
        "title": "Procurement & Supplier Analytics",
        "intro": "Procurement controlling using demonstration data",
        "period": "Order date range",
        "supplier": "Supplier",
        "category": "Material category",
        "currency": "Currency",
        "all": "All",
        "spend": "Purchase value",
        "variance": "Variance vs budget",
        "transactions": "Transactions",
        "suppliers": "Suppliers",
        "ontime": "On-time deliveries",
        "quality": "Quality issues",
        "delay": "Average delay (days)",
        "trend": "Monthly purchase value",
        "ranking": "Top 10 suppliers",
        "categories": "Spend by category",
        "supplier_table": "Supplier performance",
        "transactions_table": "Transactions",
        "download": "Download filtered transactions (CSV)",
        "month": "Month",
        "no_data": "No transactions match the selected filters.",
        "db_error": "Procurement database error",
        "note": (
            "Synthetic data. Variance equals purchase value "
            "minus budget. A positive figure means over budget. "
            "PLN values use FX rates stored in the dataset."
        ),
    },
    "da": {
        "title": "Indkøbs- og leverandøranalyse",
        "intro": "Indkøbscontrolling med demonstrationsdata",
        "period": "Ordredatointerval",
        "supplier": "Leverandør",
        "category": "Materialekategori",
        "currency": "Valuta",
        "all": "Alle",
        "spend": "Indkøbsværdi",
        "variance": "Afvigelse fra budget",
        "transactions": "Transaktioner",
        "suppliers": "Leverandører",
        "ontime": "Leveringer til tiden",
        "quality": "Kvalitetsproblemer",
        "delay": "Gennemsnitlig forsinkelse (dage)",
        "trend": "Månedlig indkøbsværdi",
        "ranking": "10 største leverandører",
        "categories": "Indkøb fordelt på kategorier",
        "supplier_table": "Leverandørresultater",
        "transactions_table": "Transaktioner",
        "download": "Download filtrerede transaktioner (CSV)",
        "month": "Måned",
        "no_data": "Ingen transaktioner matcher filtrene.",
        "db_error": "Fejl i indkøbsdatabasen",
        "note": (
            "Alle data er syntetiske. Afvigelsen er indkøbsværdi "
            "minus budget. Et positivt beløb betyder en "
            "budgetoverskridelse. PLN-beløb bruger valutakurser "
            "gemt i datasættet."
        ),
    },
}

t = TEXT[lang]

# Tłumaczenia kategorii materiałowych

CATEGORY_NAMES = {
    "Automatyka": (
        "Automatyka", "Automation", "Automation"
    ),
    "Komponenty elektryczne": (
        "Komponenty elektryczne",
        "Electrical components",
        "Elektriske komponenter",
    ),
    "Konstrukcje spawane": (
        "Konstrukcje spawane",
        "Welded structures",
        "Svejste konstruktioner",
    ),
    "Napędy i przekładnie": (
        "Napędy i przekładnie",
        "Drives and gearboxes",
        "Drev og gearkasser",
    ),
    "Opakowania": (
        "Opakowania", "Packaging", "Emballage"
    ),
    "Pneumatyka": (
        "Pneumatyka", "Pneumatics", "Pneumatik"
    ),
    "Przenośniki i rolki": (
        "Przenośniki i rolki",
        "Conveyors and rollers",
        "Transportører og ruller",
    ),
    "Stal i blachy": (
        "Stal i blachy",
        "Steel and sheet metal",
        "Stål og plader",
    ),
    "Usługi obróbki": (
        "Usługi obróbki",
        "Machining services",
        "Bearbejdningsydelser",
    ),
    "Łożyska i mechanika": (
        "Łożyska i mechanika",
        "Bearings and mechanics",
        "Lejer og mekanik",
    ),
}

LANG_INDEX = {"pl": 0, "en": 1, "da": 2}


def local_category(name):
    names = CATEGORY_NAMES.get(name)
    if names:
        return names[LANG_INDEX[lang]]
    return name


# ==========================================
# BAZA DANYCH
# ==========================================

@st.cache_data(show_spinner=False)
def load_data():
    path = PROJECT_DIR / "procurement_demo.db"

    if not path.is_file():
        raise FileNotFoundError(str(path))

    with sqlite3.connect(path) as db:
        return pd.read_sql_query(
            "SELECT * FROM procurement_transactions",
            db,
        )


try:
    df = load_data()
except (
    sqlite3.Error,
    FileNotFoundError,
    pd.errors.DatabaseError,
) as error:
    st.error(f"{t['db_error']}: {error}")
    st.stop()

df["order_date"] = pd.to_datetime(
    df["order_date"], errors="coerce"
)

df = df.dropna(subset=["order_date"])

df["category_display"] = df["category"].map(
    local_category
)

# ==========================================
# FILTRY
# ==========================================

st.title(t["title"])
st.caption(t["intro"])
st.divider()

minimum = df["order_date"].min().date()
maximum = df["order_date"].max().date()

period = st.date_input(
    t["period"],
    value=(minimum, maximum),
    min_value=minimum,
    max_value=maximum,
)

if not isinstance(period, (tuple, list)) or len(period) != 2:
    st.info(t["period"])
    st.stop()

start, end = period

s1, s2, s3 = st.columns(3)

with s1:
    supplier_options = sorted(
        df["supplier_name"].unique().tolist()
    )
    supplier = st.selectbox(
        t["supplier"],
        [t["all"]] + supplier_options,
    )

with s2:
    categories = sorted(
        df["category_display"].unique().tolist()
    )
    category = st.selectbox(
        t["category"],
        [t["all"]] + categories,
    )

with s3:
    currency = st.selectbox(
        t["currency"],
        [t["all"], "PLN", "EUR", "USD", "DKK"],
    )

filtered = df[
    df["order_date"].dt.date.between(start, end)
].copy()

if supplier != t["all"]:
    filtered = filtered[
        filtered["supplier_name"] == supplier
    ]

if category != t["all"]:
    filtered = filtered[
        filtered["category_display"] == category
    ]

if currency != t["all"]:
    filtered = filtered[
        filtered["currency"] == currency
    ]

if filtered.empty:
    st.warning(t["no_data"])
    st.stop()

# ==========================================
# WSKAŹNIKI KPI
# ==========================================

spend = filtered["actual_value_pln"].sum()
variance = filtered["variance_pln"].sum()
budget = filtered["budget_value_pln"].sum()

variance_pct = (
    variance / budget * 100 if budget else 0.0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    t["spend"],
    format_money(spend, lang),
)

k2.metric(
    t["variance"],
    format_money(variance, lang),
    delta=format_percent(
        variance_pct, lang, signed=True
    ),
    delta_color="inverse",
)

k3.metric(
    t["transactions"],
    format_number(len(filtered), lang, 0),
)

k4.metric(
    t["suppliers"],
    format_number(
        filtered["supplier_id"].nunique(), lang, 0
    ),
)

st.divider()

q1, q2, q3 = st.columns(3)

q1.metric(
    t["ontime"],
    format_percent(
        filtered["on_time"].mean() * 100, lang
    ),
)

q2.metric(
    t["quality"],
    format_percent(
        filtered["quality_issue"].mean() * 100,
        lang,
    ),
)

q3.metric(
    t["delay"],
    format_number(
        filtered["delay_days"].mean(), lang, 1
    ),
)

# ==========================================
# TREND ZAKUPÓW
# ==========================================

st.divider()

filtered["month"] = (
    filtered["order_date"].dt.strftime("%Y-%m")
)

monthly = (
    filtered.groupby("month", as_index=False)[
        "actual_value_pln"
    ]
    .sum()
    .sort_values("month")
)

st.subheader(t["trend"])

fig = px.line(
    monthly,
    x="month",
    y="actual_value_pln",
    markers=True,
    labels={
        "month": t["month"],
        "actual_value_pln": t["spend"],
    },
)

st.plotly_chart(fig, width="stretch")

# ==========================================
# DOSTAWCY I KATEGORIE
# ==========================================

left, right = st.columns(2)

with left:
    st.subheader(t["ranking"])

    top = (
        filtered.groupby(
            "supplier_name", as_index=False
        )["actual_value_pln"]
        .sum()
        .nlargest(10, "actual_value_pln")
    )

    fig = px.bar(
        top.sort_values("actual_value_pln"),
        x="actual_value_pln",
        y="supplier_name",
        orientation="h",
        labels={
            "supplier_name": t["supplier"],
            "actual_value_pln": t["spend"],
        },
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader(t["categories"])

    cat_data = (
        filtered.groupby(
            "category_display", as_index=False
        )["actual_value_pln"]
        .sum()
        .sort_values("actual_value_pln")
    )

    fig = px.bar(
        cat_data,
        x="actual_value_pln",
        y="category_display",
        orientation="h",
        labels={
            "category_display": t["category"],
            "actual_value_pln": t["spend"],
        },
    )
    st.plotly_chart(fig, width="stretch")

# ==========================================
# ANALIZA DOSTAWCÓW
# ==========================================

st.subheader(t["supplier_table"])

supplier_stats = filtered.groupby(
    ["supplier_id", "supplier_name"],
    as_index=False,
).agg(
    transactions=("transaction_id", "count"),
    spend_pln=("actual_value_pln", "sum"),
    variance_pln=("variance_pln", "sum"),
    on_time_pct=("on_time", "mean"),
    quality_issue_pct=("quality_issue", "mean"),
)

supplier_stats["on_time_pct"] = (
    supplier_stats["on_time_pct"] * 100
).round(1)

supplier_stats["quality_issue_pct"] = (
    supplier_stats["quality_issue_pct"] * 100
).round(1)

st.dataframe(
    supplier_stats.sort_values(
        "spend_pln", ascending=False
    ).round(2),
    hide_index=True,
    width="stretch",
)

# ==========================================
# TRANSAKCJE I EKSPORT
# ==========================================

st.subheader(t["transactions_table"])

st.dataframe(
    filtered.drop(columns=["month"])
    .sort_values("order_date", ascending=False)
    .head(300),
    hide_index=True,
    width="stretch",
)

st.download_button(
    t["download"],
    data=filtered.drop(
        columns=["month"]
    ).to_csv(index=False).encode("utf-8-sig"),
    file_name="procurement_filtered.csv",
    mime="text/csv",
)

st.caption(t["note"])
