import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from weasyprint import HTML
import base64
import datetime
import unicodedata
import os
import re
import json
import urllib.parse

# --- NUOVE IMPORTAZIONI PER GOOGLE SHEETS ---
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="Itinerary Wizard", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="Itinerary Wizard", page_icon="🧙‍♂️", layout="centered")

# --- INJECTION JAVASCRIPT PER UMAMI E SOCIAL ---
def set_social_headers():
    SOCIAL_IMAGE_URL = "https://raw.githubusercontent.com/Fax79/30secondstoguide/main/logo.png"
    
    meta_tags = f"""
    <meta property="og:title" content="Itinerary Wizard - 30SecondsToGuide" />
    <meta property="og:description" content="Il pianificatore di viaggi complessi con analisi del budget generato dall'IA." />
    <meta property="og:image" content="{SOCIAL_IMAGE_URL}" />
    <meta property="og:url" content="https://www.30secondstoguide.it" />
    <meta property="og:type" content="website" />
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

# --- CONFIGURAZIONE GOOGLE SHEETS ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "30Seconds_Stats"

def get_db_connection():
    """Connette a Google Sheets usando i Secrets."""
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        return None

def load_logs():
    """Carica i log da Google Sheets per l'admin panel."""
    sheet = get_db_connection()
    if sheet:
        try:
            return sheet.get_all_records()
        except:
            return []
    return []

def add_log(entry_data):
    """Aggiunge una nuova entry su Google Sheets."""
    sheet = get_db_connection()
    if sheet:
        try:
            row = [
                entry_data.get("timestamp", ""),
                entry_data.get("destination", ""),
                entry_data.get("budget", 0),
                entry_data.get("nights", 0),
                entry_data.get("adults", 0),
                entry_data.get("minors", 0),
                str(entry_data.get("minors_ages", [])),
                entry_data.get("lang", "-")
            ]
            sheet.append_row(row)
        except Exception as e:
            print(f"Errore salvataggio log: {e}")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

# ==========================================
# 🌐 CONFIGURAZIONE CROSS-PROMO & MONETIZZAZIONE
# ==========================================
GUIDE_APP_URL = "https://www.30secondstoguide.it" 

FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARD"
RENTAL_LINK = "https://clk.tradedoubler.com/click?p=284745&a=3480952"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://www.tiqets.com/?partner=30secondstoguide.it-185728"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARD&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
TRAIN_LINK = "https://www.omio.com"
GYG_LINK = "https://gyg.me/YAGbtbpK"
HOTEL_LINK = "https://www.expedia.com"
TOUR_LINK = "https://www.getyourguide.com"

# --- HELPER IMMAGINI ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def partner_button(label, link, image_file):
    if os.path.exists(image_file):
        try:
            img_base64 = get_base64_of_bin_file(image_file)
            html_code = f"""
            <a href="{link}" target="_blank">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:8px; border: 1px solid #e0e0e0; transition: transform 0.2s;">
            </a>
            <div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
                <a href="{link}" target="_blank" style="text-decoration: none; color: #E67E22; font-weight: bold; font-size: 0.9em;">{label} ➜</a>
            </div>
            """
            st.markdown(html_code, unsafe_allow_html=True)
        except:
            st.link_button(label, link, use_container_width=True)
    else:
        st.link_button(label, link, use_container_width=True)

# --- DIZIONARI LINGUA ---
LANGUAGES = {
    "IT": {
        "subtitle": "Il pianificatore di viaggi complessi con analisi del budget.",
        "info_box": "🧙‍♂️ Inserisci i dettagli per ricevere un Travel Plan completo.",
        "label_dest": "Destinazione (Città/Regione/Paese)",
        "place_dest": "Es. New York, Provenza, Giappone...",
        "label_budget": "Budget Totale (€)",
        "label_start": "Data Partenza",
        "label_end": "Data Ritorno",
        "label_adults": "Numero Adulti",
        "label_kids": "Numero Minorenni",
        "label_ages": "Età figlio",
        "label_desc": "Descrizione del viaggio (Opzionale)",
        "place_desc": "Es. Partenza da Milano, voglio fare scalo a Dubai. Mi interessano musei e trekking...",
        "help_desc": "Dettagli extra per l'AI.",
        "btn_generate": "✨ Crea il mio Travel Plan",
        "btn_download": "📥 SCARICA IL TRAVEL PLAN (PDF)",
        "msg_success": "✅ Travel Plan pronto!",
        "msg_warning_dest": "Inserisci una destinazione!",
        "msg_warning_long": "⚠️ Il viaggio è troppo lungo ({days} notti). Il limite massimo è di 40 notti.",
        "msg_warning_short": "⚠️ Hai scelto un periodo di una sola notte, verifica se è corretta la Data Ritorno.",
        "spinner": "🧙‍♂️ Sto elaborando il Travel Plan per {dest}...",
        "months": {1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile", 5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto", 9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"},
        "pax_adults": "Adulti",
        "pax_kids": "Ragazzi",
        "pdf_title": "Travel Plan Esclusivo",
        "pdf_generated": "GENERATO CON www.30secondstoguide.it",
        "pdf_promo": "Approfondisci la conoscenza delle città del tuo itinerario, crea le tue guide qui.",
        "pdf_travellers": "Viaggiatori",
        "pdf_date": "Date",
        "pdf_budget_target": "Budget Target",
        "pdf_page": "Pagina",
        "pdf_seen": "Già visti nella guida...",
        "pdf_others": "ALTRI SERVIZI INDISPENSABILI",
        # Keywords for PDF Parsing
        "key_chapter": "CAPITOLO",
        "key_verdict": "VERDETTO",
        "key_day": "GIORNO",
        # Ad Texts
        "ad_flight": "In {month} i prezzi aumentano? Inizia a monitorare ORA i migliori prezzi su Kiwi.com",
        "ad_esim": "eSim Saily: Internet immediato all'arrivo senza acquisto di SIM locali. 5$ di sconto con codice FABIOI3455",
        "ad_insur": "MAI senza Assicurazione Sanitaria: Clicca e sblocca il 10% DI SCONTO con Heymondo",
        "ad_hotel": "Stanze in Hotel quasi esaurite in {month}? Prenota ora su Expedia",
        "ad_transfer": "Transfer privati ad un prezzo WOW! da e per l'aeroporto",
        "ad_tiqets": "Non rischiare il tutto esaurito a {dest}. Assicurati il posto e le migliori offerte su Tiqets",
        "ad_car": "Viaggia in libertà e noleggia un auto: Tariffe esclusive con Sixt",
        "ad_train": "Treni e Bus: Prenota su Omio",
        "ad_rest": "Esplora al miglior prezzo! Prenota su GetYourGuide",
        # Sidebar
        "sb_book": "✈️ PRENOTAZIONI",
        "sb_exp": "🎟️ ESPERIENZE & ALTRO",
        "sb_tools": "🛠️ SERVIZI UTILI",
        "footer_title": "Come funziona Itinerary Wizard?",
        "footer_text": "Strumento di <strong>30SecondsToGuide</strong> per pianificare viaggi complessi analizzando il budget. Gratuito al 100%."
    },
    "EN": {
        "subtitle": "The complex trip planner with budget analysis.",
        "info_box": "🧙‍♂️ Enter details to receive a full Travel Plan.",
        "label_dest": "Destination (City/Region/Country)",
        "place_dest": "E.g. New York, Provence, Japan...",
        "label_budget": "Total Budget (€)",
        "label_start": "Departure Date",
        "label_end": "Return Date",
        "label_adults": "Adults",
        "label_kids": "Minors",
        "label_ages": "Age child",
        "label_desc": "Trip Description (Optional)",
        "place_desc": "E.g. Departing from London, want a layover in Dubai. Interested in museums and hiking...",
        "help_desc": "Extra details for AI.",
        "btn_generate": "✨ Create my Travel Plan",
        "btn_download": "📥 DOWNLOAD TRAVEL PLAN (PDF)",
        "msg_success": "✅ Travel Plan ready!",
        "msg_warning_dest": "Please enter a destination!",
        "msg_warning_long": "⚠️ Trip is too long ({days} nights). Maximum limit is 40 nights.",
        "msg_warning_short": "⚠️ You chose a single night trip, check if Return Date is correct.",
        "spinner": "🧙‍♂️ Processing Travel Plan for {dest}...",
        "months": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
        "pax_adults": "Adults",
        "pax_kids": "Teens/Kids",
        "pdf_title": "Exclusive Travel Plan",
        "pdf_generated": "GENERATED WITH www.30secondstoguide.it",
        "pdf_promo": "Deepen your knowledge of the cities in your itinerary, create your guides here.",
        "pdf_travellers": "Travelers",
        "pdf_date": "Dates",
        "pdf_budget_target": "Target Budget",
        "pdf_page": "Page",
        "pdf_seen": "Featured in this guide...",
        "pdf_others": "ESSENTIAL SERVICES",
        # Keywords for PDF Parsing
        "key_chapter": "CHAPTER",
        "key_verdict": "VERDICT",
        "key_day": "DAY",
        # Ad Texts
        "ad_flight": "Prices rising in {month}? Book now on Kiwi.com",
        "ad_esim": "eSim Saily: Instant internet on arrival without buying local SIMs",
        "ad_insur": "NEVER without Health Insurance: Get 10% off HERE with Heymondo",
        "ad_hotel": "Hotel rooms almost sold out in {month}? Book now on Expedia",
        "ad_transfer": "Private transfers at WOW prices! to and from the airport",
        "ad_tiqets": "Don't risk sold out in {dest}. Secure spots and best deals on Tiqets",
        "ad_car": "Travel freely and rent a car: Exclusive rates with Sixt",
        "ad_train": "Trains and Buses: Book on Omio",
        "ad_rest": "Discover at the best rate! Book on GetYourGuide",
        # Sidebar
        "sb_book": "✈️ BOOKINGS",
        "sb_exp": "🎟️ EXPERIENCES & MORE",
        "sb_tools": "🛠️ USEFUL SERVICES",
        "footer_title": "How does Itinerary Wizard work?",
        "footer_text": "Tool by <strong>30SecondsToGuide</strong> to plan complex trips analyzing the budget. 100% Free."
    }
}

# ==========================================
# GESTIONE LINK DINAMICI
# ==========================================
def inject_gyg_links(text_line, dest_name):
    """
    Intercetta i tag [TOUR: ...] generati dall'AI e li trasforma 
    in Deep Link affiliati per GetYourGuide.
    """
    tour_matches = re.findall(r'\[TOUR:\s*(.*?)\]', text_line)
    
    for tour in tour_matches:
        query_string = f"{tour} {dest_name}"
        query_encoded = urllib.parse.quote(query_string)
        
        search_link = f"https://www.getyourguide.it/s?q={query_encoded}&partner_id=UR2ZJHB&utm_medium=online_publisher"
        html_link = f"<a href='{search_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>{tour}</a>"
        
        text_line = text_line.replace(f"[TOUR: {tour}]", html_link)

    return text_line


# ==========================================
# 🧙‍♂️ PDF ENGINE (MULTILINGUA & WEASYPRINT)
# ==========================================
def create_complex_pdf(text, destination, meta_data, lang_code):
    
    ui = LANGUAGES[lang_code]

    def clean_text_for_pdf(text_input):
        if not text_input: return ""
                    
        # Sostituisce il grassetto markdown con tag HTML
        text_input = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_input)
        return text_input

    dest_clean = clean_text_for_pdf(destination)
    month_clean = clean_text_for_pdf(meta_data.get('month_name', ''))

    # Titolo Copertina
    city_upper = dest_clean.strip().upper()
    if len(city_upper) > 24:
        city_upper = city_upper[:21] + "..."
    if 12 < len(city_upper) <= 24 and " " in city_upper:
        words = city_upper.split()
        mid = len(words) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        html_city = f"{line1}<br>{line2[:-1]}<span class='last-letter-dot'>{line2[-1]}.</span>"
    else:
        html_city = f"{city_upper[:-1]}<span class='last-letter-dot'>{city_upper[-1]}.</span>"

    # Preparazione Body HTML
    formatted_body = ""
    lines = text.split('\n')
    inserted_ch1 = inserted_ch2 = inserted_ch3 = inserted_ch4 = False

    TRIGGER_CH = f"## {ui['key_chapter']}"
    TRIGGER_VERDICT = ui['key_verdict']
    TRIGGER_DAY = f"{ui['key_day']}"

    def make_html_box(link, cta, sub):
        # Isola l'ultima lettera e le assegna il grigio scuro/nero
        cta_html = f"{cta[:-1]}<span style='color: #1a1a1a;'>{cta[-1]}</span>"
        
        return f"""
        <div class="section-service-box">
            <span class="service-tag">LINK UTILI PER IL TUO VIAGGIO</span>
            <a href="{link}" target="_blank" class="service-cta">{cta_html}</a>
            <div class="service-sub">{sub}</div>
        </div>
        """

    for line in lines:
        clean_line = clean_text_for_pdf(line.strip())
        
        # --- SOSTITUZIONE DIRETTA PER HEYMONDO ---
        heymondo_link = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARDCONTEXT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
        heymondo_html = f"<a href='{heymondo_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Heymondo</a>"
        clean_line = re.sub(r'\bHeymondo\b', heymondo_html, clean_line, flags=re.IGNORECASE)

        # --- SOSTITUZIONE DIRETTA PER KIWI ---
        kiwi_link = "https://kiwi.tpx.lt/k6iWGXOK"
        kiwi_html = f"<a href='{kiwi_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Kiwi</a>"
        clean_line = re.sub(r'\bKiwi(?:\.com)?\b', kiwi_html, clean_line, flags=re.IGNORECASE)
        
        # --- SOSTITUZIONE DIRETTA PER SAILY ---
        saily_link = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARDTEXT"
        saily_html = f"<a href='{saily_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Saily</a>"
        clean_line = re.sub(r'\bSaily\b', saily_html, clean_line, flags=re.IGNORECASE)
        
        # --- ESECUZIONE DELLA FUNZIONE GYG SULLA RIGA CORRENTE ---
        clean_line = inject_gyg_links(clean_line, destination)
        
        if not clean_line:
            continue
        line_upper = clean_line.upper()
        
        # LOGICA INIEZIONE ANNUNCI 
        if f"{TRIGGER_CH} 2" in line_upper and not inserted_ch1:
            formatted_body += make_html_box(FLIGHT_LINK, "FLIGHTS", ui["ad_flight"].format(month=month_clean))
            formatted_body += make_html_box(ESIM_LINK, "INTERNET", ui["ad_esim"])
            formatted_body += make_html_box(INSURANCE_LINK, "INSURANCE", ui["ad_insur"])
            inserted_ch1 = True
        elif f"{TRIGGER_CH} 3" in line_upper and not inserted_ch2:
            formatted_body += make_html_box(HOTEL_LINK, "HOTEL", ui["ad_hotel"].format(month=month_clean))
            formatted_body += make_html_box(TRANSF_LINK, "TRANSFER", ui["ad_transfer"])
            inserted_ch2 = True
        elif f"{TRIGGER_CH} 4" in line_upper and not inserted_ch3:
            formatted_body += make_html_box(TIQETS_LINK, "TICKETS", ui["ad_tiqets"].format(dest=dest_clean))
            formatted_body += make_html_box(RENTAL_LINK, "RENTAL CAR", ui["ad_car"])
            formatted_body += make_html_box(TRAIN_LINK, "TRAIN & BUS", ui["ad_train"])
            inserted_ch3 = True
        elif f"{TRIGGER_CH} 5" in line_upper and not inserted_ch4:
            formatted_body += make_html_box(GYG_LINK, "TOURS", ui["ad_rest"])
            inserted_ch4 = True

        # PARSING ELEMENTI MARKDOWN
        if clean_line.startswith('## '):
            formatted_body += f"<h2 class='h2-title'>{clean_line.replace('## ', '')}</h2>"
        elif clean_line.startswith('### '):
            formatted_body += f"<h3 class='h3-title'>{clean_line.replace('### ', '')}</h3>"
        elif TRIGGER_VERDICT in line_upper:
            verdict_text = clean_line.replace('#', '').strip()
            formatted_body += f"<div class='verdict-box'>{verdict_text}</div>"
        elif clean_line.startswith('* ') or clean_line.startswith('- '):
            formatted_body += f"<li>{clean_line[2:]}</li>"
        elif re.match(r'^\d+\.', clean_line):
            formatted_body += f"<p><strong>{clean_line}</strong></p>"
        elif clean_line.startswith('# '):
            continue # Salta l'H1 per non duplicare la copertina
        else:
            formatted_body += f"<p>{clean_line}</p>"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 25mm 20mm 30mm 20mm;
                background-color: #faf9f6;
                background-image: 
                    linear-gradient(rgba(26, 26, 26, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(26, 26, 26, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;

                @bottom-left {{
                    content: "30SecondsToGuide";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 800;
                    color: #e67e22;
                    padding-bottom: 5mm;
                }}
                @bottom-right {{
                    content: "{ui['pdf_generated']}";
                    font-family: monospace;
                    font-size: 11px;
                    color: #1a1a1a;
                    opacity: 0.8;
                    padding-bottom: 5mm;
                }}
            }}

            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1a1a1a;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}

            .cover-container {{
                page-break-after: always;
                position: relative;
                padding-top: 80px;
            }}
            .design-accent-l {{
                position: absolute;
                top: 40px; left: -15px;
                width: 120px; height: 200px;
                border-top: 12px solid #1a1a1a;
                border-left: 12px solid #1a1a1a;
                z-index: -1;
            }}
            .category-label {{
                font-size: 13px; font-weight: 800; letter-spacing: 5px;
                text-transform: uppercase; margin-bottom: 12px;
                background: #faf9f6; display: inline-block; padding-right: 10px;
            }}
            .city-name {{
                font-size: 65px; font-weight: 900; text-transform: uppercase;
                margin: 0; line-height: 0.95; letter-spacing: -2px;
                color: #e67e22;
            }}
            .last-letter-dot {{ color: #1a1a1a; }}
            
            .description-box {{
                margin-top: 145px; padding: 25px; background-color: #ffffff;
                border-left: 4px solid #1a1a1a; max-width: 460px; font-size: 14px;
                color: #555; box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
            }}

            .content-container {{
                page-break-after: always;
            }}
            .h2-title {{
                text-transform: uppercase; font-weight: 900; letter-spacing: -1px;
                color: #e67e22; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #1a1a1a; display: inline-block;
                page-break-after: avoid; 
            }}
            .h3-title {{ 
                font-weight: 800; color: #1a1a1a; margin-top: 30px; margin-bottom: 10px; 
                page-break-after: avoid; 
            }}
            p, li {{ font-size: 14px; color: #333; margin-bottom: 10px; text-align: justify; }}
            li {{ margin-left: 20px; }}
            strong {{ color: #000000; font-weight: bold; }}

            .verdict-box {{
                margin: 30px 0; padding: 15px; background-color: #f8f9fa; 
                border-left: 5px solid #e67e22; font-weight: bold; color: #2c3e50;
            }}

            .section-service-box {{
                margin: 40px 0px; padding: 25px; position: relative;
                background-color: #ffffff;
                border: 1px solid rgba(26, 26, 26, 0.08);
                box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
                page-break-inside: avoid;
            }}
            .section-service-box::before {{
                content: ""; position: absolute; top: -6px; left: -6px;
                width: 40px; height: 40px;
                border-top: 8px solid #1a1a1a; border-left: 8px solid #1a1a1a;
            }}
            .service-tag {{
                font-size: 11px; font-weight: 800; letter-spacing: 4px;
                text-transform: uppercase; color: #1a1a1a; display: block; margin-bottom: 10px;
            }}
            .service-cta {{
                font-size: 30px; font-weight: 900; text-transform: uppercase;
                color: #e67e22; text-decoration: none; letter-spacing: -1.5px; line-height: 1; display: block;
            }}
            .service-cta::after {{ content: "."; color: #1a1a1a; }}
            .service-sub {{ font-size: 13px; color: #7f8c8d; margin-top: 8px; font-weight: 400; }}

        </style>
    </head>
    <body>

        <div class="cover-container">
            <div class="design-accent-l"></div>
            <div class="category-label">{ui['pdf_title']}</div>
            <h1 class="city-name">{html_city}</h1>
            <div class="description-box">
                <strong>{ui['pdf_date']}:</strong> {meta_data['dates']}<br>
                <strong>{ui['pdf_travellers']}:</strong> {meta_data['pax']}<br>
                <strong>{ui['pdf_budget_target']}:</strong> {meta_data['budget']}
            </div>
            
            <div style="margin-top: 60px; text-align: center;">
                <a href="{GUIDE_APP_URL}" style="display:inline-block; padding:15px 25px; background-color:#e67e22; color:white; text-decoration:none; font-weight:bold; border-radius:5px;">
                    {ui['pdf_promo']}
                </a>
            </div>
        </div>

        <div class="content-container">
            {formatted_body}
        </div>

    </body>
    </html>
    """

    return HTML(string=html_template).write_pdf()

# ==========================================
# 🖥️ INTERFACCIA UTENTE
# ==========================================

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("⏱️")
    
    # Session state fallback per sidebar labels
    if "lang_code" not in st.session_state:
        st.session_state["lang_code"] = "IT"
    ui_sb = LANGUAGES[st.session_state["lang_code"]]

    st.markdown("---")
    st.caption(ui_sb["sb_book"])
    partner_button("Kiwi", FLIGHT_LINK, "btn_kiwi.png")
    partner_button("Expedia", HOTEL_LINK, "btn_booking.png")
    partner_button("Welcome", TRANSF_LINK, "btn_wp.png")
    partner_button("Sixt", RENTAL_LINK, "btn_sixt.png")
    partner_button("Omio", TRAIN_LINK, "btn_omio.png")
    partner_button("Kiwitaxi", TAXI_LINK, "btn_taxi.png")
    st.caption(ui_sb["sb_exp"])
    partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png")
    partner_button("GetYourGuide", GYG_LINK, "btn_gyg.png")
    st.caption(ui_sb["sb_tools"])
    partner_button("Saily", ESIM_LINK, "btn_saily.png")
    partner_button("Radical", LUGGAGE_LINK, "btn_radical.png")
    partner_button("Heymondo", INSURANCE_LINK, "btn_heymondo.png")
    partner_button("Airhelp", REIMB_LINK, "btn_airhelp.png")
    with st.sidebar.expander("🔐 Admin Stats"):
        secret_pwd = st.text_input("Password", type="password")
        if secret_pwd == "fabio123":
            st.write("### 📊 Logs:")
            logs = load_logs()
            if logs:
                for log in list(reversed(logs))[:10]:
                    st.caption(f"🧙‍♂️ **{log.get('Destination', 'N/A')}**\n{log.get('Timestamp', '')} | € {log.get('Budget', 0)} | {log.get('Nights', 0)} n.")
            else:
                st.caption("No DB.")
    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")

# --- MAIN: SELETTORE LINGUA ---
col_lang_1, col_lang_2 = st.columns([3, 1]) 
with col_lang_2:
    lang_opt = st.radio(
        "Language:",
        ["🇮🇹 IT", "🇬🇧 EN"],
        horizontal=True,
        label_visibility="collapsed",
        key="lang_select_wiz"
    )

lang_code = "IT" if "IT" in lang_opt else "EN"
st.session_state["lang_code"] = lang_code 
ui = LANGUAGES[lang_code]

# --- MAIN: LOGO E TITOLO ---
if os.path.exists("logo.png"):
    col_sp1, col_img, col_sp2 = st.columns([3, 2, 3])
    with col_img: st.image("logo.png", use_container_width=True)

st.markdown(f"""
    <h1 style='text-align: center; color: #2C3E50; margin-bottom: 0; margin-top: -10px;'>
        Itinerary Wizard
    </h1>
    <p style='text-align: center; color: #E67E22; font-size: 1.2em; font-style: italic; margin-top: 5px;'>
        {ui["subtitle"]}
    </p>
    """, unsafe_allow_html=True)

st.write("")

# --- CSS HACK ---
st.markdown("""
<style>
div[data-testid="stPageLink-NavLink"] {
    background-color: #E67E22; border: 1px solid #d35400; border-radius: 8px;
    padding: 10px; text-align: center; transition: all 0.3s ease;
}
div[data-testid="stPageLink-NavLink"]:hover { background-color: #d35400; transform: scale(1.01); }
div[data-testid="stPageLink-NavLink"] p { color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.info(ui["info_box"])
    
    current_months = ui["months"]

    c_dest, c_bud = st.columns([2, 1])
    with c_dest: destination = st.text_input(ui["label_dest"], placeholder=ui["place_dest"])
    with c_bud: budget = st.number_input(ui["label_budget"], min_value=100, value=3000, step=100)
    
    def aggiorna_data_ritorno():
        if st.session_state.start_input: st.session_state.end_input = st.session_state.start_input + datetime.timedelta(days=1)

    c_start, c_end = st.columns(2)
    with c_start: start_date = st.date_input(ui["label_start"], value=datetime.date.today() + datetime.timedelta(days=30), min_value=datetime.date.today(), key="start_input", on_change=aggiorna_data_ritorno)
    with c_end:
        min_return_date = start_date + datetime.timedelta(days=1)
        if "end_input" not in st.session_state: st.session_state.end_input = min_return_date
        end_date = st.date_input(ui["label_end"], value=st.session_state.end_input, min_value=min_return_date, key="end_input")

    c_ad, c_kids = st.columns(2)
    with c_ad: adults = st.number_input(ui["label_adults"], min_value=1, value=2)
    with c_kids: kids = st.number_input(ui["label_kids"], min_value=0, value=0)

    kids_ages = []
    if kids > 0:
        st.caption(f"{ui['label_ages']}:")
        k_cols = st.columns(min(kids, 4))
        for i in range(kids):
            with k_cols[i % 4]:
                age = st.number_input(f"{ui['label_ages']} {i+1}", 0, 17, 10, key=f"kid_{i}")
                kids_ages.append(str(age))

    st.write("")
    travel_desc = st.text_area(ui["label_desc"], placeholder=ui["place_desc"], help=ui["help_desc"])

    duration_check = (end_date - start_date).days
    if duration_check == 1: st.warning(ui["msg_warning_short"])
    
    def reset_app():
        if 'wizard_pdf' in st.session_state: del st.session_state['wizard_pdf']
    
    is_generated = 'wizard_pdf' in st.session_state
    
    if st.button(ui["btn_generate"], type="primary", use_container_width=True, disabled=is_generated):
        if duration_check > 40:
            st.error(ui["msg_warning_long"].format(days=duration_check))
            st.stop()
        if not destination:
            st.warning(ui["msg_warning_dest"])
        else:
            pax_desc = f"{adults} {ui['pax_adults']}"
            if kids > 0: pax_desc += f", {kids} {ui['pax_kids']} ({', '.join(kids_ages)})"
            
            mese_partenza = current_months[start_date.month]
            timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
            
            add_log({
                "timestamp": timestamp, 
                "destination": destination, 
                "budget": budget, 
                "nights": duration_check, 
                "adults": adults, 
                "minors": kids, 
                "minors_ages": kids_ages,
                "lang": lang_code
            })
            
            with st.spinner(ui["spinner"].format(dest=destination)):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    if lang_code == "IT":
                        sys_prompt = "Agisci come un Travel Planner Senior. Non pianifichi solo un viaggio, pianifichi un viaggio su misura che massimizza il valore del budget."
                        rules_lang = "Usa SOLO l'alfabeto Latino/Italiano. Quando suggerisci un'escursione, un'attrazione, un tour o un museo specifico, SOLO E SOLTANTO SE SEI RAGIONEVOLMENTE CERTO CHE SI POSSA PRENOTARE TRAMITE GETYOURGUIDE ALLORA devi racchiudere il nome ESATTAMENTE in questo tag: [TOUR: Nome Attrazione]. Esempio: Ti consiglio di visitare il [TOUR: Colosseo]."
                        structure = f"""
                        # {destination.upper()}: [Sottotitolo]
                        **IL VERDETTO SUL BUDGET: € {budget}** (Stato: Lusso/Più che adeguato/Sufficiente/Stretto/Impossibile)
                        ## CAPITOLO 1: LA PREPARAZIONE (Voli, eSim, Assicurazione)
                        [Info trasporti ottimizza orari dei voli consultando dove possibile google flights se hai informazioni sulla città di partenza, reperisci gli ultimi prezzi da google flight se hai date precise e suggerisci Kiwi per la prenotazione sfruttando i travel hack. ATTENZIONE ALLA COERENZA CON LA DATA ODIERNA RISPETTO AI SUGGERIMENTI CHE DAI (es. se il volo è tra un mese non sugggerire di prenotare 6 mesi prima). Come eSim consiglia sempre Saily (NON per Italia/UE dove esiste roaming as at home), per l'assicurazione Heymondo con sconto 10%]
                        ## CAPITOLO 2: DOVE DORMIRE (Strategie alloggio)
                        ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (Dettagliato)
                        [Itinerario ottimizzato, razionalizza gli spostamenti in base alla distanza, a seconda del mezzo di trasporto massimizza le tappe con i tempo a disposizione. Prediligi attrazioni su Tiqets e Getyourguide. Scoperta del territorio]
                        ## CAPITOLO 4: COSA MANGIARE
                        [Piatti tipici, ristoranti (verifica su Tripadvisor i migliori per la fascia di prezzo compatibile con il budget e dai riferimenti puntuali), suggerisci i posti migliori per lo street food]
                        ## CAPITOLO 5: CALENDARIO CULTURALE
                        [Festival e ricorrenze]
                        ## CAPITOLO 6: CONTO ECONOMICO FINALE [includi sempre Voli internazionali se il viaggio li necessita per la stima del budget]
                        ## CAPITOLO 7: INFORMAZIONI PRATICHE
                        ## CAPITOLO 8: CONCLUSIONE
                        """
                    else:
                        sys_prompt = "Act as a Senior Travel Planner. You don't just plan a trip, you plan a tailor-made trip that maximizes budget value."
                        rules_lang = "Use ONLY Latin/English alphabet. When you suggest a specific excursion, attraction, tour, or museum, you MUST enclose the name EXACTLY in this tag: [TOUR: Attraction Name]. Example: I recommend visiting the [TOUR: Colosseum]."
                        structure = f"""
                        # {destination.upper()}: [Subtitle]
                        **THE VERDICT ON BUDGET: € {budget}** (Status: Luxury/More than adequate/Sufficient/Tight/Impossible)
                        ## CHAPTER 1: PREPARATION (Flights, eSim, Insurance)
                        [Transport info, Saily eSim, Heymondo insurance 10% off]
                        ## CHAPTER 2: WHERE TO SLEEP (Accommodation strategies)
                        ## CHAPTER 3: DAY BY DAY ITINERARY (Detailed)
                        ## CHAPTER 4: WHAT TO EAT
                        ## CHAPTER 5: CULTURAL CALENDAR
                        ## CHAPTER 6: FINAL FINANCIAL BREAKDOWN
                        ## CHAPTER 7: PRACTICAL INFORMATION
                        ## CHAPTER 8: CONCLUSION
                        """

                    prompt = f"""
                    {sys_prompt}
                    Razionalizza il tempo, visita quanti più posti possibili con {duration_check} notti a disposizione.
                    Valuta la densità degli impegni giornalieri perché siano fattibili. Presta attenzione ad essere razionale negli spostamenti per massimizzare il tempo a disposizione.
                    Tieni conto delle NOTE UTENTE per personalizzare l'esperienza, ma NON ripeterle esplicitamente.
                    Crea un "Travel Plan" esclusivo per: {destination}.
                    
                    DATI:
                    - Durata: {duration_check} notti ({start_date} - {end_date})
                    - Gruppo: {pax_desc}
                    - Budget: € {budget}
                    - NOTE UTENTE: {travel_desc if travel_desc else "Nessuna nota"}
                    
                    REGOLE TASSATIVE:
                    1. {rules_lang} 2. TRASLITTERA i nomi locali. 3. Simboli Valute: EUR, USD.
                    4. USA intelligentemente il grassetto markdown (**) per evidenziare i giorni (es. **Giorno 1:**), i nomi dei luoghi, degli hotel, delle attrazioni e dei ristoranti, per rendere la lettura del documento molto più facile e scansionabile.
                    5. VIETATO USARE LISTE ANNIDATE. 6. PREZZI IN EURO CON SEPARATORE MIGLIAIA.
                    7. USA DURATA {duration_check}, non ricalcolare. 8. NON SCRIVERE I TUOI PENSIERI INTERNI.
                    
                    STRUTTURA TITOLI (Usa ESATTAMENTE questi):
                    {structure}
                    """
                    
                    response = model.generate_content(prompt)
                    pdf_bytes = create_complex_pdf(response.text, destination, {"dates": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m/%Y')}", "pax": pax_desc, "budget": f"EUR {budget}", "month_name": mese_partenza}, lang_code)
                    st.session_state['wizard_pdf'] = pdf_bytes
                    st.rerun()
                except Exception as e: st.error(f"Errore: {e}")

    if 'wizard_pdf' in st.session_state:
        st.success(ui["msg_success"])
        st.download_button(label=ui["btn_download"], data=st.session_state['wizard_pdf'], file_name=f"Itinerary_{destination.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, on_click=reset_app)

st.markdown("---")
st.subheader(ui.get("hub_title_gen", "✈️ I migliori strumenti per il tuo viaggio"))
c1, c2, c3 = st.columns(3)
with c1: partner_button("Kiwi", FLIGHT_LINK, "btn_kiwi.png")
with c2: partner_button("Expedia", HOTEL_LINK, "btn_booking.png")
with c3: partner_button("Transfer", TRANSF_LINK, "btn_wp.png")
st.write("")
c4, c5, c6 = st.columns(3)
with c4: partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png")
with c5: partner_button("Sixt", RENTAL_LINK, "btn_sixt.png")
with c6: partner_button("Radical", LUGGAGE_LINK, "btn_radical.png")
st.write("")
c7, c8, c9 = st.columns(3)
with c7: partner_button("Saily", ESIM_LINK, "btn_saily.png")
with c8: partner_button("Heymondo", INSURANCE_LINK, "btn_heymondo.png")
with c9: partner_button("AirHelp", REIMB_LINK, "btn_airhelp.png")
st.write("")
c10, c11, c12 = st.columns(3)
with c10: partner_button("Omio", TRAIN_LINK, "btn_omio.png")
with c11: partner_button("GetYourGuide", GYG_LINK, "btn_gyg.png")
with c12: partner_button("Kiwitaxi", TAXI_LINK, "btn_taxi.png")

st.markdown("---")
st.markdown(f"""
<div style="text-align: justify; color: #555;">
    <h3>{ui["footer_title"]}</h3>
    <p>{ui["footer_text"]}</p>
</div>
""", unsafe_allow_html=True)
