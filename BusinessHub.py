from pathlib import Path
import streamlit as st
from translations import get_language

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='BusinessHub', layout='wide', page_icon='📊')

MODULES = [
('Exchange_Rates.py','Exchange Rates','💱','Kursy walut NBP i ich historia','NBP exchange rates and history','NBP-valutakurser og historik'),
('pages/1_FX_Risk.py','FX Risk','📉','Wpływ kursów walut na koszty zakupów','Impact of exchange rates on purchasing costs','Valutakursers betydning for indkøbsomkostninger'),
('pages/2_Profitability.py','Profitability','📊','Symulacja rentowności i marży projektów','Project profitability and margin simulation','Simulering af projekters rentabilitet og avance'),
('pages/3_Procurement.py','Procurement','🛒','Analiza zakupów, kosztów i dostawców','Analysis of purchasing, costs and suppliers','Analyse af indkøb, omkostninger og leverandører'),
('pages/4_Procurement_Insights.py','Procurement Insights','🔎','Wykrywanie odchyleń i ryzyka dostawców','Detection of deviations and supplier risks','Identifikation af afvigelser og leverandørrisici'),
('pages/5_AI_Business_Analyst.py','AI Business Analyst','📋','Generowanie raportów menedżerskich','Generation of management reports','Generering af ledelsesrapporter'),
('pages/6_AI_Business_Agent.py','AI Business Agent','💬','Analiza danych za pomocą pytań biznesowych','Data analysis through business questions','Dataanalyse gennem forretningsspørgsmål'),
('pages/7_Business_Automation.py','Business Automation','⚙️','Kontrole, harmonogramy i historia procesów','Checks, schedules and process history','Kontroller, tidsplaner og proceshistorik'),
]
T = {
'pl': ('Platforma wspierająca decyzje zarządcze','Transakcje zakupowe','Dostawcy','Moduły biznesowe','Procesy automatyzacji','Analiza biznesowa','Sztuczna inteligencja i automatyzacja','Otwórz moduł','Wersja demonstracyjna • Dane zakupowe są syntetyczne. Kursy walut pochodzą z NBP.','Brak pliku modułu'),
'en': ('A platform supporting management decisions','Purchase transactions','Suppliers','Business modules','Automation processes','Business Intelligence','Artificial Intelligence & Automation','Open module','Demo edition • Procurement data is synthetic. Exchange rates are sourced from NBP.','Module file missing'),
'da': ('En platform til støtte for ledelsesbeslutninger','Indkøbstransaktioner','Leverandører','Forretningsmoduler','Automatiseringsprocesser','Forretningsanalyse','Kunstig intelligens og automatisering','Åbn modul','Demoversion • Indkøbsdata er syntetiske. Valutakurser kommer fra NBP.','Modulfil mangler')}
PAGES = {m[0]: st.Page(m[0], title=m[1]) for m in MODULES if (ROOT/m[0]).is_file()}

def home():
    lang = get_language()
    if lang == 'dk': lang = 'da'
    if lang not in T: lang = 'pl'
    t = T[lang]
    ix = {'pl':3,'en':4,'da':5}[lang]
    st.title('BusinessHub')
    st.markdown('**Business Intelligence & AI Automation Platform**')
    st.caption(t[0])
    st.info({"pl":"Demo online: kursy NBP są zapisanym stanem bazy, AI i harmonogram pokazano w trybie demonstracyjnym.","en":"Online demo: NBP rates are a database snapshot; AI and scheduling are shown in demonstration mode.","da":"Online-demo: NBP-kurser er et øjebliksbillede; AI og tidsplaner vises i demonstrationstilstand."}[lang])
    cols = st.columns(4)
    for col, label, value in zip(cols,t[1:5],['10,000' if lang=='en' else '10 000','80',str(len(PAGES)),'5']):
        with col:
            with st.container(border=True): st.metric(label,value)
    st.divider()
    for heading, modules in [(t[5],MODULES[:5]),(t[6],MODULES[5:])]:
        st.subheader(heading)
        for start in range(0,len(modules),2):
            cols=st.columns(2)
            for col,m in zip(cols,modules[start:start+2]):
                with col:
                    with st.container(border=True):
                        st.markdown(f'### {m[2]} {m[1]}')
                        st.caption(m[ix])
                        if m[0] in PAGES:
                            st.page_link(PAGES[m[0]],label=t[7],width='stretch')
                        else:
                            st.warning(t[9]+': '+m[0])
    st.divider()
    st.caption(t[8])

nav = st.navigation([st.Page(home,title='BusinessHub',default=True), *PAGES.values()])
nav.run()
