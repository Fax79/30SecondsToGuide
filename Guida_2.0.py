import streamlit.components.v1 as components
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
# 💰 AREA MONETIZZAZIONE (MODIFICA QUI)
# ==========================================
# Appena ricevi i codici da CJ/Booking/GYG, incollali tra le virgolette qui sotto.
# Esempio: BOOKING_AID = "1234567"

BOOKING_AID = "000000"  # <--- Incolla qui il tuo AID di Booking quando arriva
GYG_PARTNER_ID = "000000" # <--- Incolla qui il tuo ID di GetYourGuide

# Link base (Questi si aggiornano automaticamente con i codici sopra)
def get_booking_link(city):
    # Se non hai ancora il codice, manda alla home generica, altrimenti traccia
    if BOOKING_AID == "000000":
        return "https://www.booking.com"
    return f"https://www.booking.com/searchresults.html?ss={city}&aid={BOOKING_AID}"

def get_gyg_link(city):
    if GYG_PARTNER_ID == "000000":
        return "https://www.getyourguide.com"
    return f"https://www.getyourguide.com/s?q={city}&partner_id={GYG_PARTNER_ID}"
# ==========================================

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
[Migliori quartieri dove alloggiare per tipologia di turista/vacanza: in famiglia, in coppia, con un gruppo di amici, viaggiatori anziani (senior). Aggiungi qualche link booking].

## 4. Gastronomia
[Cosa mangiare e dove, la tradizione gastronomica].

### Piatti Imperdibili
* **[Piatto 1]:** [Descrizione e ingredienti]
* **[Piatto 2]:** [Descrizione e ingredienti]
* **[il cibo tradizionale]:** [i migliori ristoranti, i più caratteristici, consigli per risparmiare, link tripadvisor]
* **[bevande tradizionali]:** [i migliori locali, i più caratteristici, consigli per risparmiare, link tripadvisor]

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

# --- FUNZIONE PDF "BRANDED" ---
def create_pdf(text, city):
    class ModernPDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
            
            # Barra Blu
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
            
            # Colonna laterale
            self.set_fill_color(236, 240, 241) 
            self.rect(0, 0, 60, 297, 'F') 
            
            # --- LOGO SULLA COPERTINA ---
            # Verifica se il logo esiste per evitare crash
            if os.path.exists("logo.png"):
                # Inserisce il logo (x, y, larghezza)
                self.image("logo.png", x=70, y=20, w=50)
                y_start = 80 # Se c'è il logo, iniziamo a scrivere più in basso
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
            if line.strip().startswith('* '):
                content_raw = line.strip()[2:] 
            else:
                content_raw = line.strip()[2:]
            
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

    return bytes(pdf.output(dest='S'))

# --- INTERFACCIA ---
# Configurazione pagina con FAVICON (Logo nella scheda browser)
if os.path.exists("logo.png"):
    st.set_page_config(page_title="30SecondsToGuide", page_icon="logo.png", layout="centered")
else:
    st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️", layout="centered")

	<script data-noptimize="1" data-cfasync="false" data-wpfc-render="false">
      (function () {
          var script = document.createElement("script");
          script.async = 1;
          script.src = 'https://emrldco.com/NDc2MjQ0.js?t=476244';
          document.head.appendChild(script);
      })();
    </script>

# --- SIDEBAR CON LOGO ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200) # Mostra il logo grande
    else:
        st.title("⏱️")
		
    st.markdown("---")
    st.header("🧳 Organizza il viaggio")
    st.info("🏨 **Cerchi dove dormire?**")
    st.link_button("Cerca Hotel su Booking", "https://www.booking.com")
    st.divider()
    st.info("🎟️ **Biglietti e Tour**")
    st.link_button("Attività su GetYourGuide", "https://www.getyourguide.com")

# 3. PRIVACY & COPYRIGHT (In fondo - Discreto)
    st.markdown("---")
    st.caption("© 2025 30SecondsToGuide")
    
    # Questo crea il link alla pagina che hai appena creato
    st.page_link("pages/privacy.py", label="Privacy Policy & Cookie", icon="🔒")
	
# --- CORPO PRINCIPALE ---
st.title("Generatore Guide Turistiche")
st.markdown("### Da zero a local in mezzo minuto.")

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo, New York...")

if st.button("Genera Guida PDF"):
    if not city_name:
        st.warning("Inserisci una città.")
    else:
        with st.spinner("Sto scrivendo e impaginando la guida..."):
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                full_prompt = f"""
                Sei uno scrittore di viaggi esperto. Scrivi una guida DETTAGLIATA per: {city_name}.
                
                REGOLE FONDAMENTALI:
                1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                3. Usa ESATTAMENTE la struttura seguente.
                4. Scrivi paragrafi ricchi e lunghi.
		5. NON USARE MAI CARATTERI SPECIALI
		6. Se viene inserita un parola che non è una città o una frase rispondi in modo scherzoso
                
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
                    mime="application/pdf"
                )
                
# Banner sotto il download
                st.markdown("---")
                st.subheader(f"✈️ Pronto a partire per {city_name}?")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"🏠 **Trova alloggio a {city_name}**")
                    st.link_button(f"Vedi Hotel a {city_name}", get_booking_link(city_name))
                with col2:
                    st.markdown(f"🗺️ **Tour guidati a {city_name}**")
                    st.link_button(f"Attività a {city_name}", get_gyg_link(city_name))
                
            except Exception as e:
                st.error(f"Errore: {e}")






