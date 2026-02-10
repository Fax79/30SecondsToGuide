import streamlit as st
import streamlit.components.v1 as components # <--- UNICA AGGIUNTA NEGLI IMPORT
import google.generativeai as genai
from fpdf import FPDF
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

# --- MODIFICA CONCORDATA: INJECTION JAVASCRIPT PER UMAMI ---
def set_social_headers():
    SOCIAL_IMAGE_URL = "https://raw.githubusercontent.com/Fax79/30secondstoguide/main/logo.png"
    
    # 1. Meta Tags (Restano in Markdown perché sono statici)
    meta_tags = f"""
    <meta property="og:title" content="30SecondsToGuide - La tua guida di viaggio IA" />
    <meta property="og:description" content="Da zero a local in 30 secondi. Crea itinerari personalizzati e scarica guide PDF gratuite per qualsiasi città." />
    <meta property="og:image" content="{SOCIAL_IMAGE_URL}" />
    <meta property="og:url" content="https://www.30secondstoguide.it" />
    <meta property="og:type" content="website" />
    """
    st.markdown(meta_tags, unsafe_allow_html=True)

    # 2. Injection "Chirurgica" di Umami
    # Questo script JS esce dall'iframe e scrive nell'Header della pagina principale (window.parent).
    umami_injection = """
        <script>
            var parentHead = window.parent.document.getElementsByTagName("head")[0];
            var script = window.parent.document.createElement("script");
            script.defer = true;
            script.src = "https://cloud.umami.is/script.js";
            script.setAttribute("data-website-id", "897aa2b4-2423-49b6-978d-c1f36c84c4b3");
            
            // Controllo anti-duplicati: lo aggiungo solo se non c'è già
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
    sheet = get_db_connection()
    if sheet:
        try:
            return sheet.get_all_records()
        except:
            return []
    return []

def add_log(city_name, lang_code):
    sheet = get_db_connection()
    if sheet:
        try:
            timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
            row = [
                timestamp,
                city_name,
                "GUIDE_ONLY", 
                "-",
                "-",
                "-",
                "-",
                lang_code
            ]
            sheet.append_row(row)
        except Exception as e:
            print(f"Errore log: {e}")

# --- CONFIGURAZIONE API ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ API Key missing! Check 'Secrets'.")
    st.stop()

# ==========================================
# 🌐 CONFIGURAZIONE PROMO & LINK
# ==========================================
WIZARD_APP_URL = "https://www.30secondstoguide.it" 

# LINK TRACCIATI (Usati nel Travel Hub e nel PDF)
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://tiqets.tpx.lt/XV1Urbnn"
INSURANCE_LINK = "https://heymondo.it?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"

# LINK GENERICI
TRAIN_LINK = "https://www.omio.com"
GYG_LINK = "https://gyg.me/YAGbtbpK"
HOTEL_LINK = "https://www.expedia.com" 
PROMO_LINK = INSURANCE_LINK 

# --- DIZIONARI LINGUA ---
LANGUAGES = {
    "IT": {
        "h1": "Generatore Guide Turistiche",
        "subtitle": "Da zero a local in mezzo minuto.",
        "wiz_title": "🧙‍♂️ Vuoi chiedere al nostro Wizard di organizzare il tuo viaggio personalizzato?",
        "wiz_desc": "Verifica il tuo budget, crea il tuo itinerario su misura, interroga qui sotto il nostro mago. 🔻🔻🔻",
        "wiz_btn": "✨ APRI ITINERARY WIZARD",
        "input_label": "Se vuoi generare la guida specifica di una città inserisci QUI la destinazione:",
        "input_placeholder": "Es. Parigi, Tokyo, New York...",
        "btn_generate": "Genera Guida PDF",
        "btn_download": "🎨 SCARICA GUIDA PDF PRO",
        "msg_warning": "Inserisci una città.",
        "msg_success": "✅ Guida per {city} pronta!",
        "spinner": "Stiamo scrivendo la tua guida... (non chiudere la pagina)",
        "hub_title": "✈️ Organizza il viaggio a {city}",
        "hub_title_gen": "✈️ I migliori strumenti per il tuo viaggio",
        "footer_seo_title": "Come funziona 30SecondsToGuide?",
        "footer_seo_text": "è il primo generatore di guide turistiche basato sull'Intelligenza Artificiale. A differenza dei tradizionali blog di viaggio, il nostro algoritmo crea <strong>itinerari personalizzati in PDF</strong> per qualsiasi città del mondo in meno di 30 secondi. Il servizio è <strong>gratuito al 100%</strong>.",
        # Sidebar Labels
        "sb_pocket": "📚 LE NOSTRE GUIDE POCKET",
        "sb_privacy": "Privacy Policy"
    },
    "EN": {
        "h1": "AI Travel Guide Generator",
        "subtitle": "From zero to local in 30 seconds.",
        "wiz_title": "🧙‍♂️ Do you want our Wizard to organize your custom trip?",
        "wiz_desc": "Check your budget, create a tailor-made itinerary, ask our wizard below.",
        "wiz_btn": "✨ OPEN ITINERARY WIZARD",
        "input_label": "Enter the destination city HERE to generate your exclusive guide:",
        "input_placeholder": "E.g. Paris, Tokyo, New York...",
        "btn_generate": "Generate PDF Guide",
        "btn_download": "🎨 DOWNLOAD PRO PDF GUIDE",
        "msg_warning": "Please enter a city.",
        "msg_success": "✅ Guide for {city} is ready!",
        "spinner": "Writing your guide... (please do not close this page)",
        "hub_title": "✈️ Plan your trip to {city}",
        "hub_title_gen": "✈️ Best tools for your trip",
        "footer_seo_title": "How does 30SecondsToGuide work?",
        "footer_seo_text": "is the first AI-based travel guide generator. Unlike traditional travel blogs, our algorithm creates <strong>custom PDF itineraries</strong> for any city in the world in less than 30 seconds. The service is <strong>100% free</strong>.",
        # Sidebar Labels
        "sb_pocket": "📚 OUR POCKET GUIDES",
        "sb_privacy": "Privacy Policy"
    }
}

# --- MODELLI PROMPT (IT / EN) ---
TESTO_MODELLO_IT = """
# [NOME CITTÀ]: Guida Esclusiva

## 1. L'Anima della Città
[Intro evocativa di 150 parole, comprensione profonda dell'anima dei luoghi].

## 2. Quartieri e Atmosfere
[Descrizione zone, individua il contrasto principale antico vs moderno, popolare vs esclusivo, riva destra vs riva sinistra, ecc].

### Confronto Zone
* **[zona 1 di cui sopra]:** [Descrizione atmosfera]
* **[zona 2 di cui sopra]:** [Descrizione atmosfera]
* **Chi ci va:** [Target turisti]

## 3. Dove dormire
[Migliori quartieri dove alloggiare per tipologia di turista/vacanza: in famiglia, in coppia, con un gruppo di amici, viaggiatori senior].

## 4. Gastronomia
[Cosa mangiare e dove, la tradizione gastronomica].

### Piatti Imperdibili
* **[Piatto 1]:** [Descrizione e ingredienti]
* **[Piatto 2]:** [Descrizione e ingredienti]
* **[il cibo tradizionale]:** [i migliori ristoranti, i più caratteristici, consigli per risparmiare]
* **[bevande tradizionali]:** [i migliori locali, i più caratteristici, consigli per risparmiare]

## 5. Attrazioni
* **[Monumento 1]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 2]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 3]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 4]:** [Descrizione,  se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 5]:** [Descrizione,  se presenti giorni e orari di apertura, prezzi biglietti]

## 6. I mercati
* **[Mercato 1]:** [Descrizione]
* **[Mercato 2]:** [Descrizione]

## 7. Calendario Culturale
[I principali festival, fiere, ricorrenze e feste della città].

## 8. Info Pratiche
* **Come arrivare:** [Info su compagnie aeree che servono l'aeroporto principale (tradizionali e low cost), voli dall'Italia (se la destinazione è all'estero), mezzi alternativi: treni/autobus)]
* **Trasporti:** [Info]
* **Sicurezza:** [Info]
* **Clima:** [Info sui migliori periodi per visitare la città]
* **Visti e requisiti:** [Info]
* **Fuso orario:** [Info]
* **Consigli utili:** [Info su valuta locale e prese elettriche, non usare mai simboli delle valute ma i loro codici, es. EUR, USD, GBP, ecc]

## 9. Itinerario 3 Giorni
* **Giorno 1:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 2:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 3:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]

## 10. Itinerario 5 Giorni
* **Giorni 1-3:** Come sopra.
* **Giorno 4:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 5:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]

## 11. Se hai più tempo
* **Fuori dai sentieri battuti:** [Un quartiere meno turistico].
* **Gite fuori porta:** [Una o più gite di mezza giornata o di un giorno nei dintorni].

## 12. Conclusione
[Riflessione finale filosofica sul viaggio in questa città, descrivi l'essenza del viaggio].
"""

TESTO_MODELLO_EN = """
# [CITY NAME]: Exclusive Guide

## 1. The Soul of the City
[Evocative intro of 150 words, deep understanding of the soul of the places].

## 2. Neighborhoods and Atmospheres
[Zone description, identify the main contrast ancient vs modern, popular vs exclusive, right bank vs left bank, etc].

### Zone Comparison
* **[zone 1 mentioned above]:** [Atmosphere description]
* **[zone 2 mentioned above]:** [Atmosphere description]
* **Who goes there:** [Tourist target]

## 3. Where to sleep
[Best neighborhoods to stay for type of tourist/vacation: family, couple, group of friends, senior travelers].

## 4. Gastronomy
[What to eat and where, the gastronomic tradition].

### Unmissable Dishes
* **[Dish 1]:** [Description and ingredients]
* **[Dish 2]:** [Description and ingredients]
* **[traditional food]:** [best restaurants, most characteristic ones, tips to save money]
* **[traditional drinks]:** [best bars, most characteristic ones, tips to save money]

## 5. Attractions
* **[Monument 1]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 2]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 3]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 4]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 5]:** [Description, if present opening days and hours, ticket prices]

## 6. Markets
* **[Market 1]:** [Description]
* **[Market 2]:** [Description]

## 7. Cultural Calendar
[Main festivals, fairs, recurring events and city holidays].

## 8. Practical Info
* **Getting there:** [Info on airlines serving the main airport (legacy and low cost), flights from major hubs, alternative means: trains/buses)]
* **Transport:** [Info]
* **Safety:** [Info]
* **Climate:** [Info on best periods to visit]
* **Visas and requirements:** [Info]
* **Time zone:** [Info]
* **Useful tips:** [Info on local currency and power plugs, never use currency symbols but their codes, e.g. EUR, USD, GBP, etc]

## 9. 3-Day Itinerary
* **Day 1:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 2:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 3:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]

## 10. 5-Day Itinerary
* **Days 1-3:** As above.
* **Day 4:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 5:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]

## 11. If you have more time
* **Off the beaten path:** [A less touristy neighborhood].
* **Day trips:** [One or more half-day or full-day trips in the surroundings].

## 12. Conclusion
[Final philosophical reflection on the trip to this city, describe the essence of the journey].
"""

# --- HELPER FUNZIONI ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def partner_button(label, link, image_file):
    # Questa funzione è usata solo nel Travel Hub (in basso), non più nella sidebar
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

# --- FUNZIONE PDF (Multilingua) ---
def create_pdf(text, city, lang_code="IT"):
    
    # Dizionario stringhe PDF
    PDF_STRINGS = {
        "IT": {
            "header": "GUIDA",
            "subtitle": "Guida turistica completa\nItinerari, Storia e Cultura",
            "disclaimer": "Questa guida è offerta gratuitamente. Se ti è utile, nell'ultima pagina trovi una selezione di sconti esclusivi per voli e hotel che ci aiutano a mantenere il servizio attivo. Buon viaggio!",
            "generated_by": "GENERATO CON www.30secondstoguide.it",
            "promo_cta": "Clicca qui se vuoi un itinerario personalizzato in base alla durata e al tuo budget.",
            "inj_esim": f"Non restare senza internet a {city}? eSim Saily (Sconto 5%)",
            "inj_hotel": f"Prezzi Hotel in aumento a {city}? Verifica disponibilità su Expedia",
            "inj_tix": f"Biglietti ufficiali Musei e Attrazioni a {city} su Tiqets",
            "inj_flight": f"Trova subito voli economici per {city} su Kiwi.com",
            "inj_transfer": f"Transfer NCC dall'aeroporto al prezzo di un taxi (Welcome Pickups)",
            "inj_insur": "Assicurazione Viaggio (Sconto 10% con Heymondo)",
            "partner_seen": "Già visti nella guida...",
            "partner_others": "ALTRI SERVIZI INDISPENSABILI",
            "p_hotel": "Hotel e alloggi",
            "p_tix": "Biglietti musei e attrazioni",
            "p_flight": "Voli low cost",
            "p_insur": "Assicurazione viaggio",
            "p_esim": "eSim internazionale",
            "p_transf": "Transfer aeroportuali",
            "p_lugg": "Libera le mani con Radical Storage",
            "p_reimb": "Volo in ritardo? Chiedi risarcimento con AirHelp",
            "p_rent": "Migliori tariffe con Auto Europe",
            "p_train": "Prenota con Omio",
            "p_taxi": "Kiwitaxi per spostamenti urbani",
            "p_rest": "Le tue escursioni con GetYourGuide"
        },
        "EN": {
            "header": "GUIDE",
            "subtitle": "Complete Travel Guide\nItineraries, History and Culture",
            "disclaimer": "This guide is free. If it's useful, on the last page you'll find a selection of exclusive discounts for flights and hotels that help us keep the service running. Safe travels!",
            "generated_by": "GENERATED WITH www.30secondstoguide.it",
            "promo_cta": "Click here if you want a personalized itinerary based on duration and budget.",
            "inj_esim": f"Don't run out of internet in {city}? eSim Saily (5% Discount)",
            "inj_hotel": f"Hotel prices rising in {city}? Check availability on Expedia",
            "inj_tix": f"Official Tickets for Museums and Attractions in {city} on Tiqets",
            "inj_flight": f"Find cheap flights to {city} now on Kiwi.com",
            "inj_transfer": f"Private Airport Transfer at taxi price (Welcome Pickups)",
            "inj_insur": "Travel Insurance (10% Discount with Heymondo)",
            "partner_seen": "Featured in this guide...",
            "partner_others": "ESSENTIAL SERVICES",
            "p_hotel": "Hotels and accommodation",
            "p_tix": "Museums and attractions tickets",
            "p_flight": "Low cost flights",
            "p_insur": "Travel insurance",
            "p_esim": "International eSim",
            "p_transf": "Airport transfers",
            "p_lugg": "Free your hands with Radical Storage",
            "p_reimb": "Delayed flight? Claim compensation with AirHelp",
            "p_rent": "Best rates with Auto Europe",
            "p_train": "Book with Omio",
            "p_taxi": "Kiwitaxi for urban rides",
            "p_rest": "Travel experiences on GetYourGuide"
        }
    }
    
    ps = PDF_STRINGS[lang_code]

    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        replacements = {
            "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...",
            "€": "EUR", "$": "USD", "£": "GBP",
            "ł": "l", "Ł": "L", "đ": "d", "Đ": "D", "ø": "o", "Ø": "O",
            "©": "(c)", "®": "(r)"
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
                base_char = decomposed[0]
                try:
                    base_char.encode('latin-1')
                    output.append(base_char)
                except UnicodeEncodeError:
                    pass
        return "".join(output)

    city_clean = clean_text_for_pdf(city)

    class ModernPDF(FPDF):
        def header(self):
            if self.page_no() <= 2: return 
            self.set_fill_color(44, 62, 80) 
            self.rect(0, 0, 210, 20, 'F')
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(255, 255, 255)
            self.set_y(8)
            self.cell(0, 0, f'{ps["header"]}: {city_clean.upper()}', 0, 0, 'R')
            self.ln(20) 
            
        def footer(self):
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - Page {self.page_no()}', 0, 0, 'C')

        def make_cover(self, city_name_input):
            self.add_page()
            self.set_fill_color(236, 240, 241) 
            self.rect(0, 0, 60, 297, 'F') 
            if os.path.exists("logo.png"):
                self.image("logo.png", x=70, y=20, w=50)
                y_start = 80 
            else:
                y_start = 50
            self.set_y(y_start)
            self.set_x(70)
            self.set_font('Helvetica', 'B', 40)
            self.set_text_color(44, 62, 80)
            self.multi_cell(0, 20, city_name_input.upper())
            self.ln(10)
            self.set_x(70)
            self.set_font('Helvetica', '', 16)
            self.set_text_color(127, 140, 141)
            self.multi_cell(0, 10, ps["subtitle"])
            self.ln(20)
            self.set_fill_color(230, 126, 34) 
            self.rect(70, self.get_y(), 100, 2, 'F')
            self.set_y(225) 
            self.set_x(70)
            self.set_font('Helvetica', 'I', 9) 
            self.set_text_color(100, 100, 100)
            self.multi_cell(110, 5, ps["disclaimer"])
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'BU', 10) 
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, ps["generated_by"], link="https://www.30secondstoguide.it")

    def add_promo_page(pdf_obj):
        # Selezione dinamica immagine (Wizard En vs Wizard It)
        promo_img = "promo_to_wizard_en.jpg" if lang_code == "EN" else "promo_to_wizard.jpg"
        if not os.path.exists(promo_img): return
        
        pdf_obj.add_page()
        pdf_obj.image(promo_img, x=15, y=30, w=180)
        box_y = 160 
        pdf_obj.set_fill_color(155, 89, 182) 
        pdf_obj.set_draw_color(142, 68, 173)
        pdf_obj.rect(15, box_y, 180, 30, 'DF')
        pdf_obj.set_y(box_y + 8)
        pdf_obj.set_font("Helvetica", 'B', 14)
        pdf_obj.set_text_color(255, 255, 255)
        pdf_obj.set_x(15)
        pdf_obj.multi_cell(180, 8, ps["promo_cta"], align='C', link=WIZARD_APP_URL)

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.make_cover(city_clean)
    add_promo_page(pdf)
    pdf.add_page()
    
    lines = text.split('\n')
    
    def make_box(pdf_obj, text, link, style="blue"):
        text = clean_text_for_pdf(text)
        palettes = {
            "blue":   {"bg": (240, 248, 255), "accent": (0, 102, 204)}, 
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
        pdf_obj.rect(10, current_y, 190, 14, 'DF')
        pdf_obj.set_fill_color(ac_r, ac_g, ac_b)
        pdf_obj.rect(10, current_y, 2, 14, 'F')
        pdf_obj.set_xy(15, current_y + 4) 
        pdf_obj.set_font("Helvetica", 'B', 9)
        pdf_obj.set_text_color(44, 62, 80)
        pdf_obj.cell(180, 6, f"{text} >", link=link)
        pdf_obj.ln(12)

    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
        # Iniezioni basate sui numeri di sezione
        if line.startswith('## 2. '):
            make_box(pdf, ps["inj_esim"], ESIM_LINK, style="yellow")
        if line.startswith('## 4. '):
            make_box(pdf, ps["inj_hotel"], HOTEL_LINK, style="blue")
        if line.startswith('## 6. '):
             make_box(pdf, ps["inj_tix"], TIQETS_LINK, style="orange")
        if line.startswith('## 9. '):
             make_box(pdf, ps["inj_flight"], FLIGHT_LINK, style="green")
             make_box(pdf, ps["inj_transfer"], TRANSF_LINK, style="purple")
             make_box(pdf, ps["inj_insur"], INSURANCE_LINK, style="green")

        if line.startswith('# '): 
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 22)
            pdf.set_text_color(44, 62, 80)
            content = clean_line.replace('# ', '').replace('*', '').upper().strip()
            pdf.multi_cell(0, 10, content)
            y = pdf.get_y()
            pdf.set_draw_color(230, 126, 34)
            pdf.set_line_width(1)
            pdf.line(10, y+2, 50, y+2) 
            pdf.ln(8)
        elif line.startswith('## '): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 16)
            pdf.set_text_color(230, 126, 34)
            content = clean_line.replace('## ', '').replace('*', '').strip()
            pdf.cell(0, 10, content, ln=True)
            pdf.ln(2)
        elif line.startswith('### '): 
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.set_text_color(52, 73, 94)
            content = clean_line.replace('### ', '').replace('*', '').strip()
            pdf.cell(0, 10, content, ln=True)
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(0, 0, 0)
            content_raw = line.strip()[2:]
            content = clean_text_for_pdf(content_raw.replace('*', ''))
            pdf.set_x(15) 
            pdf.cell(5, 5, chr(149), 0, 0) 
            pdf.set_x(22) 
            pdf.multi_cell(0, 6, content)
            pdf.ln(1)
        else: 
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                content = clean_line.replace('*', '')
                pdf.multi_cell(0, 6, content)
                pdf.ln(2)

    # PAGINA PARTNER FINALE
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
        start_y = pdf.get_y()
        pdf.rect(10, start_y, 190, 14, 'DF') 
        pdf.set_y(start_y + 2)
        pdf.set_x(15)
        pdf.set_font("Helvetica", 'B', 10) 
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 5, title, 0, 1)
        pdf.set_x(15)
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 6, subtitle, 0, 1, link=link)
        pdf.ln(4) 

    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, ps["partner_seen"], 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Expedia", ps["p_hotel"], HOTEL_LINK) 
    make_sponsor_box("Tiqets", ps["p_tix"], TIQETS_LINK) 
    make_sponsor_box("Kiwi.com", ps["p_flight"], FLIGHT_LINK)
    make_sponsor_box("Heymondo", ps["p_insur"], INSURANCE_LINK)
    make_sponsor_box("Saily", ps["p_esim"], ESIM_LINK)
    make_sponsor_box("Welcome Pickups", ps["p_transf"], TRANSF_LINK)
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 10, ps["partner_others"], 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Radical Storage", ps["p_lugg"], LUGGAGE_LINK, highlight=True)
    make_sponsor_box("AirHelp", ps["p_reimb"], REIMB_LINK, highlight=True)
    make_sponsor_box("Auto Europe", ps["p_rent"], RENTAL_LINK, highlight=True)
    make_sponsor_box("Omio", ps["p_train"], TRAIN_LINK, highlight=True)
    make_sponsor_box("Kiwitaxi", ps["p_taxi"], TAXI_LINK, highlight=True)
    make_sponsor_box("GetYourGuide", ps["p_rest"], GYG_LINK, highlight=True)

    return bytes(pdf.output(dest='S'))

# --- SELETTORE LINGUA (MAIN AREA) ---
# Niente bandiere, solo testo per evitare problemi su PC
col_lang_1, col_lang_2 = st.columns([3, 1]) 
with col_lang_2:
    lang_opt = st.radio(
        "Language:",
        ["Italiano", "English"],
        horizontal=True,
        label_visibility="collapsed",
        key="lang_select_main"
    )

# Aggiornamento Variabili Lingua
lang_code = "IT" if lang_opt == "Italiano" else "EN"
st.session_state["lang_code"] = lang_code 
ui = LANGUAGES[lang_code]

# --- SIDEBAR (NUOVA VERSIONE: GUIDE POCKET) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("⏱️")
    
    st.markdown("---")
    
    # Titolo sezione
    st.subheader(ui["sb_pocket"])
    
    # LISTA GUIDE - Stile Bottone Pieno
    st.link_button("Roma", "https://guide.30secondstoguide.it/roma", use_container_width=True)
    st.link_button("New York", "https://guide.30secondstoguide.it/new-york", use_container_width=True)
    st.link_button("Tokyo", "https://guide.30secondstoguide.it/tokyo", use_container_width=True)
    
    st.divider() # Linea di separazione
    
    # Sezione Blog
    st.markdown("### 📝 Travel Blog")
    st.caption("Ispirazione, guide e sfide AI.")
    
    st.link_button(
        label="Vai al Blog Ufficiale 🚀", 
        url="https://blog.30secondstoguide.it",
        type="primary", 
        use_container_width=True
    )
    
    st.divider()
    
    # --- ADMIN ---
    with st.sidebar.expander("🔐 Admin Stats"):
        secret_pwd = st.text_input("Password", type="password")
        if secret_pwd == "fabio123": 
            st.write("### 📊 Last Searches:")
            logs = load_logs()
            if logs:
                for log in list(reversed(logs))[:10]:
                    if isinstance(log, dict):
                        dest = log.get('Destination', 'N/A')
                        ts = log.get('Timestamp', '')
                        note = log.get('Budget', '') 
                        st.caption(f"📍 {dest} | {ts} [{note}]")
                    else:
                         st.caption(log)
            else:
                st.caption("No logs yet.")

    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")
    st.page_link("pages/privacy.py", label=ui["sb_privacy"], icon="🔒")


# --- CORPO CENTRALE ---
if os.path.exists("logo.png"):
    col_sp1, col_img, col_sp2 = st.columns([3, 2, 3])
    with col_img:
        st.image("logo.png", use_container_width=True)

st.markdown(f"""
    <h1 style='text-align: center; color: #2C3E50; margin-bottom: 0; margin-top: -10px;'>
        {ui["h1"]}
    </h1>
    <p style='text-align: center; color: #E67E22; font-size: 1.2em; font-style: italic; margin-top: 5px;'>
        {ui["subtitle"]}
    </p>
    """, unsafe_allow_html=True)

# CTA WIZARD
st.write("") 
st.markdown(f"""
<div style="background-color: #f0f2f6; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: center; border: 1px solid #dcdcdc;">
    <h3 style="margin: 0; color: #4A00E0; font-size: 1.2em;">{ui["wiz_title"]}</h3>
    <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #333;">
        {ui["wiz_desc"]}
    </p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.page_link("pages/itinerari.py", label=ui["wiz_btn"], use_container_width=True)

st.write("") 

# PROMO AUTOMATICA
PROMO_IMG = "promo_banner.png"
if os.path.exists(PROMO_IMG):
    try:
        promo_b64 = get_base64_of_bin_file(PROMO_IMG)
        promo_html = f"""
        <div style="margin-bottom: 20px; text-align: center;">
            <a href="{PROMO_LINK}" target="_blank">
                <img src="data:image/png;base64,{promo_b64}" 
                     style="width: 100%; max-width: 700px; border-radius: 10px; 
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                            transition: transform 0.2s; cursor: pointer;"
                     onmouseover="this.style.transform='scale(1.02)'"
                     onmouseout="this.style.transform='scale(1.0)'"
                >
            </a>
        </div>
        """
        st.markdown(promo_html, unsafe_allow_html=True)
    except:
        pass

def reset_app():
    if 'generated_pdf' in st.session_state:
        del st.session_state['generated_pdf']
    if 'last_city' in st.session_state:
        del st.session_state['last_city']
    st.session_state.city_input = ""

city_name = st.text_input(ui["input_label"], placeholder=ui["input_placeholder"], key="city_input")

# --- GENERAZIONE ---
with st.container():
    is_generated = 'generated_pdf' in st.session_state
    
    if st.button(ui["btn_generate"], type="primary", use_container_width=True, disabled=is_generated):
        if not city_name:
            st.warning(ui["msg_warning"])
        else:
            add_log(city_name, lang_code)
            
            with st.spinner(ui["spinner"]):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    # SELEZIONE PROMPT IN BASE ALLA LINGUA
                    if lang_code == "IT":
                        sys_instruct = "Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA per:"
                        base_prompt = TESTO_MODELLO_IT
                        rules = """
                        1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                        2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                        3. Usa ESATTAMENTE la struttura seguente.
                        4. Scrivi paragrafi ricchi e lunghi.
                        5. NON USARE MAI CARATTERI SPECIALI, simboli delle valute (come Euro o Dollaro), semplifica la grafia delle parole straniere utilizzando l'alfabeto standard, ammesse SOLO lettere accentate comunemente usate in italiano.
                        6. Se viene inserita una nazione, una regione, un'area geografica produci la guida per la città principale, aggiungi una premessa prima del capitolo 1 in cui elenchi eventuali altre città esortando a fare guide separate, suggerisci anche di utilizzare il bottone dell'"ITINERARY WIZARD" che trovano nel sito.
                        7. Se viene inserita un parola o una frase che non sono luoghi geografici rispondi in modo scherzoso ma sintetico, non usare la struttura della guida.
                        """
                    else:
                        sys_instruct = "You are an expert travel writer (Lonely Planet/National Geographic style). Write a DETAILED guide for:"
                        base_prompt = TESTO_MODELLO_EN
                        rules = """
                        1. NEVER USE MARKDOWN TABLES (no lines with | |).
                        2. If you need to make a comparison, use descriptive bullet points.
                        3. Use EXACTLY the following structure.
                        4. Write rich and long paragraphs.
                        5. NEVER USE SPECIAL CHARACTERS or currency symbols (like Euro or Dollar), simplify foreign spelling using standard alphabet.
                        6. If a nation, region, or geographic area is entered, produce the guide for the main city, add a premise before chapter 1 listing other cities urging to make separate guides, also suggest using the "ITINERARY WIZARD" button found on the site.
                        7. If a word or phrase is entered that is not a geographical place, answer jokingly but synthetically, do not use the guide structure.
                        """
                    
                    full_prompt = f"""
                    {sys_instruct} {city_name}.
                    
                    RULES:
                    {rules}
                    
                    MODEL:
                    {base_prompt}
                    """
                    
                    response = model.generate_content(full_prompt)
                    markdown_content = response.text
                    
                    st.session_state['generated_pdf'] = create_pdf(markdown_content, city_name, lang_code)
                    st.session_state['last_city'] = city_name
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")

if 'generated_pdf' in st.session_state:
    st.success(ui["msg_success"].format(city=st.session_state['last_city']))
    st.download_button(
        label=ui["btn_download"],
        data=st.session_state['generated_pdf'],
        file_name=f"Guide_{st.session_state['last_city']}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
        on_click=reset_app 
    )

# --- TRAVEL HUB (Rimasto invariato, in fondo pagina) ---
st.markdown("---")
if city_name:
    st.subheader(ui["hub_title"].format(city=city_name))
else:
    st.subheader(ui["hub_title_gen"])

c1, c2, c3 = st.columns(3)
with c1:
    st.caption("✈️ **Kiwi**")
    partner_button("Kiwi", FLIGHT_LINK, "btn_kiwi.png")
with c2:
    st.caption("🏨 **Expedia**")
    partner_button("Expedia", HOTEL_LINK, "btn_booking.png") 
with c3:
    st.caption("🚘 **Welcome**")
    partner_button("Welcome", TRANSF_LINK, "btn_wp.png")

st.write("") 

c4, c5, c6 = st.columns(3)
with c4:
    st.caption("🎟️ **Tiqets**")
    partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png") 
with c5:
    st.caption("🚗 **Rental**")
    partner_button("AutoEurope", RENTAL_LINK, "btn_autoe.png")
with c6:
    st.caption("🎒 **Radical**")
    partner_button("Radical", LUGGAGE_LINK, "btn_radical.png")

st.write("") 

c7, c8, c9 = st.columns(3)
with c7:
    st.caption("📲 **Saily**")
    partner_button("Saily", ESIM_LINK, "btn_saily.png")
with c8:
    st.caption("🛡️ **Heymondo**")
    partner_button("Heymondo", INSURANCE_LINK, "btn_heymondo.png")
with c9:
    st.caption("💸 **AirHelp**")
    partner_button("AirHelp", REIMB_LINK, "btn_airhelp.png")

st.write("") 

c10, c11, c12 = st.columns(3)
with c10:
    st.caption("🚆 **Omio**")
    partner_button("Omio", TRAIN_LINK, "btn_omio.png")
with c11:
    st.caption("🍴 **GYG**")
    partner_button("GetYourGuide", GYG_LINK, "btn_gyg.png")
with c12:
    st.caption("🚖 **Kiwitaxi**")
    partner_button("Kiwitaxi", TAXI_LINK, "btn_taxi.png")

# --- FOOTER SEO ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: justify; color: #555;">
    <h3>{ui["footer_seo_title"]}</h3>
    <p>
        <strong>30SecondsToGuide</strong> {ui["footer_seo_text"]}
    </p>
</div>
""", unsafe_allow_html=True)







