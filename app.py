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
st.markdown("""
    <style>
    /* 1. GLOBAL PAGE STYLING */
    .stApp {
        background-color: #f8f9fa !important;
    }

    /* 2. FORCE TEXT VISIBILITY */
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #1a1a1a !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 3. DASHBOARD METRICS */
    [data-testid="stMetricValue"] {
        color: #FF9900 !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #4b4b4b !important;
    }

    /* 4. SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }

    /* 5. CUSTOM RECOMMENDATION CARDS */
    .book-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 8px solid #FF9900;
        transition: transform 0.2s ease;
    }
    
    .book-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }

    .rating-text {
        color: #FF9900 !important;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* 6. BUTTON STYLING */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #FF9900 !important;
        color: white !important;
        font-weight: bold;
        border: none !important;
        height: 3em;
    }
    
    .stButton>button:hover {
        background-color: #e68a00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# ---------------------------------
# Footer
# ---------------------------------
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p style="color: #666 !important;">📌 <b>Audible Insights Recommendation System</b></p>
        <p style="color: #FF9900 !important; font-weight: bold;">Built by Hari Prasad</p>
    </div>
""", unsafe_allow_html=True)
