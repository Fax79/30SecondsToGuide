import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
import base64
import datetime
import unicodedata

# --- 0. CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="30SecondsToGuide", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️", layout="centered")

# --- MEMORIA CONDIVISA (LOG) ---
@st.cache_resource
def get_shared_logs():
    return [] 

# --- CONFIGURAZIONE API ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

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

# LINK HEYMONDO (Affiliato)
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"

# 2. LINK GENERICI (Statici)
TRAIN_LINK = "https://www.omio.com"
RESTAURANT_LINK = "https://www.tripadvisor.com"
HOTEL_LINK = "https://www.booking.com"
TOUR_LINK = "https://www.getyourguide.com"

# --- LINK PROMOZIONE ---
PROMO_LINK = "https://www.30secondstoguide.it" 

# --- Funzione Helper per Bottoni con Logo ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

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

# --- MODELLO TESTO PROMPT (ORIGINALE) ---
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
    
    # --- FUNZIONE SPAZZINO INTELLIGENTE ---
    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        replacements = {
            "€": "EUR", "$": "USD", "£": "GBP",
            "’": "'", "“": '"', "”": '"', 
            "–": "-", "—": "-", "…": "..."
        }
        for char, replacement in replacements.items():
            text_input = text_input.replace(char, replacement)
        output = ""
        for char in text_input:
            try:
                char.encode('latin-1')
                output += char
            except UnicodeEncodeError:
                output += unicodedata.normalize('NFKD', char).encode('ascii', 'ignore').decode('ascii')
        return output

    city_clean = clean_text_for_pdf(city)

    class ModernPDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
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

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.make_cover(city_clean)
    pdf.add_page()
    
    lines = text.split('\n')
    
    # --- BOX CONTESTUALE DISCRETO ---
    def make_contextual_box(pdf_obj, text, link, r, g, b):
        pdf_obj.ln(2) # Spazio ridotto
        pdf_obj.set_fill_color(r, g, b)
        pdf_obj.set_draw_color(r-10, g-10, b-10) # Bordo appena visibile
        # Altezza ridotta a 12 (molto discreto)
        pdf_obj.rect(15, pdf_obj.get_y(), 180, 10, 'DF')
        
        pdf_obj.set_xy(20, pdf_obj.get_y() + 2)
        pdf_obj.set_font("Helvetica", 'B', 9) # Font più piccolo
        pdf_obj.set_text_color(44, 62, 80)
        
        pdf_obj.cell(170, 6, f"> {text}", link=link) # Freccia semplice
        pdf_obj.ln(12) 
    # ----------------------------------------

    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
        # --- INIEZIONI CONTESTUALI (DISCRETE) ---
        
        # 1. Dopo INTRO (L'Anima): Saily (eSim)
        if line.startswith('## 2. Quartieri'):
            make_contextual_box(pdf, f"Serve internet a {city_clean}? eSim Saily (Sconto 5%)", ESIM_LINK, 240, 255, 240) # Verdino
        
        # 2. Dopo DOVE DORMIRE: Booking
        if line.startswith('## 4. Gastronomia'):
            make_contextual_box(pdf, f"Cerca offerte Hotel a {city_clean} su Booking.com", HOTEL_LINK, 235, 245, 255) # Azzurrino
            
        # 3. Dopo ATTRAZIONI: GetYourGuide
        if line.startswith('## 6. I mercati'):
             make_contextual_box(pdf, f"Biglietti e Tour per {city_clean} (Salta la fila)", TOUR_LINK, 255, 245, 235) # Arancio chiari

        # 4. Inizio INFO PRATICHE (Come Arrivare): Kiwi + Welcome
        if line.startswith('## 8. Info Pratiche'):
             # Qui non usiamo il box, lo mettiamo subito dopo il titolo
             pass 

        # 5. Fine INFO PRATICHE: Heymondo
        if line.startswith('## 9. Itinerario'):
             # Prima dell'itinerario mettiamo il blocco trasporti/sicurezza
             make_contextual_box(pdf, f"Voli economici per {city_clean} su Kiwi.com", FLIGHT_LINK, 245, 245, 245) # Grigio
             make_contextual_box(pdf, f"Transfer NCC dall'aeroporto (Welcome Pickups)", TRANSF_LINK, 245, 245, 245) # Grigio
             make_contextual_box(pdf, "Assicurazione Viaggio (Sconto 10% Heymondo)", INSURANCE_LINK, 255, 252, 220) # Giallo
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
        
        # Se highlight=True, usiamo un colore diverso per enfatizzare quelli NON visti prima
        if highlight:
            pdf.set_fill_color(230, 240, 255) # Azzurrino
            pdf.set_draw_color(0, 102, 204)   # Bordo blu
        else:
            pdf.set_fill_color(250, 250, 250) # Grigio chiarissimo
            pdf.set_draw_color(220, 220, 220) # Bordo grigio
            
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

    # 1. Partner già apparsi nel testo (Discreti)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Già visti nella guida...", 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Booking.com", "Hotel e alloggi", HOTEL_LINK)
    make_sponsor_box("GetYourGuide", "Tour e biglietti", TOUR_LINK)
    make_sponsor_box("Kiwi.com", "Voli low cost", FLIGHT_LINK)
    make_sponsor_box("Heymondo", "Assicurazione viaggio", INSURANCE_LINK)
    make_sponsor_box("Saily", "eSim internazionale", ESIM_LINK)
    make_sponsor_box("Welcome Pickups", "Transfer aeroportuali", TRANSF_LINK)

    pdf.ln(5)
    
    # 2. Partner NUOVI (Enfatizzati come richiesto)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80) # Colore principale scuro
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
    partner_button("Hotel (Booking)", HOTEL_LINK, "btn_booking.png")
    partner_button("Transfers (Welcome)", TRANSF_LINK, "btn_wp.png")
    partner_button("Auto (Autoeurope)", RENTAL_LINK, "btn_autoe.png")
    partner_button("Treni (Omio)", TRAIN_LINK, "btn_omio.png")
    partner_button("Taxi (Kiwitaxi)", TAXI_LINK, "btn_taxi.png")
    
    st.caption("🎟️ ESPERIENZE & ALTRO")
    partner_button("Tour (GetYourGuide)", TOUR_LINK, "btn_gyg.png")
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
            logs = get_shared_logs()
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

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo, New York...")

# --- GENERAZIONE GUIDA ---
with st.container():
    if st.button("Genera Guida PDF", type="primary", use_container_width=True):
        if not city_name:
            st.warning("Inserisci una città.")
        else:
            timestamp = datetime.datetime.now().strftime("%H:%M")
            get_shared_logs().append(f"📍 {city_name} ({timestamp})")
            
            with st.spinner("Stiamo scrivendo la tua guida... (non chiudere la pagina)"):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    # --- PROMPT ORIGINALE ---
                    full_prompt = f"""
                    Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA per: {city_name}.
                    
                    REGOLE FONDAMENTALI:
                    1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                    2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                    3. Usa ESATTAMENTE la struttura seguente.
                    4. Scrivi paragrafi ricchi e lunghi.
                    5. NON USARE MAI CARATTERI SPECIALI, simboli delle valute (come Euro o Dollaro), semplifica la grafia delle parole straniere utilizzando l'alfabeto standard, ammesse SOLO lettere accentate comunemente usate in italiano.
                    6. Se viene inserita un parola che non è una città o una frase rispondi in modo scherzoso.
                    
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

# --- DOWNLOAD BUTTON ---
if 'generated_pdf' in st.session_state:
    st.success(f"✅ Guida per {st.session_state['last_city']} pronta!")
    st.download_button(
        label="🎨 SCARICA GUIDA PDF PRO",
        data=st.session_state['generated_pdf'],
        file_name=f"Guida_{st.session_state['last_city']}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
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
    partner_button("Booking", HOTEL_LINK, "btn_booking.png")
with c3:
    st.caption("🚘 **Transfer**")
    partner_button("Welcome Pickups", TRANSF_LINK, "btn_wp.png")

st.write("") 

# RIGA 2
c4, c5, c6 = st.columns(3)
with c4:
    st.caption("🎟️ **Tour**")
    partner_button("Attività", TOUR_LINK, "btn_gyg.png")
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
