
import streamlit as st

# ==========================================
# BUSINESS INTELLIGENCE & AI AUTOMATION HUB
# CENTRAL LANGUAGE SYSTEM
# ==========================================

LANGUAGES = {
    "pl": "🇵🇱 Polski",
    "en": "🇬🇧 English",
    "da": "🇩🇰 Dansk",
}

TRANSLATIONS = {
    "pl": {
        "app_title": "Business Intelligence & AI Automation Hub",
        "dashboard": "Panel analityczny",
        "dashboard_desc": "Analiza historycznych kursów walut NBP",
        "fx_title": "Analiza ryzyka walutowego i zakupów",
        "fx_desc": "Wpływ kursów walut na koszty zakupów",
        "currency": "Wybierz walutę",
        "order_currency": "Waluta zamówienia",
        "order_value": "Wartość zamówienia",
        "latest_rate": "Ostatni kurs NBP",
        "rate_change": "Zmiana względem poprzedniego notowania",
        "rate_history": "Historia kursu",
        "date": "Data",
        "rate": "Kurs PLN",
        "rate_date": "Data kursu NBP",
        "budget_rate": "Kurs budżetowy PLN",
        "budget_cost": "Koszt budżetowy",
        "current_cost": "Koszt według NBP",
        "cost_variance": "Odchylenie kosztu",
        "variance_pct": "Odchylenie procentowe",
        "conclusion": "Wniosek z analizy",
        "increase": "Wzrost kosztów zakupu względem budżetu.",
        "decrease": "Oszczędność względem budżetu.",
        "neutral": "Brak odchylenia względem budżetu.",
        "no_data": "Brak danych dla wybranej waluty.",
        "db_error": "Nie udało się odczytać bazy danych.",
        "simulation": "Symulacja oparta na ostatnim kursie NBP zapisanym w bazie.",
        "warning": "Niekorzystne odchylenie kosztu.",
        "favorable": "Korzystne odchylenie kosztu.",
        "period": "Liczba ostatnich notowań",
        "observations": "Dostępne notowania",
        "source": "Źródło: Narodowy Bank Polski",
        "not_realtime": "Ostatni opublikowany kurs NBP — nie jest to kurs transakcyjny ani notowanie w czasie rzeczywistym.",
    },

    "en": {
        "app_title": "Business Intelligence & AI Automation Hub",
        "dashboard": "Analytics Dashboard",
        "dashboard_desc": "Historical NBP exchange rate analysis",
        "fx_title": "FX Risk & Purchasing Analysis",
        "fx_desc": "Exchange rate impact on purchasing costs",
        "currency": "Select currency",
        "order_currency": "Purchase order currency",
        "order_value": "Purchase order value",
        "latest_rate": "Latest NBP exchange rate",
        "rate_change": "Change from previous quotation",
        "rate_history": "Exchange rate history",
        "date": "Date",
        "rate": "Exchange rate PLN",
        "rate_date": "NBP rate date",
        "budget_rate": "Budget exchange rate PLN",
        "budget_cost": "Budget cost",
        "current_cost": "Cost at NBP rate",
        "cost_variance": "Cost variance",
        "variance_pct": "Percentage variance",
        "conclusion": "Analysis conclusion",
        "increase": "Purchasing costs increased against budget.",
        "decrease": "Savings compared with budget.",
        "neutral": "No variance against budget.",
        "no_data": "No data available for the selected currency.",
        "db_error": "Unable to read the database.",
        "simulation": "Simulation based on the latest NBP rate stored in the database.",
        "warning": "Unfavorable cost variance.",
        "favorable": "Favorable cost variance.",
        "period": "Number of latest quotations",
        "observations": "Available quotations",
        "source": "Source: National Bank of Poland",
        "not_realtime": "Latest published NBP rate — not a transaction rate or real-time quotation.",
    },

    "da": {
        "app_title": "Business Intelligence & AI Automation Hub",
        "dashboard": "Analyseoversigt",
        "dashboard_desc": "Analyse af historiske valutakurser fra NBP",
        "fx_title": "Valutarisiko og indkøbsanalyse",
        "fx_desc": "Valutakursernes indvirkning på indkøbsomkostninger",
        "currency": "Vælg valuta",
        "order_currency": "Ordrevaluta",
        "order_value": "Ordreværdi",
        "latest_rate": "Seneste valutakurs fra NBP",
        "rate_change": "Ændring siden forrige notering",
        "rate_history": "Valutakurshistorik",
        "date": "Dato",
        "rate": "Valutakurs i PLN",
        "rate_date": "Dato for NBP-kursen",
        "budget_rate": "Budgetteret valutakurs i PLN",
        "budget_cost": "Budgetteret omkostning",
        "current_cost": "Omkostning ved NBP-kurs",
        "cost_variance": "Omkostningsafvigelse",
        "variance_pct": "Procentvis afvigelse",
        "conclusion": "Konklusion på analysen",
        "increase": "Indkøbsomkostningerne er steget i forhold til budgettet.",
        "decrease": "Besparelse i forhold til budgettet.",
        "neutral": "Ingen afvigelse fra budgettet.",
        "no_data": "Ingen data for den valgte valuta.",
        "db_error": "Databasen kunne ikke læses.",
        "simulation": "Beregningen er baseret på den seneste NBP-kurs i databasen.",
        "warning": "Ugunstig omkostningsafvigelse.",
        "favorable": "Gunstig omkostningsafvigelse.",
        "period": "Antal seneste noteringer",
        "observations": "Tilgængelige noteringer",
        "source": "Kilde: Polens nationalbank (NBP)",
        "not_realtime": "Seneste offentliggjorte NBP-kurs — ikke en transaktionskurs eller realtidskurs.",
    },
}


def get_language():
    """Display one language selector and persist the choice across pages."""

    if "app_language" not in st.session_state:
        st.session_state["app_language"] = "pl"

    def update_language():
        st.session_state["app_language"] = st.session_state["_language_choice"]

    current = st.session_state["app_language"]

    # Widget values may be cleared when navigating between Streamlit pages.
    if "_language_choice" not in st.session_state:
        st.session_state["_language_choice"] = current

    with st.sidebar:
        st.selectbox(
            "🌐 Language / Język / Sprog",
            options=list(LANGUAGES.keys()),
            format_func=lambda code: LANGUAGES[code],
            key="_language_choice",
            on_change=update_language,
        )

    return st.session_state["app_language"]


def get_text(language):
    """Return translations for the selected language."""
    return TRANSLATIONS.get(language, TRANSLATIONS["pl"])


def format_number(value, language, decimals=2):
    """Format numbers according to the selected language."""

    result = f"{value:,.{decimals}f}"

    if language == "en":
        return result

    if language == "da":
        return result.replace(",", "X").replace(".", ",").replace("X", ".")

    return result.replace(",", " ").replace(".", ",")


def format_money(value, language):
    """Format financial values in PLN."""
    return f"{format_number(value, language)} PLN"


def format_percent(value, language, signed=False):
    """Format percentage values."""
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{format_number(value, language)}%"
