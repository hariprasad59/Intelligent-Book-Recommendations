import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Audible Insights",
    page_icon="🎧",
    layout="wide"
)

# ---------------------------------
# Complete CSS (Fixes Visibility & Styling)
# ---------------------------------
st.markdown(
    """
    <style>
    /* ---------- GLOBAL TEXT FIX ---------- */
    html, body, [class*="css"]  {
        color: #222 !important;
    }

    /* App background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #111 !important;
    }

    /* Paragraphs & markdown */
    p, span, div, li {
        color: #222 !important;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    div[data-testid="metric-container"] * {
        color: #222 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] * {
        color: #fff !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1f2933;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF9900;
        color: white !important;
        font-weight: bold;
        border: none;
    }

    .stButton>button:hover {
        background-color: #e68a00;
        transform: scale(1.02);
    }

    /* Selectbox & radio FIX */
    div[data-baseweb="select"] * {
        color: #222 !important;
    }

    div[data-baseweb="radio"] * {
        color: #222 !important;
    }

    /* Book cards */
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 6px solid #FF9900;
        color: #222 !important;
    }

    .rating-text {
        color: #FF9900 !important;
        font-weight: 700;
    }

    /* Footer */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #444 !important;
        text-align: center;
        padding: 8px;
        font-size: 14px;
        border-top: 1px solid #ddd;
    }
    </style>

    <div class="footer">
        🎧 Audible Insights Recommendation System — Built by <b>Hari Prasad</b>
    </div>
    """,
    unsafe_allow_html=True
)



# ---------------------------------
# Load Data (Relative Path for Cloud)
# ---------------------------------
@st.cache_data
def load_data():
    file_path = "audible_with_clusters.csv"
    try:
        df = pd.read_csv(file_path)
        
        # Clean Genres
        def extract_genres(text):
            if pd.isna(text): return []
            text = text.lower()
            text = re.sub(r"#\d+.*?(,|$)", "", text)
            parts = text.split(",")
            return [p.strip().title() for p in parts if len(p.strip()) > 3 and "audible" not in p.lower()]
        
        df["Clean_Genres"] = df["Ranks and Genre"].apply(extract_genres)
        return df
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found. Please ensure it is uploaded to GitHub.")
        st.stop()

df = load_data()

# ---------------------------------
# TF-IDF & Logic
# ---------------------------------
@st.cache_resource
def build_tfidf(desc):
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    matrix = tfidf.fit_transform(desc.astype(str))
    sim = cosine_similarity(matrix, matrix)
    return sim

cosine_sim = build_tfidf(df["Description"])

def display_recs(recs):
    cols = st.columns(2)
    for i, (_, row) in enumerate(recs.iterrows()):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="book-card">
                    <h4>📖 {row['Book Name']}</h4>
                    <p style="margin:0;"><b>👤 Author:</b> {row['Author']}</p>
                    <p class="rating-text">⭐ {row['Final_Rating']} / 5.0</p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------
# Sidebar Navigation
# ---------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a5/Audible_logo.png", width=150)
    st.markdown("---")
    st.title("Menu")
    mode = st.radio("Navigation", ["🏠 Home & Stats", "🔍 Recommendations"])

# ---------------------------------
# Main Content
# ---------------------------------
if mode == "🏠 Home & Stats":
    st.title("🎧 Audible Insights Dashboard")
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Books", len(df))
    m2.metric("Avg Rating", round(df["Final_Rating"].mean(), 2))
    m3.metric("Unique Authors", df["Author"].nunique())
    m4.metric("Genres", "50+")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Rating Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df["Final_Rating"], bins=15, kde=True, color="#FF9900")
        st.pyplot(fig)

    with col2:
        st.subheader("🏆 Top Performing Genres")
        genres_series = df["Clean_Genres"].explode().value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=genres_series.values, y=genres_series.index, palette="Oranges_r")
        st.pyplot(fig)

else:
    st.title("🔍 Recommendation Engine")
    rec_type = st.selectbox("Choose Strategy", ["Genre-Based", "Content-Based (Similar Books)", "Cluster-Based"])
    
    if rec_type == "Genre-Based":
        genre_list = sorted(list(set(df["Clean_Genres"].explode().dropna())))
        selected_genre = st.selectbox("Select Genre", genre_list)
        if st.button("Recommend"):
            filtered = df[df["Clean_Genres"].apply(lambda x: selected_genre in x)]
            recs = filtered.sort_values(["Final_Rating", "Final_Reviews"], ascending=False).head(6)
            display_recs(recs)

    elif rec_type == "Content-Based (Similar Books)":
        book_input = st.selectbox("Select a book", df["Book Name"].unique())
        if st.button("Find Similar"):
            idx = df[df["Book Name"] == book_input].index[0]
            sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:7]
            display_recs(df.iloc[[i[0] for i in sim_scores]])

    else:
        book_input = st.selectbox("Select a book", df["Book Name"].unique())
        if st.button("Find in Cluster"):
            cluster_id = df[df["Book Name"] == book_input]["Cluster"].values[0]
            recs = df[df["Cluster"] == cluster_id].sort_values("Final_Rating", ascending=False).head(6)
            display_recs(recs)


