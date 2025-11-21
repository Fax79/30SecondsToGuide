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
def create_pdf(text):
    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 16)
            self.cell(0, 10, 'Guida Turistica - 30SecondsToGuide', 0, 1, 'C')
            self.ln(5)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # FPDF2 gestisce il testo in modo semplice. 
    # Nota: Rimuove alcuni caratteri speciali non supportati dal font base
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, safe_text)
    
    # Ritorna i byte del PDF
    return pdf.output(dest='S').encode('latin-1')

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
                pdf_bytes = create_pdf(markdown_content)
                
                st.success("✅ Guida completata!")
                st.download_button(
                    label="📄 SCARICA PDF",
                    data=pdf_bytes,
                    file_name=f"Guida_{city_name}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Errore: {e}")
