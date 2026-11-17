
import sqlite3
import sys
from pathlib import Path

import streamlit as st

# ==========================================
# PROJECT PATH / ŚCIEŻKA PROJEKTU
# ==========================================

project_dir = Path(__file__).resolve().parent.parent

if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from translations import (
    get_language,
    get_text,
    format_number,
    format_money,
    format_percent,
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FX Risk & Purchasing Analysis",
    page_icon="💱",
    layout="wide",
)

# ==========================================
# LANGUAGE / JĘZYK / SPROG
# ==========================================

if "app_language" in st.session_state:
    st.session_state["_language_choice"] = st.session_state["app_language"]

language = get_language()
t = get_text(language)

# ==========================================
# DATABASE / BAZA DANYCH
# ==========================================

database_path = project_dir / "businesshub.db"

try:
    with sqlite3.connect(database_path) as connection:
        records = connection.execute(
            """
            SELECT waluta, data, kurs
            FROM kursy_walut
            ORDER BY data DESC
            """
        ).fetchall()

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
# USER INTERFACE / INTERFEJS
# ==========================================

st.title(t["fx_title"])
st.caption(t["fx_desc"])

st.divider()

col1, col2 = st.columns(2)

with col1:
    currency = st.selectbox(
        t["order_currency"],
        ["EUR", "USD", "DKK"],
    )

with col2:
    amount = st.number_input(
        t["order_value"],
        min_value=0.0,
        value=100000.0,
        step=1000.0,
        format="%.2f",
    )

# Demonstration budget rates
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
    key=f"budget_rate_{currency}",
)

current_rate = rates.get(currency)

if current_rate is None:
    st.warning(t["no_data"])
    st.stop()

st.metric(
    t["latest_rate"],
    format_number(current_rate, language, 4),
)

st.caption(f"{t['rate_date']}: {dates[currency]}")

st.divider()

# ==========================================
# CALCULATIONS / BEREGNINGER
# ==========================================

budget_cost = amount * budget_rate
current_cost = amount * current_rate

variance = current_cost - budget_cost

if budget_cost > 0:
    variance_pct = variance / budget_cost * 100
else:
    variance_pct = 0.0

# ==========================================
# RESULTS / WYNIKI
# ==========================================

st.subheader(t["conclusion"])

col_budget, col_actual = st.columns(2)

with col_budget:
    st.metric(
        t["budget_cost"],
        format_money(budget_cost, language),
    )

with col_actual:
    st.metric(
        t["current_cost"],
        format_money(current_cost, language),
    )

st.divider()

st.metric(
    t["cost_variance"],
    format_money(variance, language),
    delta=format_percent(
        variance_pct,
        language,
        signed=True,
    ),
    delta_color="inverse",
)

# ==========================================
# BUSINESS CONCLUSION
# ==========================================

if variance > 0:
    st.error(f"{t['warning']} {t['increase']}")

elif variance < 0:
    st.success(f"{t['favorable']} {t['decrease']}")

else:
    st.info(t["neutral"])

st.caption(t["simulation"])
st.caption(t["not_realtime"])
