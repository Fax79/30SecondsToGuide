import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Privacy Policy - 30SecondsToGuide",
    page_icon="🔒",
    layout="centered"
)

# --- TITOLO ---
st.title("🔒 Privacy Policy & Cookie")
st.markdown("---")

# --- TESTO LEGALE ---
st.markdown("""
### 1. Chi siamo
Il titolare del trattamento dati è il gestore di **30SecondsToGuide**.

### 2. Quali dati raccogliamo
Questo sito utilizza **Streamlit Community Cloud** e le API di **Google Gemini**.
* **Dati inseriti dall'utente:** Il nome della città inserita viene inviato a Google Gemini esclusivamente per generare la guida PDF. Non viene salvato né storicizzato sui nostri server.
* **Cookie:** Utilizziamo solo cookie tecnici essenziali per il funzionamento della sessione. Non utilizziamo cookie di profilazione o tracciamento pubblicitario proprietari.

### 3. Servizi Terzi
Il sito contiene link di affiliazione a terze parti (es. Booking.com, GetYourGuide). Cliccando su tali link, l'utente viene reindirizzato su piattaforme esterne che potrebbero installare i propri cookie, per i quali 30SecondsToGuide non è responsabile.

### 4. Diritti dell'utente
In conformità con il GDPR, hai il diritto di chiedere informazioni sui dati trattati (che in questo caso sono nulli, poiché non salviamo nulla).

*Ultimo aggiornamento: Novembre 2025*
""")

# --- BOTTONE PER TORNARE INDIETRO ---
if st.button("⬅️ Torna alla Home"):
    st.switch_page("app.py")
