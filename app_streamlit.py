import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# CONFIGURATION GÉNÉRALE
# =========================================
st.set_page_config(
    page_title="🎬 Dashboard Allociné - Pipeline Automatisé",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Tableau de Bord Allociné")
st.markdown("""
Ce tableau de bord affiche les **données extraites automatiquement**
via ton pipeline GitHub Actions (scraping + nettoyage + enrichissement).  
Les données proviennent du fichier `films_clean.csv` généré par le pipeline.
""")

# =========================================
# CHARGEMENT DU CSV
# =========================================
CSV_URL = "https://raw.githubusercontent.com/hadil123-web/pipeline_films/main/scripts/data/films_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Erreur de chargement du CSV : {e}")
    st.stop()

# =========================================
# FILTRES
# =========================================
col1, col2 = st.columns(2)

films = sorted(df["film_title"].dropna().unique())
selected_film = col1.selectbox("🎬 Choisir un film :", films)

sentiments = ["Tous"] + sorted(df["sentiment"].dropna().unique())
selected_sentiment = col2.selectbox("💭 Filtrer par sentiment :", sentiments)

# Filtrage dynamique
df_filtered = df[df["film_title"] == selected_film]
if selected_sentiment != "Tous":
    df_filtered = df_filtered[df_filtered["sentiment"] == selected_sentiment]

# =========================================
# INDICATEURS CLÉS
# =========================================
st.subheader(f"🎞️ Analyse du film : {selected_film}")

col3, col4, col5 = st.columns(3)
col3.metric("Nombre d'avis", len(df_filtered))
col4.metric("Note moyenne", f"{df_filtered['user_note'].mean():.2f}" if len(df_filtered) else "0")
col5.metric("Avis positifs (%)",
            f"{(df_filtered['sentiment'].eq('Positif').mean() * 100):.1f}%" if len(df_filtered) else "0%")

# =========================================
# VISUALISATIONS
# =========================================
st.subheader("📊 Visualisations")

col6, col7 = st.columns(2)

# Histogramme des notes
with col6:
    fig1 = px.histogram(df_filtered, x="user_note", nbins=5, title="Répartition des notes")
    st.plotly_chart(fig1, use_container_width=True)

# Répartition des sentiments
with col7:
    fig2 = px.pie(df_filtered, names="sentiment", title="Répartition des sentiments", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# =========================================
# TABLEAU DÉTAILLÉ DES AVIS
# =========================================
st.subheader("💬 Avis des spectateurs")
st.dataframe(df_filtered[["user_note", "sentiment", "clean_review"]].head(15))

st.success("✅ Dashboard généré à partir du pipeline CI/CD")
