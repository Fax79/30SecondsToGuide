import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os

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
BOOKING_AID = "000000"  
GYG_PARTNER_ID = "000000" 

ALOSIM_LINK = "https://www.alosim.com" 
AURAS_LINK = "https://www.aurasinsure.com"

def get_booking_link(city):
    if BOOKING_AID == "000000": return "https://www.booking.com"
    return f"https://www.booking.com/searchresults.html?ss={city}&aid={BOOKING_AID}"

def get_gyg_link(city):
    if GYG_PARTNER_ID == "000000": return "https://www.getyourguide.com"
    return f"https://www.getyourguide.com/s?q={city}&partner_id={GYG_PARTNER_ID}"
# ==========================================


# --- IL NUOVO MODELLO STANDARD (Avanzato) ---
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
* **[Monumento 1]:** [Descrizione]
* **[Monumento 2]:** [Descrizione]
* **[Monumento 3]:** [Descrizione]
* **[Monumento 4]:** [Descrizione]
* **[Monumento 5]:** [Descrizione]

## 6. I mercati
* **[Mercato 1]:** [Descrizione]
* **[Mercato 2]:** [Descrizione]

## 7. Calendario Culturale
[I principali festival, fiere, ricorrenze e feste della città].

## 8. Info Pratiche
* **Trasporti:** [Info]
* **Sicurezza:** [Info]
* **Clima:** [Info sui migliori periodi per visitare la città]
* **Visti e requisiti per l'ingresso nel paese:** [Info]
* **Fuso orario:** [Info]
* **Consigli utili:** [Info su valuta locale e prese elettriche, non usare mai simboli delle valute ma i loro codici, es. EUR, USD, GBP, ecc]

## 9. Itinerario 3 Giorni
* **Giorno 1:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore del susseguirsi delle tappe per razionalizzare i tempi]
* **Giorno 2:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore del susseguirsi delle tappe per razionalizzare i tempi]
* **Giorno 3:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore del susseguirsi delle tappe per razionalizzare i tempi]

## 10. Itinerario 5 Giorni
* **Giorni 1-3:** Come sopra.
* **Giorno 4:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore del susseguirsi delle tappe per razionalizzare i tempi]
* **Giorno 5:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore del susseguirsi delle tappe per razionalizzare i tempi]

## 11. Se hai più tempo
* **Fuori dai sentieri battuti:** [Un quartiere meno turistico].
* **Gite fuori porta:** [Una o più gita di mezza giornata o di un giorno nei dintorni, link get your guide].

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
            
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, "GENERATO DA 30SecondsToGuide")

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.make_cover(city)
    pdf.add_page()
    
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        
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
            content = content_raw.replace('*', '')
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

    # --- PAGINA SPONSOR ---
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "LINK UTILI PER IL VIAGGIO", 0, 1, 'C')
    pdf.ln(5)
    
    def make_sponsor_box(title, subtitle, link):
        pdf.set_fill_color(245, 245, 245)
        start_y = pdf.get_y()
        pdf.rect(10, start_y, 190, 30, 'F')
        
        pdf.set_y(start_y + 5)
        pdf.set_x(15)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 5, title, 0, 1)
        
        pdf.set_x(15)
        pdf.set_font("Helvetica", '', 10)
        pdf.set_text_color(0, 102, 204)
        
        pdf.cell(0, 8, subtitle, 0, 1, link=link)
        pdf.ln(15)

    make_sponsor_box("Dove Dormire", f"Trova le migliori offerte hotel a {city} su Booking.com", get_booking_link(city))
    make_sponsor_box("Cosa Fare", f"Salta la fila: Biglietti e Tour a {city}", get_gyg_link(city))
    make_sponsor_box("Connettività (eSim)", "Naviga subito all'estero senza roaming costoso con AloSIM", ALOSIM_LINK)
    make_sponsor_box("Assicurazione Viaggio", "Parti senza pensieri con la protezione di Auras", AURAS_LINK)

    return bytes(pdf.output(dest='S'))

# --- INTERFACCIA ---
if os.path.exists("logo.png"):
    st.set_page_config(page_title="30SecondsToGuide", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️", layout="centered")

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("⏱️")
    
    st.markdown("---")
    st.header("🧳 Organizza")
    
    st.info("🏨 **Hotel & Alloggi**")
    st.link_button("Vedi offerte su Booking", get_booking_link(""))
    
    st.info("🎟️ **Tour & Biglietti**")
    st.link_button("Prenota su GetYourGuide", get_gyg_link(""))
    
    st.divider()
    st.markdown("### 🛠️ Utilità")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.caption("📲 **eSim**")
        st.link_button("AloSIM", ALOSIM_LINK)
    with col_sb2:
        st.caption("🛡️ **Polizza**")
        st.link_button("Auras", AURAS_LINK)
    
    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")
    st.page_link("pages/privacy.py", label="Privacy Policy", icon="🔒")

# --- CORPO CENTRALE (MOBILE FRIENDLY) ---

# 1. Logo Mobile (Centrato)
if os.path.exists("logo.png"):
    col_sp1, col_img, col_sp2 = st.columns([3, 2, 3])
    with col_img:
        st.image("logo.png", use_container_width=True)

# 2. Titolo Brandizzato
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50; margin-bottom: 0; margin-top: -10px;'>
        Generatore Guide Turistiche
    </h1>
    <p style='text-align: center; color: #E67E22; font-size: 1.2em; font-style: italic; margin-top: 5px;'>
        Da zero a local in mezzo minuto.
    </p>
    """, unsafe_allow_html=True)

st.write("") # Spaziatura

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo, New York...")

# 3. Bottone Largo e Centrato
if st.button("Genera Guida PDF", type="primary", use_container_width=True):
    if not city_name:
        st.warning("Inserisci una città.")
    else:
        with st.spinner("Sto scrivendo e impaginando la guida... non chiudere la pagina"):
            try:
                # USARE GEMINI 1.5 FLASH (2.5 non esiste ancora pubblicamente)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                full_prompt = f"""
                Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA per: {city_name}.
                
                REGOLE FONDAMENTALI:
                1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                3. Usa ESATTAMENTE la struttura seguente.
                4. Scrivi paragrafi ricchi e lunghi.
                5. NON USARE MAI CARATTERI SPECIALI, anche se semplifica la grafia delle parole straniere utilizzando l'alfabeto standard.
                6. Se viene inserita un parola che non è una città o una frase rispondi in modo scherzoso.
                
                MODELLO:
                {TESTO_MODELLO}
                """
                
                response = model.generate_content(full_prompt)
                markdown_content = response.text
                
                with st.expander("Anteprima Testo"):
                    st.markdown(markdown_content)
                
                pdf_bytes = create_pdf(markdown_content, city_name)
                
                st.success("✅ Guida pronta!")
                st.download_button(
                    label="🎨 SCARICA GUIDA PDF PRO",
                    data=pdf_bytes,
                    file_name=f"Guida_{city_name}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                # Banner sotto il download
                st.markdown("---")
                st.subheader(f"✈️ Pronto a partire per {city_name}?")
                
                c1, c2 = st.columns(2)
                c3, c4 = st.columns(2)
                
                with c1:
                    st.markdown(f"🏨 **Hotel**")
                    st.link_button("Vedi Offerte", get_booking_link(city_name))
                with c2:
                    st.markdown(f"🎟️ **Tour**")
                    st.link_button("Prenota Attività", get_gyg_link(city_name))
                with c3:
                    st.markdown(f"📲 **eSim Dati**")
                    st.link_button("AloSIM", ALOSIM_LINK)
                with c4:
                    st.markdown(f"🛡️ **Assicurazione**")
                    st.link_button("Auras", AURAS_LINK)
                
            except Exception as e:
                st.error(f"Errore: {e}")

