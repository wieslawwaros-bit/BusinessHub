
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from translations import (
    get_language,
    get_text,
    format_number,
    format_percent,
)

# ==========================================
# EXCHANGE RATE ANALYTICS
# ==========================================

st.set_page_config(
    page_title="Exchange Rates | BusinessHub",
    page_icon="💱",
    layout="wide",
)

# ==========================================
# LANGUAGE / JĘZYK / SPROG
# ==========================================

if "app_language" in st.session_state:
    st.session_state["_language_choice"] = (
        st.session_state["app_language"]
    )

language = get_language()
t = get_text(language)

REPORT_TITLES = {
    "pl": "Analiza kursów walut",
    "en": "Exchange Rate Analytics",
    "da": "Valutakursanalyse",
}

REPORT_DESCRIPTIONS = {
    "pl": "Analiza historycznych kursów walut NBP",
    "en": "Historical NBP exchange rate analysis",
    "da": "Analyse af historiske valutakurser fra NBP",
}

# ==========================================
# DATABASE / BAZA DANYCH
# ==========================================

database_path = (
    Path(__file__).resolve().parent
    / "businesshub.db"
)

try:
    with sqlite3.connect(database_path) as connection:
        df = pd.read_sql_query(
            """
            SELECT waluta, data, kurs
            FROM kursy_walut
            ORDER BY data ASC
            """,
            connection,
        )

except (sqlite3.Error, pd.errors.DatabaseError) as error:
    st.error(f"{t['db_error']}: {error}")
    st.stop()

if df.empty:
    st.warning(t["no_data"])
    st.stop()

df["data"] = pd.to_datetime(
    df["data"],
    errors="coerce",
)

df = df.dropna(subset=["data"])

if df.empty:
    st.warning(t["no_data"])
    st.stop()

# ==========================================
# HEADER / NAGŁÓWEK
# ==========================================

st.title(REPORT_TITLES[language])
st.caption(REPORT_DESCRIPTIONS[language])

st.divider()

# ==========================================
# FILTERS / FILTRY
# ==========================================

col_currency, col_period = st.columns(2)

with col_currency:
    currency = st.selectbox(
        t["currency"],
        ["EUR", "USD", "DKK"],
    )

with col_period:
    period = st.selectbox(
        t["period"],
        [7, 30, 60, 90],
        index=3,
    )

currency_data = (
    df[df["waluta"] == currency]
    .sort_values("data")
    .tail(period)
    .copy()
)

if currency_data.empty:
    st.warning(t["no_data"])
    st.stop()

# ==========================================
# CALCULATIONS / OBLICZENIA
# ==========================================

latest = currency_data.iloc[-1]

previous = (
    currency_data.iloc[-2]
    if len(currency_data) > 1
    else None
)

change = None

if previous is not None and previous["kurs"] != 0:
    change = (
        latest["kurs"] / previous["kurs"] - 1
    ) * 100

# ==========================================
# KPI DASHBOARD
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=t["latest_rate"],
        value=format_number(
            latest["kurs"], language, 4
        ),
    )

with col2:
    st.metric(
        label=t["rate_change"],
        value=(
            format_percent(change, language, True)
            if change is not None
            else "—"
        ),
    )

with col3:
    st.metric(
        label=t["observations"],
        value=format_number(
            len(currency_data), language, 0
        ),
    )

st.caption(
    f"{t['rate_date']}: "
    f"{latest['data'].strftime('%Y-%m-%d')}"
)

st.divider()

# ==========================================
# INTERACTIVE CHART / WYKRES
# ==========================================

st.subheader(
    f"{t['rate_history']} — {currency}/PLN"
)

fig = px.line(
    currency_data,
    x="data",
    y="kurs",
    markers=True,
    labels={
        "data": t["date"],
        "kurs": t["rate"],
    },
)

fig.update_traces(
    line=dict(
        color="#38A3F1",
        width=3,
    ),
    marker=dict(size=5),
)

fig.update_layout(
    xaxis_title=t["date"],
    yaxis_title=t["rate"],
    hovermode="x unified",
    margin=dict(
        l=15,
        r=15,
        t=20,
        b=15,
    ),
)

st.plotly_chart(
    fig,
    width="stretch",
)

# ==========================================
# DATA INFORMATION
# ==========================================

st.caption(t["source"])
st.caption(t["not_realtime"])
