import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64
import datetime
import unicodedata
import os
import re
import json

# --- NUOVE IMPORTAZIONI PER GOOGLE SHEETS ---
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="Itinerary Wizard", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="Itinerary Wizard", page_icon="🧙‍♂️", layout="centered")

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
# Nota: Immagini promo gestite dinamicamente nel PDF

FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://tiqets.tpx.lt/XV1Urbnn"
INSURANCE_LINK = "https://heymondo.it?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
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
        "ad_flight": "In {month} i prezzi aumentano? Prenota ora su Kiwi.com",
        "ad_esim": "eSim Saily: Internet immediato all'arrivo senza acquisto di SIM locali",
        "ad_insur": "MAI senza Assicurazione Sanitaria: Approfitta QUI dello sconto 10% con Heymondo",
        "ad_hotel": "Stanze in Hotel quasi esaurite in {month}? Prenota ora su Expedia",
        "ad_transfer": "Transfer privati ad un prezzo WOW! da e per l'aeroporto",
        "ad_tiqets": "Non rischiare il tutto esaurito a {dest}. Assicurati il posto e le migliori offerte su Tiqets",
        "ad_car": "Viaggia in libertà e noleggia un auto: Tariffe esclusive con Auto Europe",
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
        "ad_car": "Travel freely and rent a car: Exclusive rates with Auto Europe",
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
# 🧙‍♂️ PDF ENGINE (MULTILINGUA)
# ==========================================
def create_complex_pdf(text, destination, meta_data, lang_code):
    
    ui = LANGUAGES[lang_code] # Carico dizionario lingua corretta

    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        text_input = text_input.replace("**", "")
        replacements = {
            "€": "EUR", "â‚¬": "EUR", "$": "USD", "£": "GBP",
            "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."
        }
        for char, replacement in replacements.items():
            text_input = text_input.replace(char, replacement)
        text_input = unicodedata.normalize('NFC', text_input)
        output = []
        for char in text_input:
            try:
                char.encode('latin-1')
                output.append(char)
            except UnicodeEncodeError:
                decomposed = unicodedata.normalize('NFD', char)
                stripped = "".join(c for c in decomposed if unicodedata.category(c) != 'Mn')
                try:
                    stripped.encode('latin-1')
                    output.append(stripped)
                except:
                    pass    
        return "".join(output)

    dest_clean = clean_text_for_pdf(destination)
    month_clean = clean_text_for_pdf(meta_data.get('month_name', ''))

    class WizardPDF(FPDF):
        def header(self):
            if self.page_no() <= 2: return 
            self.set_fill_color(44, 62, 80)
            self.rect(0, 0, 210, 15, 'F')
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(255, 255, 255)
            self.set_y(6)
            self.cell(0, 0, f'TRAVEL PLAN: {dest_clean.upper()}', border=0, ln=0, align='R')
            self.ln(15)
            
        def footer(self):
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - {ui["pdf_page"]} {self.page_no()}', 0, 0, 'C')

        def make_cover(self, dest, meta):
            self.add_page()
            self.set_fill_color(245, 245, 245)
            self.rect(0, 0, 210, 297, 'F')
            if os.path.exists("logo.png"):
                self.image("logo.png", x=80, y=30, w=50)
            self.ln(80)
            self.set_font('Helvetica', 'B', 36)
            self.set_text_color(44, 62, 80)
            self.multi_cell(0, 15, dest.upper(), align='C')
            self.ln(10)
            self.set_font('Helvetica', 'I', 14)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, ui["pdf_title"], 0, 1, 'C')
            self.ln(20)
            self.set_fill_color(255, 255, 255)
            self.rect(55, 140, 100, 50, 'F')
            self.set_y(145)
            self.set_font('Helvetica', 'B', 10)
            clean_budget = clean_text_for_pdf(meta['budget'])
            self.cell(0, 6, f"{ui['pdf_date']}: {meta['dates']}", 0, 1, 'C')
            self.cell(0, 6, f"{ui['pdf_travellers']}: {meta['pax']}", 0, 1, 'C')
            self.cell(0, 6, f"{ui['pdf_budget_target']}: {clean_budget}", 0, 1, 'C')
            self.set_y(260)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 10, ui["pdf_generated"], 0, 0, 'C', link="https://www.30secondstoguide.it")

    def add_promo_page(pdf_obj):
        # Selezione dinamica immagine
        promo_img = "promo_to_guide_en.jpg" if lang_code == "EN" else "promo_to_guide.jpg"
        if not os.path.exists(promo_img): return
        
        pdf_obj.add_page()
        pdf_obj.image(promo_img, x=15, y=30, w=180)
        
        box_y = 160 
        pdf_obj.set_fill_color(230, 126, 34) 
        pdf_obj.set_draw_color(211, 84, 0)
        pdf_obj.rect(15, box_y, 180, 30, 'DF')
        
        pdf_obj.set_y(box_y + 8)
        pdf_obj.set_font("Helvetica", 'B', 14)
        pdf_obj.set_text_color(255, 255, 255)
        
        cta_text = ui["pdf_promo"]
        pdf_obj.set_x(15)
        pdf_obj.multi_cell(180, 8, cta_text, align='C', link=GUIDE_APP_URL)

    pdf = WizardPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.make_cover(dest_clean, meta_data)
    add_promo_page(pdf)
    pdf.add_page()
    
    def make_box(pdf_obj, text, link, style="blue"):
        text = clean_text_for_pdf(text)
        palettes = {
            "blue":  {"bg": (240, 248, 255), "accent": (0, 102, 204)},
            "green":  {"bg": (240, 255, 240), "accent": (0, 153, 76)},
            "yellow": {"bg": (255, 253, 240), "accent": (204, 153, 0)},
            "purple": {"bg": (248, 240, 255), "accent": (102, 0, 153)},
            "orange": {"bg": (255, 245, 235), "accent": (230, 90, 0)}
        }
        chosen = palettes.get(style, palettes["blue"])
        bg_r, bg_g, bg_b = chosen["bg"]
        ac_r, ac_g, ac_b = chosen["accent"]
        if pdf_obj.get_y() > 250: pdf_obj.add_page()
        pdf_obj.ln(4)
        current_y = pdf_obj.get_y()
        pdf_obj.set_fill_color(bg_r, bg_g, bg_b)
        pdf_obj.set_draw_color(bg_r, bg_g, bg_b)
        pdf_obj.rect(15, current_y, 180, 14, 'DF')
        pdf_obj.set_fill_color(ac_r, ac_g, ac_b)
        pdf_obj.rect(15, current_y, 2, 14, 'F')
        pdf_obj.set_xy(20, current_y + 4)
        pdf_obj.set_font("Helvetica", 'B', 9)
        pdf_obj.set_text_color(44, 62, 80)
        pdf_obj.cell(170, 6, f"{text} >", link=link)
        pdf_obj.ln(12)

    lines = text.split('\n')
    inserted_ch1 = inserted_ch2 = inserted_ch3 = inserted_ch4 = False

    # DEFINISCO I TRIGGER DINAMICI (Es. "## CAPITOLO 2" vs "## CHAPTER 2")
    TRIGGER_CH = f"## {ui['key_chapter']}"
    TRIGGER_VERDICT = ui['key_verdict']
    TRIGGER_DAY = f"{ui['key_day']}"

    for line in lines:
        clean_line = clean_text_for_pdf(line)
        line_upper = clean_line.upper()
        
        # LOGICA INIEZIONE ANNUNCI (Basata sulla stringa localizzata)
        if f"{TRIGGER_CH} 2" in line_upper and not inserted_ch1:
            make_box(pdf, ui["ad_flight"].format(month=month_clean), FLIGHT_LINK, "green")
            make_box(pdf, ui["ad_esim"], ESIM_LINK, "yellow")
            make_box(pdf, ui["ad_insur"], INSURANCE_LINK, "green")
            inserted_ch1 = True
        elif f"{TRIGGER_CH} 3" in line_upper and not inserted_ch2:
            make_box(pdf, ui["ad_hotel"].format(month=month_clean), HOTEL_LINK, "blue")
            make_box(pdf, ui["ad_transfer"], TRANSF_LINK, "purple")
            inserted_ch2 = True
        elif f"{TRIGGER_CH} 4" in line_upper and not inserted_ch3:
            make_box(pdf, ui["ad_tiqets"].format(dest=dest_clean), TIQETS_LINK, "orange")
            make_box(pdf, ui["ad_car"], RENTAL_LINK, "purple")
            make_box(pdf, ui["ad_train"], TRAIN_LINK, "purple")
            inserted_ch3 = True
        elif f"{TRIGGER_CH} 5" in line_upper and not inserted_ch4:
            make_box(pdf, ui["ad_rest"], GYG_LINK, "green")
            inserted_ch4 = True

        if line.strip().startswith('# '):
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(175, 10, clean_line.replace('#', '').strip())
            pdf.ln(5)
        # Regex dinamica per Capitoli (supporta CAPITOLO e CHAPTER)
        elif re.match(r'^[\*#\s]*' + re.escape(ui['key_chapter']) + r'\s+\d+\s*:', line_upper):
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(230, 126, 34)
            title_text = re.sub(r'^[\*#\s]*', '', clean_line).strip()
            pdf.multi_cell(175, 10, title_text)
            pdf.ln(3)
        elif TRIGGER_VERDICT in line_upper:
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_fill_color(220, 220, 220)
            clean_verdict = clean_line.replace('*', '').strip()
            pdf.multi_cell(180, 8, clean_verdict, border=1, align='C', fill=True)
            pdf.ln(5)
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(20, 20, 20)
            pdf.set_x(20) 
            pdf.cell(5, 6, chr(149), 0, 0)
            content = re.sub(r'^[\*-]\s*', '', clean_line).strip()
            if content: pdf.multi_cell(160, 6, content)
        elif re.match(r'^\d+\.', line.strip()):
            pdf.set_font("Helvetica", 'B', 11)
            pdf.set_text_color(44, 62, 80)
            pdf.ln(2)
            pdf.multi_cell(175, 6, clean_line)
        # Regex dinamica per Giorni (GIORNO o DAY)
        elif re.match(re.escape(TRIGGER_DAY) + r'\s*\d+:', line_upper):
            if pdf.get_x() > 15: pdf.ln(6) 
            pdf.set_font("Helvetica", 'B', 11)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(175, 6, clean_line)
            pdf.ln(1)
        else:
            if line.strip():
                if pdf.get_x() > 15 and pdf.get_y() > 20: pdf.ln(1) 
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(175, 6, clean_line)
                pdf.ln(1)

    pdf.add_page()
    def make_sponsor_box(title, subtitle, link, highlight=False):
        title = clean_text_for_pdf(title)
        subtitle = clean_text_for_pdf(subtitle)
        if highlight:
            pdf.set_fill_color(230, 240, 255)
            pdf.set_draw_color(0, 102, 204)
        else:
            pdf.set_fill_color(250, 250, 250)
            pdf.set_draw_color(220, 220, 220)
        if pdf.get_y() > 250: pdf.add_page()
        start_y = pdf.get_y()
        pdf.rect(15, start_y, 180, 14, 'DF')
        pdf.set_y(start_y + 2)
        pdf.set_x(20)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 5, title, 0, 1)
        pdf.set_x(20)
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 6, subtitle, 0, 1, link=link)
        pdf.ln(4)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, ui["pdf_seen"], 0, 1, 'L')
    pdf.ln(2)
    make_sponsor_box("Expedia", "Hotel", HOTEL_LINK)
    make_sponsor_box("Tiqets", "Tickets", TIQETS_LINK)
    make_sponsor_box("Welcome Pickups", "Transfer", TRANSF_LINK)
    make_sponsor_box("Auto Europe", "Auto", RENTAL_LINK)
    make_sponsor_box("Omio", "Bus/Train", TRAIN_LINK)
    make_sponsor_box("Kiwi.com", "Flights", FLIGHT_LINK)
    make_sponsor_box("Heymondo", "Insurance", INSURANCE_LINK)
    make_sponsor_box("Saily", "eSim", ESIM_LINK)
    make_sponsor_box("GetYourGuide", "Escursioni", GYG_LINK)
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, ui["pdf_others"], 0, 1, 'L')
    pdf.ln(2)
    make_sponsor_box("Radical Storage", "Luggage Storage", LUGGAGE_LINK, highlight=True)
    make_sponsor_box("AirHelp", "Flight Refund", REIMB_LINK, highlight=True)
    make_sponsor_box("Kiwitaxi", "Taxi", TAXI_LINK, highlight=True)
    return bytes(pdf.output(dest='S'))

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
    partner_button("AutoEurope", RENTAL_LINK, "btn_autoe.png")
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
    with c_bud: budget = st.number_input(ui["label_budget"], min_value=500, value=3000, step=100)
    
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
                    
                    # LOGICA PROMPT LINGUA
                    if lang_code == "IT":
                        sys_prompt = "Agisci come un Travel Planner Senior. Non pianifichi solo un viaggio, pianifichi un viaggio su misura che massimizza il valore del budget."
                        rules_lang = "Usa SOLO l'alfabeto Latino/Italiano."
                        # Struttura fissa IT
                        structure = f"""
                        # {destination.upper()}: [Sottotitolo]
                        **IL VERDETTO SUL BUDGET: € {budget}** (Stato: Lusso/Più che adeguato/Sufficiente/Stretto/Impossibile)
                        ## CAPITOLO 1: LA PREPARAZIONE (Voli, eSim, Assicurazione)
                        [Info trasporti, eSim Saily (NO per Italia/UE), assicurazione Heymondo sconto 10%]
                        ## CAPITOLO 2: DOVE DORMIRE (Strategie alloggio)
                        ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (Dettagliato)
                        [Itinerario ottimizzato, razionalizza gli spostamenti in base alla distanza, a seconda del mezzo di trasporto massimizza le tappe con i tempo a disposizione. Prediligi attrazioni su Tiqets e Getyourguide. Scoperta del territorio]
                        ## CAPITOLO 4: COSA MANGIARE
                        [Piatti tipici, ristoranti (verifica su Tripadvisor i migliori per la fascia di prezzo compatibile con il budget e dai riferimenti puntuali), suggerisci i posti migliori per lo street food]
                        ## CAPITOLO 5: CALENDARIO CULTURALE
                        [Festival e ricorrenze]
                        ## CAPITOLO 6: CONTO ECONOMICO FINALE
                        ## CAPITOLO 7: INFORMAZIONI PRATICHE
                        ## CAPITOLO 8: CONCLUSIONE
                        """
                    else:
                        sys_prompt = "Act as a Senior Travel Planner. You don't just plan a trip, you plan a tailor-made trip that maximizes budget value."
                        rules_lang = "Use ONLY Latin/English alphabet."
                        # Struttura fissa EN (Cruciale: CHAPTER instead of CAPITOLO)
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
                    4. VIETATO L'USO DI ASTERISCHI O GRASSETTO MARKDOWN.
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
st.subheader(ui.get("hub_title_gen", "✈️ I migliori strumenti per il tuo viaggio")) # Fallback se manca chiave
c1, c2, c3 = st.columns(3)
with c1: partner_button("Kiwi", FLIGHT_LINK, "btn_kiwi.png")
with c2: partner_button("Expedia", HOTEL_LINK, "btn_booking.png")
with c3: partner_button("Transfer", TRANSF_LINK, "btn_wp.png")
st.write("")
c4, c5, c6 = st.columns(3)
with c4: partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png")
with c5: partner_button("AutoEurope", RENTAL_LINK, "btn_autoe.png")
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
