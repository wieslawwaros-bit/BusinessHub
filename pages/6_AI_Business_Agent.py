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
st.title(tr('Agent biznesowy AI','AI Business Agent','AI-forretningsagent'))
st.info(tr('Wersja internetowa: demonstracja wyników. Lokalny model AI nie jest uruchamiany.', 'Online edition: demonstration of results. The local AI model is not running.', 'Onlineversion: demonstration af resultater. Den lokale AI-model kører ikke.'))
st.caption(tr('Wybierz przykładowe pytanie. Wyniki są obliczane bezpośrednio z bazy SQL, bez AI.','Choose a sample question. Results are calculated directly from SQL, without AI.','Vælg et eksempelspørgsmål. Resultater beregnes direkte fra SQL uden AI.'))
options=[tr('Największe przekroczenia budżetu','Largest budget overruns','Største budgetoverskridelser'),tr('Porównanie KPI: 2025 i 2026','KPI comparison: 2025 and 2026','KPI-sammenligning: 2025 og 2026'),tr('Koncentracja zakupów','Supplier concentration','Leverandørkoncentration'),tr('Pogorszenie terminowości','Delivery deterioration','Fald i leveringspræcision')]
choice=st.selectbox(tr('Przykładowe pytanie','Sample question','Eksempelspørgsmål'),options)
supplier=tr('Dostawca','Supplier','Leverandør'); spend=tr('Zakupy (PLN)','Purchases (PLN)','Indkøb (PLN)'); variance=tr('Odchylenie (PLN)','Variance (PLN)','Afvigelse (PLN)'); delivery=tr('Terminowość (%)','On-time delivery (%)','Rettidige leveringer (%)'); quality=tr('Problemy jakościowe (%)','Quality issues (%)','Kvalitetsproblemer (%)'); share=tr('Udział (%)','Share (%)','Andel (%)'); year=tr('Rok','Year','År')
if choice==options[0]:
 df=pd.DataFrame(performance(limit=5,min_transactions=30)['rows'])[['group_name','spend_pln','variance_pln','variance_pct']].rename(columns={'group_name':supplier,'spend_pln':spend,'variance_pln':variance,'variance_pct':tr('Odchylenie (%)','Variance (%)','Afvigelse (%)')})
 st.dataframe(df,hide_index=True); st.plotly_chart(px.bar(df,x=variance,y=supplier,orientation='h',color_discrete_sequence=['#E56C78']).update_yaxes(autorange='reversed'),width='stretch')
elif choice==options[1]:
 df=pd.DataFrame(performance('year','period')['rows'])[['group_name','spend_pln','on_time_pct','quality_issue_pct','variance_pln']].rename(columns={'group_name':year,'spend_pln':spend,'on_time_pct':delivery,'quality_issue_pct':quality,'variance_pln':variance})
 st.caption(tr('Pełny 2025; 2026 do 15 listopada. Sumy nie są w pełni porównywalne.','Full 2025; 2026 through 15 November. Totals are not directly comparable.','Hele 2025; 2026 til 15. november. Totaler er ikke direkte sammenlignelige.'))
 st.dataframe(df,hide_index=True)
 for field in [spend,delivery,quality,variance]: st.plotly_chart(px.bar(df,x=year,y=field).update_xaxes(type='category'),width='stretch')
elif choice==options[2]:
 r=concentration(); a,b=st.columns(2); a.metric('TOP 5',pct(r['top_5_share_pct'])); b.metric('TOP 10',pct(r['top_10_share_pct']))
 df=pd.DataFrame(r['rows']).rename(columns={'supplier_name':supplier,'share_pct':share,'spend_pln':spend}); st.plotly_chart(px.bar(df,x=share,y=supplier,orientation='h').update_yaxes(autorange='reversed'),width='stretch'); st.dataframe(df,hide_index=True)
 st.caption(tr('Koncentracja nie przesądza o ryzyku zależności od dostawców.','Concentration alone does not establish supplier dependence risk.','Koncentration alene fastslår ikke risikoen for leverandørafhængighed.'))
else:
 df=pd.DataFrame(delivery_comparison()['rows'])[['supplier_name','on_time_2025','on_time_2026','change_pp']].rename(columns={'supplier_name':supplier,'on_time_2025':'2025','on_time_2026':'2026','change_pp':tr('Zmiana (p.p.)','Change (pp)','Ændring (pp)')}); st.dataframe(df,hide_index=True); st.plotly_chart(px.bar(df,x=supplier,y=['2025','2026'],barmode='group',labels={'value':delivery}),width='stretch'); st.caption(tr('Minimum 30 transakcji w każdym roku. 2026 do 15 listopada.','At least 30 transactions per year. 2026 through 15 November.','Mindst 30 transaktioner pr. år. 2026 til 15. november.'))
