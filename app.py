import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------
# Page Config & Custom Styling
# ---------------------------------
st.set_page_config(
    page_title="Audible Insights",
    page_icon="🎧",
    layout="wide"
)

# Custom CSS for a modern look
st.markdown("""
    <style>
    /* Main background color */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Style the buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF9900;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #e68a00;
        border: none;
        color: white;
        transform: scale(1.02);
    }

    /* Modern Card UI for books */
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #FF9900;
    }
    
    .rating-text {
        color: #FF9900;
        font-size: 1.1rem;
        font-weight: 700;
    }
    </style>
    """
             """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f9f9f9;
        color: #555;
        text-align: center;
        padding: 8px;
        font-size: 14px;
        border-top: 1px solid #e0e0e0;
    }
    </style>

    <div class="footer">
        🔊 Built by <b>Hari Prasad</b>
    </div>
    """, unsafe_allow_html=True) # <-- Fixed the keyword here

# ---------------------------------
# Load Data (Cached)
# ---------------------------------
@st.cache_data
def load_data():
    # Replace with your actual path
    df = pd.read_csv("audible_with_clusters.csv")
    
    # Pre-cleaning for display
    def extract_genres(text):
        if pd.isna(text): return []
        text = text.lower()
        text = re.sub(r"#\d+.*?(,|$)", "", text)
        parts = text.split(",")
        return [p.strip().title() for p in parts if len(p.strip()) > 3 and "audible" not in p.lower()]
    
    df["Clean_Genres"] = df["Ranks and Genre"].apply(extract_genres)
    return df

df = load_data()

# ---------------------------------
# TF-IDF Logic
# ---------------------------------
@st.cache_resource
def build_tfidf(desc):
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    matrix = tfidf.fit_transform(desc.astype(str))
    sim = cosine_similarity(matrix, matrix)
    return sim

cosine_sim = build_tfidf(df["Description"])

# ---------------------------------
# Helper UI Function
# ---------------------------------
def display_recommendations(recs):
    if recs.empty:
        st.info("No books found matching your criteria.")
        return
    
    # Create columns for a grid layout
    for _, row in recs.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="book-card">
                    <h4>📖 {row['Book Name']}</h4>
                    <p style="margin:0;"><b>👤 Author:</b> {row['Author']}</p>
                    <p class="rating-text">⭐ {row['Final_Rating']} / 5.0</p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------
# Sidebar & Header
# ---------------------------------
with st.sidebar:
    st.title("Menu")
    mode = st.radio(
        "Navigation",
        ["🏠 Home & Stats", "🔍 Recommendations"]
    )
    
    if mode == "🔍 Recommendations":
        st.divider()
        rec_type = st.selectbox(
            "Strategy",
            ["Genre-Based", "Similar to a Book", "Clustered Discovery"]
        )

# ---------------------------------
# Home Page / EDA
# ---------------------------------
if mode == "🏠 Home & Stats":
    st.title("🎧 Audible Insights Dashboard")
    
    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Books", len(df))
    m2.metric("Avg Rating", round(df["Final_Rating"].mean(), 2))
    m3.metric("Unique Authors", df["Author"].nunique())
    m4.metric("Genres", "50+")

    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Rating Distribution")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df["Final_Rating"], bins=15, kde=True, color="#FF9900")
        ax.set_frame_on(False)
        st.pyplot(fig)

    with col2:
        st.subheader("🏆 Top Performing Genres")
        genres_series = df["Clean_Genres"].explode().value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=genres_series.values, y=genres_series.index, palette="Oranges_r")
        st.pyplot(fig)

# ---------------------------------
# Recommendation Engine UI
# ---------------------------------
else:
    st.title("🔍 Find Your Next Listen")
    
    if rec_type == "Genre-Based":
        genre_list = sorted(list(set(df["Clean_Genres"].explode().dropna())))
        selected_genre = st.selectbox("Pick a Category", genre_list)
        
        if st.button("Generate Recommendations"):
            filtered = df[df["Clean_Genres"].apply(lambda x: selected_genre in x)]
            recs = filtered.sort_values(["Final_Rating", "Final_Reviews"], ascending=False).head(5)
            display_recommendations(recs)

    elif rec_type == "Similar to a Book":
        book_input = st.selectbox("Select a book you liked", df["Book Name"].unique())
        
        if st.button("Find Similar Matches"):
            idx = df[df["Book Name"] == book_input].index[0]
            sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:6]
            indices = [i[0] for i in sim_scores]
            display_recommendations(df.iloc[indices])

    else:
        book_input = st.selectbox("Select a book to find its 'Vibe' cluster", df["Book Name"].unique())
        
        if st.button("Explore Cluster"):
            cluster_id = df[df["Book Name"] == book_input]["Cluster"].values[0]
            recs = df[df["Cluster"] == cluster_id].sort_values("Final_Rating", ascending=False).head(5)
            display_recommendations(recs)


st.markdown("<br><hr><center>Built with ❤️ for Book Lovers</center>", unsafe_allow_html=True)
