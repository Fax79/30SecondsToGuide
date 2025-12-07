import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64
import datetime
import unicodedata
import os
import re

# --- CONFIGURAZIONE PAGINA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="Itinerary Wizard", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="Itinerary Wizard", page_icon="🧙‍♂️", layout="centered")

# --- MEMORIA & API ---
@st.cache_resource
def get_shared_logs():
    return [] 

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

# ==========================================
# 💰 AREA MONETIZZAZIONE
# ==========================================
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://saily.tpx.lt/Myxhqmox"
RENTAL_LINK = "https://autoeurope.tpx.lt/73PS7HAR"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://tiqets.tpx.lt/XV1Urbnn"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=INPUT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
TRAIN_LINK = "https://www.omio.com"
RESTAURANT_LINK = "https://www.tripadvisor.com"
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

# ==========================================
# 🧙‍♂️ PDF ENGINE (SAFE MODE v8.0)
# ==========================================
def create_complex_pdf(text, destination, meta_data):
    
    # --- FUNZIONE SPAZZINO ---
    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        text_input = text_input.replace("**", "") 
        replacements = {
            "€": "EUR", "â¬": "EUR", "$": "USD", "£": "GBP",
            "'": "'", "'": "'", """: '"', """: '"', "–": "-", "—": "-", "…": "..."
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
            if self.page_no() == 1: return
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
            self.cell(0, 10, f'30SecondsToGuide - Pagina {self.page_no()}', 0, 0, 'C')

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
            self.cell(0, 10, "Travel Plan Esclusivo", 0, 1, 'C')
            self.ln(20)
            self.set_fill_color(255, 255, 255)
            self.rect(55, 140, 100, 50, 'F')
            self.set_y(145)
            self.set_font('Helvetica', 'B', 10)
            clean_budget = clean_text_for_pdf(meta['budget'])
            self.cell(0, 6, f"Date: {meta['dates']}", 0, 1, 'C')
            self.cell(0, 6, f"Viaggiatori: {meta['pax']}", 0, 1, 'C')
            self.cell(0, 6, f"Budget Target: {clean_budget}", 0, 1, 'C')
            self.set_y(260)
            self.set_font('Helvetica', '', 10)
            self.cell(0, 10, "GENERATO CON www.30secondstoguide.it", 0, 0, 'C', link="https://www.30secondstoguide.it")

    # --- CONFIGURAZIONE MARGINI E PAGINA ---
    pdf = WizardPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=25)
    
    pdf.make_cover(dest_clean, meta_data)
    pdf.add_page()
    
    # --- BOX CONTESTUALE (SAFE) ---
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
        
        if pdf_obj.get_y() > 250: 
             pdf_obj.add_page()   

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
    
    inserted_ch1 = False
    inserted_ch2 = False
    inserted_ch3 = False
    inserted_ch4 = False

    for line in lines:
        clean_line = clean_text_for_pdf(line)
        line_upper = clean_line.upper()
        
        # --- LOGICA LINK ---
        if "## CAPITOLO 2" in line_upper and not inserted_ch1:
            banner_text = f"In {month_clean} i prezzi aumentano? Prenota ora su Kiwi.com"
            make_box(pdf, banner_text, FLIGHT_LINK, "green")
            make_box(pdf, "eSim Saily: Internet immediato all'arrivo senza acquisto di SIM locali", ESIM_LINK, "yellow")
            make_box(pdf, "MAI senza Assicurazione Sanitaria: Approfitta QUI dello sconto 10% con Heymondo", INSURANCE_LINK, "green")
            inserted_ch1 = True
            
        elif "## CAPITOLO 3" in line_upper and not inserted_ch2:
            make_box(pdf, f"Stanze in Hotel quasi esaurite in {month_clean}? Prenota ora su Expedia", HOTEL_LINK, "blue")
            make_box(pdf, "Transfer privati ad un prezzo WOW! da e per l'aeroporto", TRANSF_LINK, "purple")
            inserted_ch2 = True

        elif "## CAPITOLO 4" in line_upper and not inserted_ch3:
            make_box(pdf, f"Biglietti Attrazioni saltando la fila per il tuo tour in {dest_clean} su Tiqets", TIQETS_LINK, "orange")
            make_box(pdf, "Viaggia in libertà e noleggia un auto: Tariffe esclusive con Auto Europe", RENTAL_LINK, "purple")
            make_box(pdf, "Treni e Bus: Prenota su Omio", TRAIN_LINK, "purple")
            inserted_ch3 = True
            
        elif "## CAPITOLO 5" in line_upper and not inserted_ch4:
            make_box(pdf, "Ristoranti: Leggi le recensioni su TripAdvisor", RESTAURANT_LINK, "green")
            inserted_ch4 = True

        # --- FORMATTAZIONE TESTO ---
        # Larghezza effettiva disponibile: 210mm - 15mm (sx) - 15mm (dx) = 180mm
        
        if line.strip().startswith('# '): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(0, 10, clean_line.replace('#', '').strip())
            pdf.ln(5)
            
        elif line.strip().startswith('## '): 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(230, 126, 34) 
            pdf.multi_cell(0, 10, clean_line.replace('##', '').strip())
            
        elif "VERDETTO" in line_upper: 
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_fill_color(220, 220, 220)
            clean_verdict = clean_line.replace('*', '').strip()
            pdf.multi_cell(0, 8, clean_verdict, border=1, align='C', fill=True)
            pdf.ln(5)
            
        elif line.strip().startswith('* ') or line.strip().startswith('- '): 
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(20, 20, 20)
            pdf.set_x(20)
            pdf.cell(5, 6, chr(149), 0, 0)
            content = re.sub(r'^[\*-]\s*', '', clean_line).strip()
            
            if content:
                # Larghezza per bullet: 180mm - 5mm (rientro da 15 a 20) - 5mm (bullet) = 170mm
                pdf.multi_cell(170, 6, content) 
        
        elif re.match(r'^\d+\.', line.strip()):
            pdf.set_font("Helvetica", 'B', 11)
            pdf.set_text_color(44, 62, 80)
            pdf.ln(2)
            pdf.multi_cell(0, 6, clean_line)
            
        else: 
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                # Usa 0 per sfruttare tutta la larghezza disponibile tra i margini
                pdf.multi_cell(0, 6, clean_line)
                pdf.ln(1)

    # --- PAGINA PARTNER ---
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
    pdf.cell(0, 10, "Già visti nella guida...", 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Expedia", "Hotel e Voli", HOTEL_LINK)
    make_sponsor_box("Tiqets", "Biglietti musei e attrazioni", TIQETS_LINK) 
    make_sponsor_box("Welcome Pickups", "Transfer aeroportuali", TRANSF_LINK) 
    make_sponsor_box("Auto Europe", "Noleggio Auto", RENTAL_LINK)           
    make_sponsor_box("Omio", "Treni e Bus", TRAIN_LINK)                     
    make_sponsor_box("Kiwi.com", "Voli low cost", FLIGHT_LINK)
    make_sponsor_box("Heymondo", "Assicurazione viaggio", INSURANCE_LINK)
    make_sponsor_box("Saily", "eSim internazionale", ESIM_LINK)
    make_sponsor_box("TripAdvisor", "Recensioni Ristoranti", RESTAURANT_LINK)

    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 10, "ALTRI SERVIZI INDISPENSABILI", 0, 1, 'L')
    pdf.ln(2)
    
    make_sponsor_box("Deposito Bagagli", "Libera le mani con Radical Storage", LUGGAGE_LINK, highlight=True)
    make_sponsor_box("Rimborsi Voli", "Volo in ritardo? Chiedi risarcimento con AirHelp", REIMB_LINK, highlight=True)
    make_sponsor_box("Taxi Locale", "Kiwitaxi per spostamenti urbani", TAXI_LINK, highlight=True)

    return bytes(pdf.output(dest='S'))
