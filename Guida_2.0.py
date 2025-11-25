import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
import base64

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

# 3. LINK GENERICI (In attesa)
INSURANCE_LINK = "https://www.heymondo.it"
TRAIN_LINK = "https://www.omio.com"             
RENTAL_LINK = "https://www.discovercars.com"   

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
        exceptException:
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
            
            self.set_y(250)
            self.set_x(70)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, "GENERATO DA 30SecondsToGuide")

    # --- FUNZIONE SPAZZINO ---
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

    # --- PAGINA SPONSOR (PDF) ---
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "LINK UTILI PER IL VIAGGIO", 0, 1, 'C')
    pdf.ln(5)
    
    def make_sponsor_box(title, subtitle, link):
        title = clean_text_for_pdf(title)
        subtitle = clean_text_for_pdf(subtitle)
        
        pdf.set_fill_color(245, 245, 245)
        start_y = pdf.get_y()
        pdf.rect(10, start_y, 190, 20, 'F') 
        
        pdf.set_y(start_y + 3)
        pdf.set_x(15)
        pdf.set_font("Helvetica", 'B', 11)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 5, title, 0, 1)
        
        pdf.set_x(15)
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(0, 102, 204)
        
        pdf.cell(0, 6, subtitle, 0, 1, link=link)
        pdf.ln(8)

    make_sponsor_box("Voli Low Cost", f"Cerca i voli più economici per {city} su Kiwi.com", FLIGHT_LINK)
    make_sponsor_box("Dove Dormire", f"Trova le migliori offerte hotel a {city} su Booking.com", get_booking_link(city))
    make_sponsor_box("Cosa Fare", f"Salta la fila: Biglietti e Tour a {city}", get_gyg_link(city))
    make_sponsor_box("Internet (eSim)", f"Naviga a {city} senza roaming con Saily", ESIM_LINK)
    make_sponsor_box("Assicurazione Viaggio", "Parti senza pensieri con la protezione di Heymondo", INSURANCE_LINK)
    make_sponsor_box("Deposito bagagli", "Quando il bagaglio diventa un peso, depositalo in sicurezza", LUGGAGE_LINK)
    make_sponsor_box("Rimborso voli", "Volo cancellato o in ritardo? Ottieni fino a 600 EUR!", REIMB_LINK)
    make_sponsor_box("Treni e Bus", f"Spostati facilmente da/per {city} con Omio", TRAIN_LINK)
    make_sponsor_box("Noleggio Auto", f"Noleggia un'auto a {city} al miglior prezzo", RENTAL_LINK)

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
    st.caption("✈️ PRENOTAZIONI")
    partner_button("Voli (Kiwi)", FLIGHT_LINK, "btn_kiwi.png")
    partner_button("Hotel (Booking)", get_booking_link(""), "btn_booking.png")
    partner_button("Treni (Omio)", TRAIN_LINK, "btn_omio.png")
    partner_button("Auto (Discover)", RENTAL_LINK, "btn_discover.png")
    
    st.caption("🎟️ ESPERIENZE")
    partner_button("Tour (GetYourGuide)", get_gyg_link(""), "btn_gyg.png")
    
    st.caption("🛠️ SERVIZI UTILI")
    partner_button("eSim (Saily)", ESIM_LINK, "btn_saily.png")
    partner_button("Bagagli", LUGGAGE_LINK, "btn_radical.png")
    partner_button("Polizza (Heymondo)", INSURANCE_LINK, "btn_heymondo.png")
    partner_button("Rimborsi (Airhelp)", REIMB_LINK, "btn_airhelp.png")
    
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

city_name = st.text_input("Inserisci la destinazione:", placeholder="Es. Parigi, Tokyo, New York...")

# --- GENERAZIONE GUIDA ---
if st.button("Genera Guida PDF", type="primary", use_container_width=True):
    if not city_name:
        st.warning("Inserisci una città.")
    else:
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
                5. NON USARE MAI CARATTERI SPECIALI, simboli delle valute (come € o $), semplifica la grafia delle parole straniere utilizzando l'alfabeto standard, ammesse SOLO lettere accentate comunemente usate in italiano.
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
                
                # --- GRIGLIA FINALE (Hub di Viaggio) ---
                st.markdown("---")
                st.subheader(f"✈️ Organizza il viaggio a {city_name}")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.caption("✈️ **Voli**")
                    partner_button("Voli Kiwi", FLIGHT_LINK, "btn_kiwi.png")
                with c2:
                    st.caption("🏨 **Hotel**")
                    partner_button("Booking", get_booking_link(city_name), "btn_booking.png")
                with c3:
                    st.caption("🚆 **Treni**")
                    partner_button("Omio", TRAIN_LINK, "btn_omio.png")

                st.write("") 

                c4, c5, c6 = st.columns(3)
                with c4:
                    st.caption("🎟️ **Tour**")
                    partner_button("Attività", get_gyg_link(city_name), "btn_gyg.png")
                with c5:
                    st.caption("🚗 **Auto**")
                    partner_button("Noleggio", RENTAL_LINK, "btn_discover.png")
                with c6:
                    st.caption("🎒 **Bagagli**")
                    partner_button("Deposito", LUGGAGE_LINK, "btn_radical.png")

                st.write("") 

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
                
            except Exception as e:
                st.error(f"Errore: {e}")

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
        Che tu stia cercando <em>cosa vedere a Parigi</em>, un <em>itinerario di 3 giorni a New York</em> o 
        consigli su <em>dove dormire a Tokyo</em>, la nostra AI analizza migliaia di fonti per offrirti:
    </p>
    <ul>
        <li>🗺️ <strong>Itinerari passo-passo</strong> ottimizzati per risparmiare tempo.</li>
        <li>🍽️ Consigli gastronomici sui <strong>migliori ristoranti locali</strong>.</li>
        <li>🏛️ Informazioni storiche e culturali dettagliate.</li>
        <li>📲 Link utili per <strong>prenotare hotel, voli e tour</strong> al miglior prezzo.</li>
    </ul>
    <p>
        Il servizio è <strong>gratuito al 100%</strong> e non richiede registrazione. 
        Inserisci la destinazione, clicca e scarica la tua guida di viaggio in PDF pronta per essere stampata o letta su smartphone.
    </p>
</div>
""", unsafe_allow_html=True)
