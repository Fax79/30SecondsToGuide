import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIGURAZIONE ---
# Recupera la chiave dai segreti di Streamlit
# Se non trova la chiave nei segreti, non crasha ma avvisa l'utente
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Chiave API mancante! Inseriscila nei 'Secrets' della dashboard di Streamlit.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- FUNZIONE PDF (Versione "Bulletproof" con FPDF2) ---
def create_pdf(text, city):
    class ModernPDF(FPDF):
        def header(self):
            # Se siamo a pagina 1 (Copertina), non mettere l'intestazione
            if self.page_no() == 1:
                return
            
            # Barra colorata in alto (Blu Notte)
            self.set_fill_color(44, 62, 80) 
            self.rect(0, 0, 210, 20, 'F')
            
            # Testo Header bianco
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(255, 255, 255)
            self.set_y(8)
            self.cell(0, 0, f'GUIDA ESCLUSIVA: {city.upper()}', 0, 0, 'R')
            self.ln(20) 
            
        def footer(self):
            # Riga grigia in basso
            self.set_draw_color(200, 200, 200)
            self.line(10, 285, 200, 285)
            
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'30SecondsToGuide - {city} - Pagina {self.page_no()}', 0, 0, 'C')

        def make_cover(self, city_name):
            self.add_page()
            
            # Colonna decorativa laterale (Grigio chiaro)
            self.set_fill_color(236, 240, 241) 
            self.rect(0, 0, 60, 297, 'F') 
            
            self.set_y(80)
            self.set_x(70) # Sposta il cursore a destra della colonna
            
            # Titolo Città Gigante
            self.set_font('Helvetica', 'B', 40)
            self.set_text_color(44, 62, 80) # Blu Scuro
            self.multi_cell(0, 20, city_name.upper())
            
            self.ln(10)
            self.set_x(70)
            
            # Sottotitolo
            self.set_font('Helvetica', '', 16)
            self.set_text_color(127, 140, 141) # Grigio
            self.multi_cell(0, 10, "Guida turistica completa\nItinerari, Storia e Cultura")
            
            # Linea decorativa arancione
            self.ln(20)
            self.set_fill_color(230, 126, 34) 
            self.rect(70, self.get_y(), 100, 2, 'F')
            
            # Firma in basso
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, "GENERATO DA 30SecondsToGuide")

    pdf = ModernPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # 1. Crea la Copertina
    pdf.make_cover(city)
    
    # 2. Aggiungi pagina per il testo
    pdf.add_page()
    
    lines = text.split('\n')
    
    for line in lines:
        # Pulizia caratteri speciali (per evitare crash su server Linux)
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        
        if line.startswith('# '): # H1 - Titolo Capitolo
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 22)
            pdf.set_text_color(44, 62, 80) # Blu Scuro
            content = clean_line.replace('# ', '').upper().strip()
            pdf.multi_cell(0, 10, content)
            
            # Linea arancione sotto il titolo
            y = pdf.get_y()
            pdf.set_draw_color(230, 126, 34)
            pdf.set_line_width(1)
            pdf.line(10, y+2, 50, y+2) 
            pdf.ln(10)
            
        elif line.startswith('## '): # H2 - Sottotitolo
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 16)
            pdf.set_text_color(230, 126, 34) # Arancione
            content = clean_line.replace('## ', '').strip()
            pdf.cell(0, 10, content, ln=True)
            pdf.ln(2)
            
        elif line.startswith('### '): # H3 - Paragrafo
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.set_text_color(52, 73, 94) 
            content = clean_line.replace('### ', '').strip()
            pdf.cell(0, 10, content, ln=True)
            
        elif line.startswith('* '): # Elenchi puntati
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(0, 0, 0)
            # Trasforma asterisco in freccetta
            content = clean_line.replace('* ', '   > ').replace('**', '')
            pdf.multi_cell(0, 6, content)
            pdf.ln(1)
            
        else: # Testo normale
            if line.strip():
                pdf.set_font("Helvetica", '', 11)
                pdf.set_text_color(40, 40, 40) # Grigio scuro elegante
                content = clean_line.replace('**', '') # Via i grassetti markdown
                pdf.multi_cell(0, 6, content)
                pdf.ln(2)

    return bytes(pdf.output(dest='S'))

# --- IL MODELLO "MAXI" (Basato sulla struttura profonda di Astana) ---
TESTO_MODELLO = """
# [NOME CITTÀ]: Guida Completa ed Esclusiva

## 1. Introduzione: L'Anima della Città
[Scrivi un paragrafo introduttivo lungo (almeno 150 parole). Non limitarti a dire dove si trova. Descrivi i contrasti, i profumi, la luce e l'impatto emotivo che la città ha sul viaggiatore. Parla della sua evoluzione storica recente come fatto per Astana].

## 2. Geografia e Quartieri: Orientarsi
[Spiega la geografia della città. Se c'è un fiume, usalo come divisore. Descrivi la differenza tra la parte storica e quella moderna/finanziaria].

### Il Cuore Storico (o Zona A)
[Descrizione dettagliata di almeno 100 parole. Parla dell'architettura antica, dei vicoli, dell'atmosfera "vissuta" e organica].

### La Città Moderna (o Zona B)
[Descrizione dettagliata di almeno 100 parole. Parla dei grattacieli, dello shopping, del lusso, dell'architettura futuristica o dei grandi viali].

### Confronto Diretto
| Caratteristica | Zona Storica/Popolare | Zona Moderna/Lusso |
| :--- | :--- | :--- |
| **Atmosfera** | [Aggettivi evocativi] | [Aggettivi evocativi] |
| **Architettura** | [Stile e materiali] | [Stile e materiali] |
| **Chi ci va** | [Tipologia viaggiatore] | [Tipologia viaggiatore] |

## 3. Il Palato Locale: Un Viaggio Gastronomico
[Introduzione alla filosofia culinaria locale. Su quali ingredienti si basa? È cucina di terra o di mare?].

### Piatti Iconici (Non solo un elenco, descrivi la storia)
* **[Piatto 1]:** [Descrizione ricca. Ingredienti, come si mangia, origine storica].
* **[Piatto 2]:** [Descrizione ricca].
* **[Street Food]:** [Descrizione dello snack tipico da mangiare per strada].

### Bevande e Rituali
[Cosa si beve? Vino, tè, caffè o alcolici locali? Descrivi il rito sociale del bere qui].

## 4. Dove Mangiare: Dallo Street Food al Lusso
* **Per l'Autenticità (Tradizione):** [Consiglia il tipo di trattoria/locale dove vanno i locali. Descrivi l'ambiente rustico].
* **Per l'Esperienza (Lusso/Vista):** [Descrivi l'esperienza di cenare nei quartieri alti o con vista].
* **I Mercati:** [Descrivi il mercato principale della città: i rumori, gli odori, cosa comprare. Deve sembrare di essere lì].

## 5. Cultura e Attrazioni Imperdibili
[Non fare solo un elenco. Scegli 3 luoghi simbolo e dedicani un paragrafo intero a ciascuno].

### Icone della Città
* **[Monumento/Museo 1]:** [Descrizione approfondita architettonica e storica].
* **[Monumento/Museo 2]:** [Descrizione approfondita].
* **[Luogo di Culto/Parco]:** [Descrizione dell'atmosfera].

### Calendario Eventi
| Stagione | Eventi Clou | Cosa aspettarsi |
| :--- | :--- | :--- |
| **Primavera/Estate** | [Nome Evento] | [Descrizione attività] |
| **Autunno/Inverno** | [Nome Evento] | [Descrizione atmosfera] |

## 6. Guida Pratica per il Viaggiatore
* **Documenti:** [Visti necessari per Italiani].
* **Valuta e Pagamenti:** [Contanti vs Carta. Si usa la mancia?].
* **Sicurezza:** [Zone da evitare e livello di sicurezza generale].
* **Come Muoversi:** [Miglior mezzo (Metro, Taxi, Piedi). Costi medi].
* **Dove Alloggiare:** [Consiglio zona per famiglie vs zona per giovani/movida].

## 7. Itinerari Consigliati

### 3 Giorni: "L'Essenziale"
* **Giorno 1 (L'Arrivo):** [Mattina: X. Pomeriggio: Y. Sera: Cena a Z].
* **Giorno 2 (La Cultura):** [Attività dettagliate].
* **Giorno 3 (Il Relax):** [Attività dettagliate].

### 5 Giorni: "Deep Dive"
* **Giorni 1-3:** Come sopra.
* **Giorno 4 (Fuori dai sentieri battuti):** [Un quartiere meno turistico].
* **Giorno 5 (Gita fuori porta):** [Una gita di un giorno nei dintorni].

## 8. Conclusione
[Riflessione finale filosofica sul viaggio in questa città].
"""

# --- INTERFACCIA ---
st.set_page_config(page_title="30SecondsToGuide", page_icon="⏱️")

st.title("⏱️ 30SecondsToGuide")
st.markdown("### *Da zero a local in mezzo minuto.*")

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Tokyo, Roma, Parigi...")

if st.button("Genera Guida"):
    if not city_name:
        st.warning("Inserisci una città.")
    else:
        with st.spinner("Scrivo la guida... (richiede circa 30 secondi)"):
            try:
                model = genai.GenerativeModel("gemini-2.5-pro")
                
                full_prompt = f"""
                Sei una guida turistica. Scrivi una guida per: {city_name}.
                Usa questa struttura. NON usare tabelle complesse o grassetti eccessivi, usa elenchi semplici.
                
                {TESTO_MODELLO}
                """
                
                response = model.generate_content(full_prompt)
                markdown_content = response.text
                
                # Mostra a video
                st.markdown("---")
                st.markdown(markdown_content)
                
                # Crea PDF
                pdf_bytes = create_pdf(markdown_content, city_name)
                
                st.success("✅ Guida completata!")
                st.download_button(
                    label="📄 SCARICA PDF",
                    data=pdf_bytes,
                    file_name=f"Guida_{city_name}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Errore: {e}")



