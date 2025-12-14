import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
import base64
import datetime
import unicodedata
import json

# --- 0. CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="30SecondsToGuide", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️", layout="centered")

# --- MEMORIA LOG (JSON) ---
LOG_FILE = "admin_stats.json"

def load_logs():
    """Carica i log dal file JSON."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def add_log(entry):
    """Aggiunge una nuova ricerca e salva su file."""
    logs = load_logs()
    logs.append(entry)
    if len(logs) > 100: logs = logs[-100:] # Mantieni solo ultimi 100
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# --- CONFIGURAZIONE API ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

# ==========================================
# 🌐 CONFIGURAZIONE CROSS-PROMO
# ==========================================
WIZARD_APP_URL = "https://www.30secondstoguide.it" 
PROMO_IMG_WIZARD = "promo_to_wizard.jpg" # IMMAGINE 1: Cerchio su "APRI ITINERARY WIZARD"

# ==========================================
# 💰 AREA MONETIZZAZIONE & PARTNER
# ==========================================

# 1. LINK TRACCIATI (Attivi)
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"            # Voli
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW" # Bagagli
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"          # Rimborsi
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"             # eSim
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"      # Auto Europe
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"                 # Transfer / NCC
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"          # Taxi
TIQETS_LINK = "https://tiqets.tpx.lt/XV1Urbnn"          # Biglietti Musei

# LINK HEYMONDO (Affiliato)
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"

# 2. LINK GENERICI (Statici)
TRAIN_LINK = "https://www.omio.com"
RESTAURANT_LINK = "https://www.tripadvisor.com"
HOTEL_LINK = "https://www.expedia.com" 

# --- LINK PROMOZIONE ---
PROMO_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL" 

# --- Funzione Helper per Bottoni con Logo ---
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

# ==========================================

# --- MODELLO TESTO PROMPT ---
TESTO_MODELLO = """
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

# --- FUNZIONE PDF ---
def create_pdf(text, city):
    
    # --- FUNZIONE SPAZZINO 5.0 (SMART ACCENTS) ---
    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        
        # 1. Mappatura manuale per simboli problematici noti
        replacements = {
            "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...",
            "€": "EUR", "$": "USD", "£": "GBP",
            "ł": "l", "Ł": "L", "đ": "d", "Đ": "D", "ø": "o", "Ø": "O",
            "©": "(c)", "®": "(r)"
        }
        for char, replacement in replacements.items():
            text_input = text_input.replace(char, replacement)

        # 2. Normalizzazione NFC (IMPORTANTE: Mantiene uniti accenti e lettere -> 'à' resta 'à')
        text_input = unicodedata.normalize('NFC', text_input)
        
        output = []
        for char in text_input:
            try:
                # 3. Test: il carattere è supportato nativamente da Latin-1?
                char.encode('latin-1')
                output.append(char)
            except UnicodeEncodeError:
                # 4. Se fallisce, decomponiamo e prendiamo la base
                decomposed = unicodedata.normalize('NFD', char)
                base_char = decomposed[0]
                try:
                    base_char.encode('latin-1')
                    output.append(base_char)
                except UnicodeEncodeError:
                    # 5. Se anche la base non va, lo ignoriamo
                    pass
                    
        return "".join(output)

    city_clean = clean_text_for_pdf(city)

    class ModernPDF(FPDF):
        def header(self):
            # FIX: Salta intestazione su Cover (1) E su Promo (2)
            if self.page_no() <= 2: return 
            
            self.set_fill_color(44, 62, 80) 
            self.rect(0, 0, 210, 20, 'F')
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(255, 255, 255)
            self.set_y(8)
            self.cell(0, 0, f'GUIDA: {city_clean.upper()}', 0, 0, 'R')
            self.ln(20) 
            
        def footer(self):
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - Pagina {self.page_no()}', 0, 0, 'C')

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
            self.multi_cell(0, 10, "Guida turistica completa\nItinerari, Storia e Cultura")
            self.ln(20)
            self.set_fill_color(230, 126, 34) 
            self.rect(70, self.get_y(), 100, 2, 'F')
            self.set_y(225) 
            self.set_x(70)
            self.set_font('Helvetica', 'I', 9) 
            self.set_text_color(100, 100, 100)
            disclaimer = "Questa guida è offerta gratuitamente. Se ti è utile, nell'ultima pagina trovi una selezione di sconti esclusivi per voli e hotel che ci aiutano a mantenere il servizio attivo. Buon viaggio!"
            self.multi_cell(110, 5, disclaimer)
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'BU', 10) 
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, "GENERATO CON www.30secondstoguide.it", link="https://www.30secondstoguide.it")

    # --- FUNZIONE PAGINA PROMO ---
    def add_promo_page(pdf_obj):
        # Se non c'è l'immagine, non facciamo nulla (evitiamo pagine bianche a caso)
        if not os.path.exists(PROMO_IMG_WIZARD): return

        pdf_obj.add_page()
        
        # 1. Immagine Screenshot
        # Posizionata in alto (Y=30), larga 180mm (margini 15mm)
        pdf_obj.image(PROMO_IMG_WIZARD, x=15, y=30, w=180)
        
        # 2. Box CTA
        box_y = 160 
        pdf_obj.set_fill_color(155, 89, 182) # Viola per rimandare al Wizard
        pdf_obj.set_draw_color(142, 68, 173)
        pdf_obj.rect(15, box_y, 180, 30, 'DF')
        
        # 3. Testo e Link
        pdf_obj.set_y(box_y + 8)
        pdf_obj.set_font("Helvetica", 'B', 14)
        pdf_obj.set_text_color(255, 255, 255)
        
        cta_text = "Clicca qui se vuoi un itinerario personalizzato in base alla durata e al tuo budget."
        pdf_obj.set_x(15)
        pdf_obj.multi_cell(180, 8, cta_text, align='C', link=WIZARD_APP_URL)

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # 1. Copertina (Pagina 1)
    pdf.make_cover(city_clean)
    
    # 2. Pagina Promo (Pagina 2)
    add_promo_page(pdf)
    
    # 3. FIX: Nuova pagina ORA, così la guida parte pulita a pag 3
    pdf.add_page()
    
    lines = text.split('\n')
    
    # --- NUOVO BOX "MAGAZINE STYLE" (Uniformato a itinerari.py) ---
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
        
        # --- FIX PAGE BREAK ---
        if pdf_obj.get_y() > 250: 
             pdf_obj.add_page()   

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
    # ----------------------------------------

    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
        # --- INIEZIONI CONTESTUALI (Uniformate) ---
        
        if line.startswith('## 2. Quartieri'):
            make_box(pdf, f"Non restare senza internet a {city_clean}? eSim Saily (Sconto 5%)", ESIM_LINK, style="yellow")
        
        if line.startswith('## 4. Gastronomia'):
            make_box(pdf, f"Prezzi Hotel in aumento a {city_clean}? Verifica disponibilità su Expedia", HOTEL_LINK, style="blue")
            
        if line.startswith('## 6. I mercati'):
             make_box(pdf, f"Biglietti ufficiali Musei e Attrazioni a {city_clean} su Tiqets", TIQETS_LINK, style="orange")

        if line.startswith('## 9. Itinerario'):
             make_box(pdf, f"Trova subito voli economici per {city_clean} su Kiwi.com", FLIGHT_LINK, style="green")
             make_box(pdf, f"Transfer NCC dall'aeroporto al prezzo di un taxi (Welcome Pickups)", TRANSF_LINK, style="purple")
             make_box(pdf, "Assicurazione Viaggio (Sconto 10% con Heymondo)", INSURANCE_LINK, style="green")
        # --------------------------------

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
            if line.strip().startswith('* '): content_raw = line.strip()[2:] 
            else: content_raw = line.strip()[2:]
            
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

    # --- PAGINA PARTNER FINALE ---
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

    # 1. Partner già apparsi nel testo
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Già visti nella guida...", 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Expedia", "Hotel e alloggi", HOTEL_LINK) 
    make_sponsor_box("Tiqets", "Biglietti musei e attrazioni", TIQETS_LINK) 
    make_sponsor_box("Kiwi.com", "Voli low cost", FLIGHT_LINK)
    make_sponsor_box("Heymondo", "Assicurazione viaggio", INSURANCE_LINK)
    make_sponsor_box("Saily", "eSim internazionale", ESIM_LINK)
    make_sponsor_box("Welcome Pickups", "Transfer aeroportuali", TRANSF_LINK)

    pdf.ln(5)
    
    # 2. Partner NUOVI
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 10, "ALTRI SERVIZI INDISPENSABILI", 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Deposito Bagagli", "Libera le mani con Radical Storage", LUGGAGE_LINK, highlight=True)
    make_sponsor_box("Rimborsi Voli", "Volo in ritardo? Chiedi risarcimento con AirHelp", REIMB_LINK, highlight=True)
    make_sponsor_box("Noleggio Auto", "Migliori tariffe con Auto Europe", RENTAL_LINK, highlight=True)
    make_sponsor_box("Treni e Bus", "Prenota con Omio", TRAIN_LINK, highlight=True)
    make_sponsor_box("Taxi Locale", "Kiwitaxi per spostamenti urbani", TAXI_LINK, highlight=True)
    make_sponsor_box("Ristoranti", "Recensioni su TripAdvisor", RESTAURANT_LINK, highlight=True)

    return bytes(pdf.output(dest='S'))

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("⏱️")
    
    st.markdown("---")
    st.caption("✈️ PRENOTAZIONI")
    partner_button("Voli (Kiwi)", FLIGHT_LINK, "btn_kiwi.png")
    partner_button("Hotel (Expedia)", HOTEL_LINK, "btn_booking.png") 
    partner_button("Transfers (Welcome)", TRANSF_LINK, "btn_wp.png")
    partner_button("Auto (Autoeurope)", RENTAL_LINK, "btn_autoe.png")
    partner_button("Treni (Omio)", TRAIN_LINK, "btn_omio.png")
    partner_button("Taxi (Kiwitaxi)", TAXI_LINK, "btn_taxi.png")
    
    st.caption("🎟️ ESPERIENZE & ALTRO")
    partner_button("Musei & Ticket (Tiqets)", TIQETS_LINK, "btn_tiqets.png") 
    partner_button("Ristoranti (Tripadvisor)", RESTAURANT_LINK, "btn_tripadv.png")
    
    st.caption("🛠️ SERVIZI UTILI")
    partner_button("eSim (Saily)", ESIM_LINK, "btn_saily.png")
    partner_button("Bagagli (Radical)", LUGGAGE_LINK, "btn_radical.png")
    partner_button("Polizza (Heymondo)", INSURANCE_LINK, "btn_heymondo.png")
    partner_button("Rimborsi (Airhelp)", REIMB_LINK, "btn_airhelp.png")
    
    # --- AREA ADMIN SEGRETA ---
    with st.sidebar.expander("🔐 Admin Stats"):
        secret_pwd = st.text_input("Password", type="password")
        if secret_pwd == "fabio123": 
            st.write("### 📊 Ultime Ricerche:")
            # MODIFICA: Uso load_logs()
            logs = load_logs()
            if logs:
                for log in reversed(logs):
                    st.caption(log)
            else:
                st.caption("Nessuna ricerca ancora.")
            st.write(f"**Totale:** {len(logs)}")

    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")
    st.page_link("pages/privacy.py", label="Privacy Policy", icon="🔒")

# --- CORPO CENTRALE ---
if os.path.exists("logo.png"):
    col_sp1, col_img, col_sp2 = st.columns([3, 2, 3])
    with col_img:
        st.image("logo.png", use_container_width=True)

st.markdown("""
    <h1 style='text-align: center; color: #2C3E50; margin-bottom: 0; margin-top: -10px;'>
        Generatore Guide Turistiche
    </h1>
    <p style='text-align: center; color: #E67E22; font-size: 1.2em; font-style: italic; margin-top: 5px;'>
        Da zero a local in mezzo minuto.
    </p>
    """, unsafe_allow_html=True)

# ==========================================
# 🆕 CTA WIZARD (MOBILE FRIENDLY)
# ==========================================
st.write("") 

# 1. Testo descrittivo "Gradient Style"
st.markdown("""
<div style="background-color: #f0f2f6; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: center; border: 1px solid #dcdcdc;">
    <h3 style="margin: 0; color: #4A00E0; font-size: 1.2em;">🧙‍♂️ Vuoi chiedere al nostro Wizard di organizzare il tuo viaggio personalizzato?</h3>
    <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #333;">
        Verifica il tuo budget, crea il tuo itinerario su misura, interroga qui sotto il nostro mago.
    </p>
</div>
""", unsafe_allow_html=True)

# 2. Bottone con Etichetta CORTA (Anti-Troncamento)
with st.container(border=True):
    st.page_link("pages/itinerari.py", label="✨ APRI ITINERARY WIZARD", use_container_width=True)

st.write("") 

# ==========================================
# 📢 AREA PROMO AUTOMATICA
# ==========================================
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

# --- FUNZIONE RESET ---
def reset_app():
    if 'generated_pdf' in st.session_state:
        del st.session_state['generated_pdf']
    if 'last_city' in st.session_state:
        del st.session_state['last_city']
    st.session_state.city_input = ""

# Collegamento variabile input
city_name = st.text_input("Se vuoi generare la guida specifica di una città inserisci QUI la destinazione:", placeholder="Es. Parigi, Tokyo, New York...", key="city_input")

# --- GENERAZIONE GUIDA ---
with st.container():
    # Logica Bottone: Se c'è già un PDF, il bottone Genera è disabilitato
    is_generated = 'generated_pdf' in st.session_state
    
    if st.button("Genera Guida PDF", type="primary", use_container_width=True, disabled=is_generated):
        if not city_name:
            st.warning("Inserisci una città.")
        else:
            # DATA NEL LOG
            timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
            # MODIFICA: Uso add_log() invece di get_shared_logs()
            add_log(f"📍 {city_name} ({timestamp})")
            
            with st.spinner("Stiamo scrivendo la tua guida... (non chiudere la pagina)"):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    full_prompt = f"""
                    Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA per: {city_name}.
                    
                    REGOLE FONDAMENTALI:
                    1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                    2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                    3. Usa ESATTAMENTE la struttura seguente.
                    4. Scrivi paragrafi ricchi e lunghi.
                    5. NON USARE MAI CARATTERI SPECIALI, simboli delle valute (come Euro o Dollaro), semplifica la grafia delle parole straniere utilizzando l'alfabeto standard, ammesse SOLO lettere accentate comunemente usate in italiano.
                    6. Se viene inserita una nazione, una regione, un'area geografica produci la guida per la città principale, aggiungi una premessa prima del capitolo 1 in cui elenchi eventuali altre città esortando a fare guide separate, suggerisci anche di utilizzare il bottone dell'"ITINERARY WIZARD" che trovano nel sito.
                    7. Se viene inserita un parola o una frase che non sono luoghi geografici rispondi in modo scherzoso ma sintetico, non usare la struttura della guida.
                    
                    MODELLO:
                    {TESTO_MODELLO}
                    """
                    
                    response = model.generate_content(full_prompt)
                    markdown_content = response.text
                    
                    # Salva in sessione
                    st.session_state['generated_pdf'] = create_pdf(markdown_content, city_name)
                    st.session_state['last_city'] = city_name
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Errore: {e}")

# --- DOWNLOAD BUTTON CON RESET ---
if 'generated_pdf' in st.session_state:
    st.success(f"✅ Guida per {st.session_state['last_city']} pronta!")
    st.download_button(
        label="🎨 SCARICA GUIDA PDF PRO",
        data=st.session_state['generated_pdf'],
        file_name=f"Guida_{st.session_state['last_city']}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
        on_click=reset_app 
    )

# =========================================================
# 🏨 TRAVEL HUB (GRID 4x3)
# =========================================================
st.markdown("---")
if city_name:
    st.subheader(f"✈️ Organizza il viaggio a {city_name}")
else:
    st.subheader("✈️ I migliori strumenti per il tuo viaggio")

# RIGA 1
c1, c2, c3 = st.columns(3)
with c1:
    st.caption("✈️ **Voli**")
    partner_button("Voli Kiwi", FLIGHT_LINK, "btn_kiwi.png")
with c2:
    st.caption("🏨 **Hotel**")
    partner_button("Expedia", HOTEL_LINK, "btn_booking.png") 
with c3:
    st.caption("🚘 **Transfer**")
    partner_button("Welcome Pickups", TRANSF_LINK, "btn_wp.png")

st.write("") 

# RIGA 2
c4, c5, c6 = st.columns(3)
with c4:
    st.caption("🎟️ **Tour**")
    partner_button("Tiqets", TIQETS_LINK, "btn_tiqets.png") 
with c5:
    st.caption("🚗 **Auto**")
    partner_button("Noleggio", RENTAL_LINK, "btn_autoe.png")
with c6:
    st.caption("🎒 **Bagagli**")
    partner_button("Deposito", LUGGAGE_LINK, "btn_radical.png")

st.write("") 

# RIGA 3
c7, c8, c9 = st.columns(3)
with c7:
    st.caption("📲 **Dati**")
    partner_button("eSim Saily", ESIM_LINK, "btn_saily.png")
with c8:
    st.caption("🛡️ **Polizza**")
    partner_button("Assicuraz.", INSURANCE_LINK, "btn_heymondo.png")
with c9:
    st.caption("💸 **Risarcim.**")
    partner_button("AirHelp", REIMB_LINK, "btn_airhelp.png")

st.write("") 

# RIGA 4
c10, c11, c12 = st.columns(3)
with c10:
    st.caption("🚆 **Treni**")
    partner_button("Omio", TRAIN_LINK, "btn_omio.png")
with c11:
    st.caption("🍴 **Ristoranti**")
    partner_button("Tripadvisor", RESTAURANT_LINK, "btn_tripadv.png")
with c12:
    st.caption("🚖 **Taxi**")
    partner_button("Kiwitaxi", TAXI_LINK, "btn_taxi.png")

# --- SEZIONE SEO ---
st.markdown("---")
st.markdown("""
<div style="text-align: justify; color: #555;">
    <h3>Come funziona 30SecondsToGuide?</h3>
    <p>
        <strong>30SecondsToGuide</strong> è il primo generatore di guide turistiche basato sull'Intelligenza Artificiale. 
        A differenza dei tradizionali blog di viaggio, il nostro algoritmo crea <strong>itinerari personalizzati in PDF</strong> 
        per qualsiasi città del mondo in meno di 30 secondi.
    </p>
    <p>
        Il servizio è <strong>gratuito al 100%</strong>.
    </p>
</div>
""", unsafe_allow_html=True)






