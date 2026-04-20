import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from weasyprint import HTML, CSS # Sostituito FPDF con WeasyPrint
import os
import base64
import datetime
import unicodedata
import json
import gspread
from google.oauth2.service_account import Credentials

# --- 0. CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="30SecondsToGuide", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️", layout="centered")

# --- INJECTION JAVASCRIPT PER UMAMI ---
def set_social_headers():
    SOCIAL_IMAGE_URL = "https://raw.githubusercontent.com/Fax79/30secondstoguide/main/logo.png"
    meta_tags = f"""
    <meta property="og:title" content="30SecondsToGuide - La tua guida di viaggio IA" />
    <meta property="og:description" content="Da zero a local in 30 secondi. Crea itinerari personalizzati e scarica guide PDF gratuite." />
    <meta property="og:image" content="{SOCIAL_IMAGE_URL}" />
    <meta property="og:url" content="https://www.30secondstoguide.it" />
    """
    st.markdown(meta_tags, unsafe_allow_html=True)
    umami_injection = """
        <script>
            var parentHead = window.parent.document.getElementsByTagName("head")[0];
            var script = window.parent.document.createElement("script");
            script.defer = true;
            script.src = "https://cloud.umami.is/script.js";
            script.setAttribute("data-website-id", "897aa2b4-2423-49b6-978d-c1f36c84c4b3");
            if (!parentHead.querySelector('script[src="https://cloud.umami.is/script.js"]')) {
                parentHead.appendChild(script);
            }
        </script>
    """
    components.html(umami_injection, height=0, width=0)

set_social_headers()

# --- CONFIGURAZIONE GOOGLE SHEETS & API ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "30Seconds_Stats"

def get_db_connection():
    try:
        if "gcp_service_account" not in st.secrets: return None
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        return gspread.authorize(creds).open(SHEET_NAME).sheet1
    except: return None

def add_log(city_name, lang_code):
    sheet = get_db_connection()
    if sheet:
        timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
        sheet.append_row([timestamp, city_name, "GUIDE_ONLY", "-", "-", "-", "-", lang_code])

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ API Key missing!")
    st.stop()

# --- LINK AFFILIATI ---
HOTEL_LINK = "https://www.expedia.com" 
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
TIQETS_LINK = "https://tiqets.tpx.lt/abHnK4vL"
ESIM_LINK = "https://go.saily.site/aff_c?offer_id=126&aff_id=13541"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&cod_descuento=30SECONDSTOGUIDE&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn"

# --- NUOVA FUNZIONE PDF (WEASYPRINT) ---
def create_pdf(text, city, lang_code="IT"):
    # 1. Logica Titolo Dinamico (Regola 12/24)
    city_upper = city.strip().upper()
    if len(city_upper) > 24:
        city_upper = city_upper[:21] + "..."
    
    if 12 < len(city_upper) <= 24 and " " in city_upper:
        words = city_upper.split()
        mid = len(words) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        html_city = f"{line1}<br>{line2[:-1]}<span class='last-letter'>{line2[-1]}.</span>"
    else:
        html_city = f"{city_upper[:-1]}<span class='last-letter'>{city_upper[-1]}.</span>"

    # 2. Stringhe Localizzate
    strings = {
        "IT": {"label": "Pocket Guide", "sub": "Guida turistica completa:<br>Itinerari, Storia e Cultura", "disc": "Guida gratuita. Nell'ultima pagina sconti esclusivi per supportarci. <strong>Buon viaggio!</strong>", "planner": "Travel Planner", "cta": "PRENOTA ORA", "insight": "Consiglio Pratico"},
        "EN": {"label": "Pocket Guide", "sub": "Complete Travel Guide:<br>Itineraries, History and Culture", "disc": "Free guide. See last page for exclusive discounts. <strong>Safe travels!</strong>", "planner": "Travel Planner", "cta": "BOOK NOW", "insight": "Travel Insight"}
    }[lang_code]

    # 3. Formattazione Contenuto (Injection Box Sezione)
    formatted_body = ""
    lines = text.split('\n')
    for line in lines:
        if line.startswith('## '):
            title = line.replace('## ', '').strip()
            formatted_body += f"<h2>{title}</h2>"
            # Iniezione automatica in base alla sezione
            if any(x in title.upper() for x in ["DORMIRE", "SLEEP", "HOTEL"]):
                formatted_body += f'<div class="section-service-box"><span class="service-tag">{strings["insight"]}</span><a href="{HOTEL_LINK}" class="service-cta">{strings["cta"]}</a></div>'
            elif any(x in title.upper() for x in ["ARRIVARE", "GETTING", "VOLI"]):
                formatted_body += f'<div class="section-service-box"><span class="service-tag">{strings["insight"]}</span><a href="{FLIGHT_LINK}" class="service-cta">{strings["cta"]}</a></div>'
        elif line.startswith('### '):
            formatted_body += f"<h3>{line.replace('### ', '')}</h3>"
        elif line.startswith('* ') or line.startswith('- '):
            formatted_body += f"<li>{line[2:]}</li>"
        elif line.strip():
            # Effetto 3: Link evidenziatore (se presente URL nel testo)
            formatted_body += f"<p>{line}</p>"

    # 4. Template HTML Unificato
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 0; }}
            body {{ margin: 0; padding: 0; font-family: 'Helvetica', sans-serif; background-color: #faf9f6; color: #1a1a1a; }}
            .paper {{ background-image: linear-gradient(rgba(26,26,26,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(26,26,26,0.03) 1px, transparent 1px), url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E"); background-size: 40px 40px, 200px 200px; }}
            .cover {{ height: 297mm; display: flex; flex-direction: column; justify-content: center; padding: 60px; position: relative; page-break-after: always; }}
            .design-accent {{ position: absolute; top: 120px; left: 45px; width: 120px; height: 200px; border-top: 12px solid #1a1a1a; border-left: 12px solid #1a1a1a; }}
            .city-name {{ font-size: 65px; font-weight: 900; color: #e67e22; line-height: 0.95; margin: 0 0 0 20px; text-transform: uppercase; }}
            .last-letter {{ color: #1a1a1a; }}
            .description-box {{ margin: 45px 0 0 20px; padding: 25px; background: #fff; border-left: 4px solid #1a1a1a; max-width: 460px; box-shadow: 8px 8px 0 rgba(0,0,0,0.05); font-size: 14px; }}
            .content {{ padding: 60px; min-height: 297mm; }}
            .section-service-box {{ margin: 40px 0; padding: 25px; position: relative; background: #faf9f6; border: 1px solid rgba(0,0,0,0.1); box-shadow: 8px 8px 0 rgba(0,0,0,0.05); }}
            .section-service-box::before {{ content: ""; position: absolute; top: -5px; left: -5px; width: 40px; height: 60px; border-top: 8px solid #1a1a1a; border-left: 8px solid #1a1a1a; }}
            .service-tag {{ font-size: 11px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; display: block; margin-bottom: 10px; }}
            .service-cta {{ font-size: 32px; font-weight: 900; color: #e67e22; text-decoration: none; }}
            .service-cta::after {{ content: "."; color: #1a1a1a; }}
            .footer {{ padding: 40px 60px; border-top: 1px solid #eee; display: flex; justify-content: space-between; background: #fff; }}
            .brand {{ font-weight: 900; color: #e67e22; }}
        </style>
    </head>
    <body>
        <div class="paper">
            <div class="cover">
                <div class="design-accent"></div>
                <div style="font-size: 13px; font-weight: 800; letter-spacing: 5px; margin-left: 20px; text-transform: uppercase;">{strings['label']}</div>
                <h1 class="city-name">{html_city}</h1>
                <div style="font-size: 20px; color: #7f8c8d; margin-left: 20px; margin-top: 20px;">{strings['sub']}</div>
                <div class="description-box">{strings['disc']}</div>
            </div>
            <div class="content">
                {formatted_body}
            </div>
            <div class="content" style="page-break-before: always; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 13px; font-weight: 800; letter-spacing: 5px; text-transform: uppercase;">{strings['planner']}</div>
                <div class="section-service-box" style="margin-top: 60px;">
                    <a href="{HOTEL_LINK}" class="service-cta">BOOKIN<span class="last-letter">G.</span></a>
                </div>
                <div class="section-service-box">
                    <a href="{FLIGHT_LINK}" class="service-cta">FLIGHT<span class="last-letter">S.</span></a>
                </div>
                <div class="section-service-box">
                    <a href="{INSURANCE_LINK}" class="service-cta">INSURANC<span class="last-letter">E.</span></a>
                </div>
            </div>
            <div class="footer">
                <div class="brand">30SecondsToGuide</div>
                <div style="font-family: monospace; font-size: 11px;">WWW.30SECONDSTOGUIDE.IT</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()

# --- INTERFACCIA STREAMLIT (RIMASTA INVARIATA MA PULITA) ---
lang_opt = st.radio("Language:", ["Italiano", "English"], horizontal=True, label_visibility="collapsed")
lang_code = "IT" if lang_opt == "Italiano" else "EN"
ui = {
    "IT": {"h1": "Generatore Guide Turistiche", "sub": "Da zero a local in mezzo minuto.", "btn": "Genera Guida PDF PRO", "spin": "Stiamo scrivendo la tua guida..."},
    "EN": {"h1": "AI Travel Guide Generator", "sub": "From zero to local in 30 seconds.", "btn": "Generate PRO PDF Guide", "spin": "Writing your guide..."}
}[lang_code]

st.markdown(f"<h1 style='text-align: center;'>{ui['h1']}</h1><p style='text-align: center; color: #E67E22;'>{ui['sub']}</p>", unsafe_allow_html=True)

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo...")

if st.button(ui["btn"], type="primary", use_container_width=True):
    if city_name:
        add_log(city_name, lang_code)
        with st.spinner(ui["spin"]):
            model = genai.GenerativeModel("gemini-2.0-flash")
            # Prompt semplificato per evitare tabelle e forzare la struttura
            prompt = f"Scrivi una guida dettagliata per {city_name} in {lang_opt}. Usa titoli ## per sezioni come Dove Dormire, Cosa Vedere, Arrivare. NO TABELLE."
            response = model.generate_content(prompt)
            pdf_bytes = create_pdf(response.text, city_name, lang_code)
            st.download_button("⬇️ SCARICA GUIDA PDF", data=pdf_bytes, file_name=f"Guide_{city_name}.pdf", mime="application/pdf", use_container_width=True)
