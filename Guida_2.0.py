import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
import base64
import datetime

# --- MEMORIA CONDIVISA (LOG) ---
@st.cache_resource
def get_shared_logs():
    return [] 

# --- CONFIGURAZIONE ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

genai.configure(api_key=API_KEY)

# ==========================================
# 💰 AREA MONETIZZAZIONE
# ==========================================
# 1. CODICI NUMERICI
BOOKING_AID = "000000"  
GYG_PARTNER_ID = "000000" 

# 2. LINK TRACCIATI (Attivi)
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"            # Voli
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW" # Bagagli
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"          # Rimborsi
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"             # eSim
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"      # Auto Europe

# LINK HEYMONDO (Affiliato)
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"

# 3. LINK GENERICI (In attesa)
TRAIN_LINK = "https://www.omio.com"             

# --- LINK PROMOZIONE (Banner Black Friday) ---
PROMO_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL" 

# --- Funzioni Link ---
def get_booking_link(city):
    if BOOKING_AID == "000000": return "https://www.booking.com"
    return f"https://www.booking.com/searchresults.html?ss={city}&aid={BOOKING_AID}"

def get_gyg_link(city):
    if GYG_PARTNER_ID == "000000": return "https://www.getyourguide.com"
    return f"https://www.getyourguide.com/s?q={city}&partner_id={GYG_PARTNER_ID}"

# --- Funzione Helper per Bottoni con Logo ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def partner_button(label, link, image_file):
    if os.path.exists(image_file):
        # Se c'è il logo, mostra immagine cliccabile
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
        # Fallback: Se manca il logo, mostra il bottone classico
        st.link_button(label, link, use_container_width=True)
# ==========================================


# --- MODELLO TESTO (12 PUNTI) ---
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
    class ModernPDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
            self.set_fill_color(44, 62, 80) 
            self.rect(0, 0, 210, 20, 'F')
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(255, 255, 255)
            self.set_y(8)
            self.cell(0, 0, f'GUIDA: {city.upper()}', 0, 0, 'R')
            self.ln(20) 
            
        def footer(self):
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - Pagina {self.page_no()}', 0, 0, 'C')

        def make_cover(self, city_name):
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
            self.multi_cell(0, 20, city_name.upper())
            
            self.ln(10)
            self.set_x(70)
            self.set_font('Helvetica', '', 16)
            self.set_text_color(127, 140, 141)
            self.multi_cell(0, 10, "Guida turistica completa\nItinerari, Storia e Cultura")
            
            self.ln(20)
            self.set_fill_color(230, 126, 34) 
            self.rect(70, self.get_y(), 100, 2, 'F')
            
            # --- MESSAGGIO GRATUITO (DISCLAIMER) ---
            self.set_y(225) 
            self.set_x(70)
            self.set_font('Helvetica', 'I', 9) 
            self.set_text_color(100, 100, 100)
            disclaimer = "Questa guida è offerta gratuitamente. Se ti è utile, nell'ultima pagina trovi una selezione di sconti esclusivi per voli e hotel che ci aiutano a mantenere il servizio attivo. Buon viaggio!"
            self.multi_cell(110, 5, disclaimer)
            # ---------------------------------------
            
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(44, 62, 80)
            # --- MODIFICA LINK SITO WEB ---
            self.cell(0, 10, "GENERATO CON www.30secondstoguide.it", link="https://www.30secondstoguide.it")

    # --- FUNZIONE SPAZZINO (Cruciale per non crashare) ---
    def clean_text_for_pdf(text_line):
        replacements = {
            "€": "EUR", "$": "USD", "£": "GBP",
            "’": "'", "“": '"', "”": '"', "–": "-", "…": "..."
        }
        for char, replacement in replacements.items():
            text_line = text_line.replace(char, replacement)
        return text_line.encode('latin-1', 'replace').decode('latin-1')

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.make_cover(city)
    pdf.add_page()
    
    lines = text.split('\n')
    
    for line in lines:
        clean_line = clean_text_for_pdf(line)
        
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
