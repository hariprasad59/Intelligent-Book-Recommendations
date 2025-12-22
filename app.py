st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Headings */
    h1, h2, h3, h4, h5 {
        color: #222;
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
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #e68a00;
        transform: scale(1.02);
    }

    /* Book card */
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 6px solid #FF9900;
        color: #222;
    }

    .rating-text {
        color: #FF9900;
        font-size: 1.1rem;
        font-weight: 700;
    }

    /* FIX: dropdowns & radio text */
    div[data-baseweb="select"] * {
        color: white !important;
    }

    div[data-baseweb="radio"] * {
        color: white !important;
    }

    /* Labels */
    label {
        color: #222 !important;
        font-weight: 600;
    }

    /* Footer */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
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
