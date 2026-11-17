
import sqlite3
import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

# ==========================================
# PROJECT SETTINGS
# ==========================================

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

from translations import (
    get_language,
    format_money,
    format_number,
)

st.set_page_config(
    page_title="Profitability & Margin Analysis",
    page_icon="📈",
    layout="wide",
)

# ==========================================
# LANGUAGE SETTINGS
# ==========================================

if "app_language" in st.session_state:
    st.session_state["_language_choice"] = (
        st.session_state["app_language"]
    )

language = get_language()

TEXTS = {
    "pl": {
        "title": "Analiza rentowności i marży",
        "subtitle": "Wpływ kursów walut na rentowność projektu",
        "currency": "Waluta zakupów",
        "revenue": "Przychód ze sprzedaży (PLN)",
        "materials": "Koszt materiałów w walucie obcej",
        "other": "Pozostałe koszty projektu (PLN)",
        "budget_rate": "Kurs budżetowy",
        "nbp_rate": "Ostatni kurs NBP",
        "budget": "Marża budżetowa",
        "actual": "Marża według kursu NBP",
        "change": "Zmiana marży (pp)",
        "profit_budget": "Wynik budżetowy",
        "profit_actual": "Wynik według kursu NBP",
        "fx_impact": "Wpływ kursu na koszt materiałów",
        "chart": "Porównanie rentowności",
        "recommendation": "Wniosek z analizy",
        "negative": "Zmiana kursu obniża rentowność projektu.",
        "positive": "Zmiana kursu poprawia rentowność projektu.",
        "neutral": "Zmiana kursu nie wpływa na rentowność.",
        "rate_date": "Data kursu NBP",
        "no_data": "Brak kursu w bazie danych.",
        "db_error": "Błąd odczytu bazy danych",
        "invalid": "Przychód musi być większy od zera.",
        "note": "Symulacja przy stałej cenie sprzedaży i pozostałych kosztach. Kurs NBP nie oznacza rzeczywistego kursu transakcyjnego.",
    },
    "en": {
        "title": "Profitability & Margin Analysis",
        "subtitle": "FX impact on project profitability",
        "currency": "Purchasing currency",
        "revenue": "Sales revenue (PLN)",
        "materials": "Material cost in foreign currency",
        "other": "Other project costs (PLN)",
        "budget_rate": "Budget FX rate",
        "nbp_rate": "Latest NBP rate",
        "budget": "Budget margin",
        "actual": "Margin at NBP rate",
        "change": "Margin change (pp)",
        "profit_budget": "Budget profit",
        "profit_actual": "Profit at NBP rate",
        "fx_impact": "FX impact on material costs",
        "chart": "Profitability comparison",
        "recommendation": "Analysis conclusion",
        "negative": "Exchange rate changes reduce project profitability.",
        "positive": "Exchange rate changes improve project profitability.",
        "neutral": "Exchange rate changes have no impact.",
        "rate_date": "NBP rate date",
        "no_data": "No exchange rate in the database.",
        "db_error": "Database read error",
        "invalid": "Sales revenue must be greater than zero.",
        "note": "Simulation with fixed sales price and other costs. The NBP rate is not necessarily the actual transaction rate.",
    },
    "da": {
        "title": "Analyse af rentabilitet og avance",
        "subtitle": "Valutakursernes indvirkning på projektets rentabilitet",
        "currency": "Indkøbsvaluta",
        "revenue": "Salgsomsætning (PLN)",
        "materials": "Materialeomkostninger i fremmed valuta",
        "other": "Øvrige projektomkostninger (PLN)",
        "budget_rate": "Budgetteret valutakurs",
        "nbp_rate": "Seneste NBP-kurs",
        "budget": "Budgetteret avance",
        "actual": "Avance ved NBP-kurs",
        "change": "Ændring i avance (procentpoint)",
        "profit_budget": "Budgetteret resultat",
        "profit_actual": "Resultat ved NBP-kurs",
        "fx_impact": "Valutakursens effekt på materialeomkostninger",
        "chart": "Sammenligning af rentabilitet",
        "recommendation": "Konklusion på analysen",
        "negative": "Valutakursændringen reducerer projektets rentabilitet.",
        "positive": "Valutakursændringen forbedrer projektets rentabilitet.",
        "neutral": "Valutakursændringen påvirker ikke rentabiliteten.",
        "rate_date": "Dato for NBP-kursen",
        "no_data": "Ingen valutakurs i databasen.",
        "db_error": "Fejl ved læsning af databasen",
        "invalid": "Salgsomsætningen skal være større end nul.",
        "note": "Simulering med fast salgspris og øvrige omkostninger. NBP-kursen er ikke nødvendigvis den faktiske transaktionskurs.",
    },
}

t = TEXTS[language]

# ==========================================
# DATABASE
# ==========================================

database_path = project_dir / "businesshub.db"

try:
    with sqlite3.connect(database_path) as db:
        records = db.execute("""
            SELECT waluta, data, kurs
            FROM kursy_walut
            ORDER BY data DESC
        """).fetchall()

except sqlite3.Error as error:
    st.error(f"{t['db_error']}: {error}")
    st.stop()

rates = {}
dates = {}

for currency_code, date, rate in records:
    if currency_code not in rates:
        rates[currency_code] = rate
        dates[currency_code] = date

# ==========================================
# INPUT DATA
# ==========================================

st.title(t["title"])
st.caption(t["subtitle"])
st.divider()

currency = st.selectbox(
    t["currency"],
    ["EUR", "USD", "DKK"],
)

col1, col2 = st.columns(2)

with col1:
    revenue = st.number_input(
        t["revenue"],
        min_value=0.0,
        value=1000000.0,
        step=10000.0,
    )

    material_cost = st.number_input(
        t["materials"],
        min_value=0.0,
        value=100000.0,
        step=1000.0,
    )

with col2:
    other_costs = st.number_input(
        t["other"],
        min_value=0.0,
        value=320000.0,
        step=1000.0,
    )

    budget_defaults = {
        "EUR": 4.30,
        "USD": 4.00,
        "DKK": 0.58,
    }

    budget_rate = st.number_input(
        t["budget_rate"],
        min_value=0.0001,
        value=budget_defaults[currency],
        step=0.0001,
        format="%.4f",
        key=f"margin_budget_{currency}",
    )

current_rate = rates.get(currency)

if current_rate is None:
    st.warning(t["no_data"])
    st.stop()

if revenue <= 0:
    st.warning(t["invalid"])
    st.stop()

st.metric(
    t["nbp_rate"],
    format_number(current_rate, language, 4),
)

st.caption(f"{t['rate_date']}: {dates[currency]}")

# ==========================================
# FINANCIAL CALCULATIONS
# ==========================================

budget_materials = material_cost * budget_rate
actual_materials = material_cost * current_rate

total_budget_cost = budget_materials + other_costs
total_actual_cost = actual_materials + other_costs

budget_profit = revenue - total_budget_cost
actual_profit = revenue - total_actual_cost

budget_margin = budget_profit / revenue * 100
actual_margin = actual_profit / revenue * 100

margin_change = actual_margin - budget_margin
fx_impact = actual_materials - budget_materials

# ==========================================
# KPI DASHBOARD
# ==========================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        t["budget"],
        f"{format_number(budget_margin, language)}%",
    )

with col2:
    st.metric(
        t["actual"],
        f"{format_number(actual_margin, language)}%",
    )

with col3:
    st.metric(
        t["change"],
        format_number(margin_change, language),
        delta=f"{format_number(margin_change, language)} pp",
        delta_color="normal",
    )

st.divider()

col4, col5 = st.columns(2)

with col4:
    st.metric(
        t["profit_budget"],
        format_money(budget_profit, language),
    )

with col5:
    st.metric(
        t["profit_actual"],
        format_money(actual_profit, language),
    )

st.metric(
    t["fx_impact"],
    format_money(fx_impact, language),
)

# ==========================================
# CHART
# ==========================================

st.subheader(t["chart"])

fig = go.Figure()

fig.add_bar(
    x=[t["budget"], t["actual"]],
    y=[budget_margin, actual_margin],
    text=[
        f"{format_number(budget_margin, language)}%",
        f"{format_number(actual_margin, language)}%",
    ],
    textposition="auto",
)

fig.update_layout(
    yaxis_title="%",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(fig, width="stretch")

# ==========================================
# BUSINESS CONCLUSION
# ==========================================

st.subheader(t["recommendation"])

if margin_change < -0.000001:
    st.error(t["negative"])
elif margin_change > 0.000001:
    st.success(t["positive"])
else:
    st.info(t["neutral"])

st.caption(t["note"])
