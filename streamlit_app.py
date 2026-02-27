import streamlit as st
import os
from dotenv import load_dotenv
from typing import List, Optional

# Import local modules
from phase_2.models import UserPreferences, Restaurant
from phase_2.retrieval import get_recommendations, load_prepared_dataframe
from phase_3.llm_recommender import get_llm_recommendations, LLMRestaurantRecommendation
from phase_3.client import GroqClientError

# Load environment variables
load_dotenv()

# Secure API Key retrieval (Local .env or Streamlit Secrets)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = None

# Page configuration
st.set_page_config(
    page_title="Zomato AI - Find Your Next Meal",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Design
st.markdown("""
    <style>
    /* Main Theme Colors */
    :root {
        --zomato-red: #E23744;
        --zomato-dark: #1C1C1C;
        --card-bg: #FFFFFF;
        --text-main: #2D2D2D;
        --text-sub: #696969;
    }

    /* Header Styling */
    .main-header {
        font-family: 'Outfit', sans-serif;
        color: var(--zomato-red);
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        color: var(--text-sub);
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .restaurant-card {
        background-color: var(--card-bg);
        border: 1px solid #E8E8E8;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out;
    }
    
    .restaurant-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    .res-name {
        color: var(--zomato-dark);
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }

    .rating-badge {
        background-color: #24963F;
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.9rem;
    }

    .cuisine-pill {
        background-color: #F8F8F8;
        color: var(--text-sub);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
        margin-top: 8px;
        display: inline-block;
        border: 1px solid #EDEDED;
    }

    .ai-reason {
        background-color: #FFF5F6;
        border-left: 4px solid var(--zomato-red);
        padding: 12px 16px;
        margin-top: 15px;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #4A4A4A;
        font-size: 0.95rem;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FBFBFB;
        border-right: 1px solid #EEEEEE;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--zomato-red);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #C12E38;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data
def get_metadata():
    # Ensure data exists before trying to load it
    from phase_1.data_ingestion import load_zomato_dataset, save_raw_dataset
    from phase_2.retrieval import RAW_DATA_PATH
    
    if not RAW_DATA_PATH.exists():
        with st.spinner("📥 Downloading Zomato dataset (this may take a minute)..."):
            df = load_zomato_dataset()
            save_raw_dataset(df)
            st.success("✅ Dataset downloaded successfully!")

    df = load_prepared_dataframe()
    localities = sorted(df["location"].dropna().unique().tolist())
    
    all_cuisines = set()
    for c_str in df["cuisines"].dropna():
        for c in c_str.split(","):
            all_cuisines.add(c.strip())
    cuisines = sorted(list(all_cuisines))
    
    return localities, cuisines

# Sidebar - Filters
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Zomato_logo.png", width=150)
    st.markdown("### 🔍 Filters")
    
    localities, cuisines = get_metadata()
    
    selected_locality = st.selectbox("Where do you want to eat?", ["Anywhere"] + localities)
    selected_cuisine = st.selectbox("What cuisine do you crave?", ["Any Cuisine"] + cuisines)
    
    price_range = st.slider("Max Price (for two)", min_value=100, max_value=5000, value=1500, step=100)
    min_rating = st.slider("Min Rating", min_value=0.0, max_value=5.0, value=3.5, step=0.1)
    
    if not GROQ_API_KEY:
        st.error("🔑 **Groq API Key Missing**")
        st.info("To run the AI recommendations, please add your `GROQ_API_KEY` to `.env` (locally) or Streamlit Secrets (cloud).")
    
    get_recs = st.button("Get Recommendations", disabled=not GROQ_API_KEY)

# Main Area
st.markdown('<h1 class="main-header">zomato AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Personalized restaurant recommendations powered by reasoning.</p>', unsafe_allow_html=True)

if get_recs:
    with st.spinner("🍽️ Asking the AI for the best spots..."):
        # Prepare preferences
        prefs = UserPreferences(
            max_price=float(price_range),
            min_rating=float(min_rating),
            locality=selected_locality if selected_locality != "Anywhere" else None,
            desired_cuisines=[selected_cuisine] if selected_cuisine != "Any Cuisine" else None
        )
        
        try:
            # Get recommendations
            recommendations: List[LLMRestaurantRecommendation] = get_llm_recommendations(prefs, max_candidates=15, max_results=5)
            
            if not recommendations:
                st.warning("😕 No restaurants found matching your criteria. Try loosening your filters!")
            else:
                st.markdown(f"### Found {len(recommendations)} matches for you")
                
                for item in recommendations:
                    res = item.restaurant
                    
                    # Custom Card HTML
                    cuisines_list = res.cuisines.split(',')
                    cuisines_html = "".join([f'<span class="cuisine-pill">{c.strip()}</span>' for c in cuisines_list])
                    
                    st.markdown(f"""
                        <div class="restaurant-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <h2 class="res-name">{res.name}</h2>
                                    <p style="color: #696969; margin: 4px 0;"><i class="fa fa-map-marker"></i> {res.location}</p>
                                </div>
                                <div class="rating-badge">
                                    {res.rating} ★
                                </div>
                            </div>
                            <div style="margin-top: 10px;">
                                {cuisines_html}
                            </div>
                            <div style="display: flex; gap: 40px; margin-top: 15px;">
                                <div>
                                    <p style="color: #999; font-size: 0.8rem; margin: 0;">PRICE FOR TWO</p>
                                    <p style="font-weight: 700; color: #2D2D2D; margin: 0;">₹{res.price_for_two}</p>
                                </div>
                                <div>
                                    <p style="color: #999; font-size: 0.8rem; margin: 0;">VOTES</p>
                                    <p style="font-weight: 700; color: #2D2D2D; margin: 0;">{res.votes:,}</p>
                                </div>
                            </div>
                            <div class="ai-reason">
                                " {item.reason} "
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
        except GroqClientError as e:
            st.error(f"⚠️ AI Service Error: {str(e)}")
        except Exception as e:
            st.error(f"💥 An unexpected error occurred: {str(e)}")

else:
    # Landing state
    st.info("👈 Use the sidebar to set your preferences and click **Get Recommendations**!")
    
    # Showcase some features or tips
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎯 Smart Filtering")
        st.write("We use structured retrieval to narrow down thousands of options instantly.")
    with col2:
        st.markdown("#### 🧠 AI Reasoning")
        st.write("Our LLM explains *why* a restaurant fits your specific tastes.")
    with col3:
        st.markdown("#### 💎 Verified Data")
        st.write("All recommendations come from the official Zomato dataset.")
