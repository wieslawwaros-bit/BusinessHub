import streamlit as st
import pandas as pd
import plotly.express as px
from translations import get_language, format_money, format_percent, format_number
from demo_queries import performance, concentration, delivery_comparison, query
lang = get_language()
def tr(pl,en,da): return {'pl':pl,'en':en,'da':da}.get(lang,pl)
def money(v): return format_money(v,lang)
def pct(v): return format_percent(v,lang)
def num(v): return format_number(v,lang,0)
st.title(tr('Analityk biznesowy AI','AI Business Analyst','AI-forretningsanalytiker'))
st.info(tr('Wersja internetowa: demonstracja wyników. Lokalny model AI nie jest uruchamiany.', 'Online edition: demonstration of results. The local AI model is not running.', 'Onlineversion: demonstration af resultater. Den lokale AI-model kører ikke.'))
r=performance('company')['rows'][0]
report=tr(
 f"### Przykładowy raport menedżerski\nOkres: {r['period_start']} – {r['period_end']}. Przeanalizowano {num(r['transactions'])} transakcji i {num(r['suppliers'])} dostawców.\n\n- Zakupy: {money(r['spend_pln'])}\n- Przekroczenie budżetu: {money(r['variance_pln'])} ({pct(r['variance_pct'])})\n- Terminowość: {pct(r['on_time_pct'])}\n- Problemy jakościowe: {pct(r['quality_issue_pct'])}\n\n**Rekomendacje:** zbadać przyczyny odchyleń kosztowych i opóźnień; zweryfikować reklamacje i krytyczność materiałów. Same KPI nie przesądzają o przyczynach.",
 f"### Sample management report\nPeriod: {r['period_start']} – {r['period_end']}. {num(r['transactions'])} transactions and {num(r['suppliers'])} suppliers.\n\n- Purchases: {money(r['spend_pln'])}\n- Budget overspend: {money(r['variance_pln'])} ({pct(r['variance_pct'])})\n- On-time delivery: {pct(r['on_time_pct'])}\n- Quality issues: {pct(r['quality_issue_pct'])}\n\n**Recommendations:** investigate cost deviations and delays; review quality claims and material criticality. KPIs alone do not establish causes.",
 f"### Eksempel på ledelsesrapport\nPeriode: {r['period_start']} – {r['period_end']}. {num(r['transactions'])} transaktioner og {num(r['suppliers'])} leverandører.\n\n- Indkøb: {money(r['spend_pln'])}\n- Budgetoverskridelse: {money(r['variance_pln'])} ({pct(r['variance_pct'])})\n- Rettidige leveringer: {pct(r['on_time_pct'])}\n- Kvalitetsproblemer: {pct(r['quality_issue_pct'])}\n\n**Anbefalinger:** undersøg årsager til omkostningsafvigelser og forsinkelser; vurder reklamationer og materialernes kritikalitet. KPI'er alene fastslår ikke årsagerne.")
label=tr('Przykład opracowany na podstawie SQL, nie wygenerowany na żywo przez AI.','SQL-based sample, not generated live by AI.','SQL-baseret eksempel, ikke genereret live af AI.')
st.caption(label); st.markdown(report)
st.download_button(tr('Pobierz raport','Download report','Download rapport'),label+'\n\n'+report,file_name=f'Demo_Report_{lang}.md')
