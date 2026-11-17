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
st.title(tr('Centrum automatyzacji biznesowej','Business Automation Center','Center for forretningsautomatisering'))
st.info(tr('Podgląd demonstracyjny. Harmonogram i wykonywanie procesów działają w wersji lokalnej, nie na tym serwerze.','Demonstration preview. Scheduling and execution run in the local edition, not on this server.','Demonstrationsvisning. Tidsplaner og kørsel fungerer i den lokale version, ikke på denne server.'))
r=performance('company')['rows'][0]
a,b,c=st.columns(3); a.metric(tr('Procesy','Processes','Processer'),5); b.metric(tr('Alerty w danych','Data alerts','Dataadvarsler'),sum([r['variance_pct']>1,r['on_time_pct']<95,r['quality_issue_pct']>2])); c.metric(tr('Transakcje','Transactions','Transaktioner'),num(r['transactions']))
for label, value, limit, alert in [(tr('Kontrola budżetu','Budget control','Budgetkontrol'),r['variance_pct'],1,r['variance_pct']>1),(tr('Monitoring terminowości','Delivery monitoring','Leveringsovervågning'),r['on_time_pct'],95,r['on_time_pct']<95),(tr('Monitoring jakości','Quality monitoring','Kvalitetsovervågning'),r['quality_issue_pct'],2,r['quality_issue_pct']>2)]:
 with st.container(border=True):
  st.subheader(label); a,b=st.columns(2); a.metric(tr('Wynik','Result','Resultat'),pct(value)); b.metric(tr('Próg','Threshold','Grænse'),pct(limit)); (st.warning if alert else st.success)(tr('Alert biznesowy','Business alert','Forretningsadvarsel') if alert else tr('W normie','Within limit','Inden for grænsen'))
st.subheader(tr('Harmonogram lokalny','Local schedule','Lokal tidsplan'))
st.table(pd.DataFrame({tr('Proces','Process','Proces'):[tr('Kursy NBP','NBP rates','NBP-kurser'),tr('Trzy kontrole biznesowe','Three business checks','Tre forretningskontroller'),tr('Raport AI','AI report','AI-rapport')],tr('Dni','Days','Dage'):[tr('Pon.–pt.','Mon–Fri','Man–fre'),tr('Pon.–pt.','Mon–Fri','Man–fre'),tr('Poniedziałek','Monday','Mandag')],tr('Godzina','Time','Tid'):['12:30','07:00','08:00']}))
st.caption(tr('W paczce nie było bazy historii automatyzacji; nie prezentujemy fikcyjnych wykonań.','Execution history was not included in the uploaded package; no fictional runs are shown.','Kørselshistorik var ikke med i pakken; ingen fiktive kørsler vises.'))
