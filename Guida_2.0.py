import streamlit as st
import google.generativeai as genai
import markdown
from xhtml2pdf import pisa
from io import BytesIO

# --- CONFIGURAZIONE ---
# INSERISCI QUI LA TUA CHIAVE API
API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=API_KEY)

# --- FUNZIONE PDF (Invariata) ---
def create_pdf(markdown_text):
    html_text = markdown.markdown(markdown_text, extensions=['tables'])
    
    # CSS Migliorato per gestire testi lunghi e impaginazione
    styled_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Helvetica, sans-serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; }}
            h1 {{ color: #8e44ad; font-size: 26pt; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 3px solid #8e44ad; }}
            h2 {{ color: #2980b9; font-size: 18pt; margin-top: 25px; margin-bottom: 15px; border-left: 5px solid #2980b9; padding-left: 10px; }}
            h3 {{ color: #c0392b; font-size: 14pt; margin-top: 20px; font-weight: bold; }}
            p {{ margin-bottom: 15px; text-align: justify; }}
            li {{ margin-bottom: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 10px; font-weight: bold; color: #2c3e50; }}
            td {{ border: 1px solid #bdc3c7; padding: 10px; vertical-align: top; }}
            strong {{ color: #2c3e50; font-weight: bold; }}
        </style>
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """
    
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=pdf_buffer)
    if pisa_status.err: return None
    return pdf_buffer.getvalue()

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

# --- INTERFACCIA SITO ---
st.set_page_config(
    page_title="30SecondsToGuide", 
    page_icon="⏱️",
    layout="centered"
)

# Header con il nuovo Brand
st.title("⏱️ 30SecondsToGuide")
st.markdown("### *From zero to local expert in half a minute.*")
st.caption("Inserisci la tua destinazione e ottieni una guida PDF professionale istantanea.")

# Modello (qui ho lasciato quello veloce per restare nei 30 secondi, 
# ma se usi il prompt "Cattivo/Lungo" l'utente aspetterà volentieri qualche secondo in più!)
model_name = "gemini-2.5-pro" 

city_name = st.text_input("Di quale città vuoi la guida?", placeholder="Es. Tokyo, New York, Roma...")

if st.button("Start 30s Timer & Generate"):

    if not city_name:
        st.warning("Inserisci una città.")
    else:
        with st.spinner(f"Sto scrivendo una guida DETTAGLIATA per {city_name}. Richiederà circa 20-30 secondi..."):
            try:
                model = genai.GenerativeModel(model_name)
                
                # --- PROMPT "TURBO" PER FORZARE LA LUNGHEZZA ---
                full_prompt = f"""
                Sei uno scrittore di viaggi professionista per riviste come National Geographic o Lonely Planet.
                Devi scrivere una guida turistica MOLTO DETTAGLIATA per: {city_name}.

                REGOLE FONDAMENTALI:
                1. NON essere sintetico. Voglio descrizioni lunghe, ricche di aggettivi e dettagli storici.
                2. Segui RIGOROSAMENTE la struttura del modello sottostante.
                3. Non fare elenchi puntati brevi. Usa frasi complete e discorsive.
                4. Nella sezione cibo, descrivi i sapori, non fare solo la lista.
                5. L'output deve essere lungo e approfondito.

                MODELLO DA RIEMPIRE:
                {TESTO_MODELLO}
                """
                
                response = model.generate_content(full_prompt)
                markdown_content = response.text
                
                # Anteprima
                with st.expander("Vedi anteprima testo"):
                    st.markdown(markdown_content)
                
                # PDF
                pdf_bytes = create_pdf(markdown_content)
                
                if pdf_bytes:
                    st.success("✅ Guida generata con successo!")
                    st.download_button(
                        label="📄 SCARICA GUIDA PDF COMPLETA",
                        data=pdf_bytes,
                        file_name=f"Guida_{city_name}_Full.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Errore PDF.")
                
            except Exception as e:
                st.error(f"Errore: {e}")