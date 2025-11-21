import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIGURAZIONE ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets'.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- IL MODELLO "MAXI" ---
TESTO_MODELLO = """
# [NOME CITTÀ]: Guida Esclusiva

## 1. L'Anima della Città
[Intro evocativa di 150 parole].

## 2. Quartieri e Atmosfere
[Descrizione zone].

### Confronto Zone (Stile Scheda)
* **Centro Storico:** [Descrizione atmosfera]
* **Città Moderna:** [Descrizione atmosfera]
* **Chi ci va:** [Target turisti]

## 3. Gastronomia
[Intro cibo].

### Piatti Imperdibili
* **[Piatto 1]:** [Descrizione e ingredienti]
* **[Piatto 2]:** [Descrizione e ingredienti]

## 4. Attrazioni
* **[Monumento 1]:** [Descrizione]
* **[Monumento 2]:** [Descrizione]

## 5. Info Pratiche
* **Trasporti:** [Info]
* **Sicurezza:** [Info]

## 6. Itinerario 3 Giorni
* **Giorno 1:** [Mattina/Pomeriggio/Sera]
* **Giorno 2:** [Mattina/Pomeriggio/Sera]
* **Giorno 3:** [Mattina/Pomeriggio/Sera]
"""

# --- FUNZIONE PDF "DESIGNER" (Con elenchi fixati) ---
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
            self.set_fill_color(236, 240, 241) 
            self.rect(0, 0, 60, 297, 'F') 
            
            self.set_y(80)
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
        # Pulizia encoding
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        
        if line.startswith('# '): # H1
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 22)
            pdf.set_text_color(44, 62, 80)
            content = clean_line.replace('# ', '').upper().strip()
            pdf.multi_cell(0, 10, content)
            y = pdf.get_y()
            pdf.set_draw_color(230, 126, 34)
            pdf.set_line_width(1)
            pdf.line(10, y+2, 50, y+2) 
            pdf.ln(8)
            
        elif line.startswith('## '): # H2
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 16)
            pdf.set_text_color(230, 126, 34)
            content = clean_line.replace('## ', '').strip()
            pdf.cell(0, 10, content, ln=True)
            pdf.ln(2)
            
        elif line.startswith('### '): # H3
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.set_text_color(52, 73, 94)
            content = clean_line.replace('### ', '').strip()
            pdf.cell(0, 10, content, ln=True)
            
        elif line.startswith('* '): # ELENCHI (FIX AVANZATO)
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(0, 0, 0)
            
            content = clean_line.replace('* ', '').replace('**', '')
            
            # Salva la posizione Y corrente
            current_y = pdf.get_y()
            
            # Disegna il pallino a sinistra
            pdf.set_x(15) 
            pdf.cell(5, 5, chr(149), 0, 0) # Pallino (bullet point)
            
            # Sposta il cursore per il testo e stampa il blocco allineato
            pdf.set_x(22) 
            pdf.multi_cell(0, 6, content)
            
            # Piccolo spazio dopo ogni punto elenco
            pdf.ln(1)
            
        else: # Testo normale
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40)
                content = clean_line.replace('**', '')
                pdf.multi_cell(0, 6, content)
                pdf.ln(2)

    return bytes(pdf.output(dest='S'))

# --- INTERFACCIA ---
st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️")

st.title("⏱️ 30SecondsToGuide")
st.markdown("### Crea la tua guida di viaggio professionale.")

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo, New York...")

if st.button("Genera Guida PDF"):
    if not city_name:
        st.warning("Inserisci una città.")
    else:
        with st.spinner("Sto scrivendo e impaginando la guida..."):
            try:
                model = genai.GenerativeModel("gemini-2.5-pro")
                
                # Prompt modificato per EVITARE TABELLE
                full_prompt = f"""
                Sei uno scrittore di viaggi esperto. Scrivi una guida DETTAGLIATA per: {city_name}.
                
                REGOLE FONDAMENTALI:
                1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
                2. Se devi fare un confronto, usa elenchi puntati descrittivi.
                3. Usa ESATTAMENTE la struttura seguente.
                4. Scrivi paragrafi ricchi e lunghi.
                
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
                
            except Exception as e:
                st.error(f"Errore: {e}")
