import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import os


# Set Page Config
st.set_page_config(
        page_title="MindCare AI Social Anxiety Detection",
        page_icon="https://storage.googleapis.com/kaggle-datasets-images/6869808/11030579/4b09dfab8c969a055d4c2aebd7923f37/dataset-thumbnail.jpg?t=2025-03-14-13-07-42",
        layout="wide",
        initial_sidebar_state="expanded"
)

# Initialize query params only once if needed
if "page" not in st.session_state:
    # Check query params for initial page
    params = st.query_params.get_all("page")
    if params:
        st.session_state.page = params[0]
    else:
        st.session_state.page = "Home"


# API Base URL
# Check if running in Streamlit Cloud (secrets) or Vercel (env vars)
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
    elif os.getenv("API_URL"):
        API_URL = os.getenv("API_URL")
    else:
        API_URL = "http://127.0.0.1:8000"
except FileNotFoundError:
    # st.secrets might raise FileNotFoundError locally if .streamlit/secrets.toml doesn't exist
    if os.getenv("API_URL"):
        API_URL = os.getenv("API_URL")
    else:
        API_URL = "http://127.0.0.1:8000"
except Exception:
    # Fallback for any other access issues
    if os.getenv("API_URL"):
        API_URL = os.getenv("API_URL")
    else:
        API_URL = "http://127.0.0.1:8000"
USER_ID = "guest_streamlit"  # Fixed user for demo

# -----------------------------------------------------------------------------
# CSS STYLES - Exact Port from React Frontend (index.css)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;700;800&display=swap');

    /* Tailwind Base Porting */
    :root {
      --primary: #2CA4B0;
      --primary-dark: #207D87;
      --bg-gradient-start: #F0F9FF;
      --bg-gradient-end: #E0F2FE;
      --white-glass: rgba(255, 255, 255, 0.7);
      --white-solid: #FFFFFF;
      --text-main: #0F172A;
      --text-secondary: #475569;
      --border-glass: rgba(255, 255, 255, 0.6);
      --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
      --shadow-glow: 0 0 20px rgba(44, 164, 176, 0.3);
    }

    /* Global Overrides for Streamlit to Match React App Layout */
    .stApp {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); /* "Rare Wind" - Attractive Aqua to Soft Pink */
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Inter', sans-serif;
        color: #1a202c; /* Ensure dark text for readability */
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Header & Footer Customization */
    /* Hide the standard Streamlit header elements (hamburger menu, deploy button) */
    /* Header & Footer Customization */
    /* Header & Footer Customization */
    /* Headers - Make transparent but keep structure */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Toolbar - Hide specific items but keep container if needed for spacing */
    [data-testid="stToolbar"] {
        right: 2rem;
        background: transparent !important;
    }
    
    /* Hide specific toolbar items we don't want (like the deploy button/running man if desired, 
       but keeping them visible is safer for now to ensure we don't accidentally hide the toggle if it lives there) */
    
    /* Decoration line */
    [data-testid="stDecoration"] {
        display: none;
    }

    /* The Sidebar Toggle Button (> or x) */
    /* The Sidebar Toggle Button (> or x) */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        backdrop-filter: blur(8px);
        border-radius: 50% !important;
        border: 2px solid rgba(255,255,255,0.5) !important;
        z-index: 1000000 !important; /* Higher than anything else */
        position: fixed !important;
        top: 24px !important;
        left: 120px !important;     /* Moved forward by ~1 inch (was 32px) */
        width: 60px !important;
        height: 60px !important;
        align-items: center !important;
        justify-content: center !important;
        transform: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: scale(1.1) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        color: #ffffff !important;
    }
    /* The following block was a duplicate and has been removed to avoid conflicts */
    /*
        z-index: 999999 !important;
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(4px);
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(0,0,0,0.05);
    }

    [data-testid="collapsedControl"]:hover {
        background-color: #FFFFFF !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
        transform: scale(1.1);
        color: #2CA4B0 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;}  <-- Removed to fix sidebar toggle issue */

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--white-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid var(--border-glass);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02);
    }
    
    .sidebar-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #0F172A, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        padding-left: 0.5rem;
    }

    /* HOME PAGE STYLES (Rich UI) */
    .home-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        padding-top: 2rem;
    }

    .welcome-card {
        max-width: 38rem; /* Reduced width */
        width: 100%;
        background: rgba(255, 255, 255, 0.65); /* Uniform Light Glass */
        backdrop-filter: blur(12px);
        padding: 1.5rem; /* Reduced padding */
        border-radius: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.6);
        margin-bottom: 2rem;
        position: relative;
        z-index: 10;
        text-align: center;
    }
    
    .welcome-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #0F172A;
    }
    
    .welcome-subtitle {
        color: #64748B;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 500;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
        height: 100%;
        text-align: left;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon-wrapper {
        width: 48px;
        height: 48px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .feature-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #1E293B;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #64748B;
        line-height: 1.4;
    }

    /* Card Variations */
    .card-blue { border-left: 4px solid #3B82F6; }
    .icon-blue { color: #3B82F6; }
    
    .card-orange { border-left: 4px solid #F59E0B; }
    .icon-orange { color: #F59E0B; }
    
    .card-green { border-left: 4px solid #10B981; }
    .icon-green { color: #10B981; }
    
    .card-purple { border-left: 4px solid #8B5CF6; }
    .icon-purple { color: #8B5CF6; }

    /* Button Styling - Vibrant & Beautiful */
    .stButton button {
        background: linear-gradient(135deg, #00C6FF, #0072FF); /* Vibrant Blue Gradient */
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.8rem 2rem;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 1rem;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 114, 255, 0.5);
        background: linear-gradient(135deg, #0072FF, #00C6FF);
    }
    
    .stButton button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 10px rgba(0, 114, 255, 0.3);
    }

    /* Chat Styling */
    .chat-container {
        padding: 2.5rem;
        background: rgba(255, 255, 255, 0.95); /* More opaque */
        border-radius: 1.5rem;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1); 
        margin-top: 1rem;
    }

    .anxiety-card {
        margin-top: 1.5rem;
        padding: 1.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid;
    }
    
    .anxiety-card.low { background: linear-gradient(to bottom right, #ECFDF5, #ffffff); border-color: #D1FAE5; }
    .anxiety-card.moderate { background: linear-gradient(to bottom right, #FFFBEB, #ffffff); border-color: #FEF3C7; }
    .anxiety-card.high { background: linear-gradient(to bottom right, #FEF2F2, #ffffff); border-color: #FEE2E2; }
    
    .suggestion-item {
        background: white;
        padding: 12px 16px; 
        margin-bottom: 8px; 
        border-radius: 12px;
        font-size: 0.95rem;
        color: #475569;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* History Styles */
    .history-item-card {
        display: flex; /* Simplified for Streamlit grid limits */
        align-items: center;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(8px);
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 1rem;
        transition: all 0.3s;
        justify-content: space-between;
    }
    
    .history-item-card:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: rgba(44, 164, 176, 0.2);
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid transparent;
        display: inline-block;
    }
    
    .status-badge.low { background: #ECFDF5; color: #059669; border-color: #D1FAE5; }
    .status-badge.moderate { background: #FFFBEB; color: #D97706; border-color: #FEF3C7; }
    .status-badge.high { background: #FEF2F2; color: #DC2626; border-color: #FEE2E2; }

    /* Insights Styles */
    .stat-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 1.25rem;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        overflow: hidden;
        transition: all 0.3s;
        height: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.1);
    }
    
    .stat-card.low { border-left: 4px solid #10B981; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(255,255,255,0.9)); }
    .stat-card.moderate { border-left: 4px solid #F59E0B; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(255,255,255,0.9)); }
    .stat-card.high { border-left: 4px solid #EF4444; background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(255,255,255,0.9)); }
    
    .stat-label { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #64748B; letter-spacing: 0.1em; }
    .stat-value { font-size: 2.5rem; font-weight: 800; color: #0F172A; }

    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
def navigate():
    # Update query params to reflect current page
    st.query_params["page"] = st.session_state.page


st.markdown("""
<style>
    /* Sidebar Container Override */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #A8EDEA 0%, #FED6E3 100%); /* "Soft Teal to Pink" - Matching Main Page */
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
    }
    
    /* Hide Radio Buttons default circles */
    div[role="radiogroup"] > label > div:first-of-type {
        display: none !important;
    }
    
    /* Style Radio Labels as Navigation Links */
    div[role="radiogroup"] {
        gap: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        padding-top: 1.5rem !important;
        background: transparent !important;
    }
    
    div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 12px 18px !important;
        border-radius: 16px !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #475569 !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        background: rgba(255, 255, 255, 0.4) !important;
        margin-bottom: 6px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #2CA4B0 !important;
        transform: translateX(6px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    
    /* Active State Styling */
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 99%, #FECFEF 100%) !important; /* "Warm Peach" Gradient */
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4) !important;
    }
    
    /* TEXT Inside Radio - Ensure it inherits color correctly */
    div[role="radiogroup"] label[data-checked="true"] p {
        color: white !important;
    }
    
    /* Text Styling inside Radio */
    div[role="radiogroup"] label * {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em;
    }

    /* Logo Container Styling */
    .sidebar-logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        margin-bottom: 32px;
        padding: 24px 12px;
        background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(255,255,255,0.2));
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        backdrop-filter: blur(8px);
    }
    
    .sidebar-icon-wrapper {
        width: 64px;
        height: 64px;
        border-radius: 16px;
        background: linear-gradient(135deg, #2CA4B0, #207D87);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 8px 20px rgba(44, 164, 176, 0.25);
        font-size: 2rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    
    .sidebar-title-text {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #0F172A, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        text-align: center;
    }
    
    .sidebar-subtitle {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-align: center;
        margin-top: 4px;
    }

</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-container">
        <div class="sidebar-icon-wrapper">🌿</div>
        <div>
            <div class="sidebar-title-text">MindCare AI</div>
            <div class="sidebar-subtitle">Social Anxiety Detection</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Use key="page" to sync with session state
    selection = st.radio(
        "",
        ["Home", "Chat", "History", "Insights"],
        key="page",
        label_visibility="collapsed",
        on_change=navigate
    )

# -----------------------------------------------------------------------------
# VIEW: HOME
# -----------------------------------------------------------------------------
if st.session_state.page == "Home":
    st.markdown("""
    <div class="home-container">
        <div class="welcome-card">
            <div class="welcome-title">MindCare AI <span style="color: #2CA4B0;">Social Anxiety Detection</span></div>
            <div class="welcome-subtitle">Your personal companion for real-time anxiety analysis and supportive coping strategies.<br>Powered by Advanced AI to help you find balance.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards Grid
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="feature-card card-blue">
            <div class="feature-icon-wrapper icon-blue">💬</div>
            <div class="feature-title">Share Feelings</div>
            <div class="feature-desc">Express yourself freely in a safe, judgment-free space.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="feature-card card-orange">
            <div class="feature-icon-wrapper icon-orange">⚡</div>
            <div class="feature-title">AI Analysis</div>
            <div class="feature-desc">Instant feedback on your anxiety levels.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="feature-card card-green">
            <div class="feature-icon-wrapper icon-green">🛡️</div>
            <div class="feature-title">Track Progress</div>
            <div class="feature-desc">Monitor your emotional journey with insights.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown("""
        <div class="feature-card card-purple">
            <div class="feature-icon-wrapper icon-purple">🔒</div>
            <div class="feature-title">Private & Secure</div>
            <div class="feature-desc">Your data is processed locally and kept private.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_center = st.columns([1,1,1])
    with col_center[1]:
         # Callback function to change page
         def go_to_chat():
             st.session_state.page = "Chat"
         
         st.button("START CHATTING NOW", on_click=go_to_chat)

# -----------------------------------------------------------------------------
# VIEW: CHAT
# -----------------------------------------------------------------------------
elif st.session_state.page == "Chat":
    # Move Header OUTSIDE container to remove "box above"
    st.markdown("<h2 style='text-align: center; color: #1E293B; margin-bottom: 2rem;'>How are you feeling today?</h2>", unsafe_allow_html=True)
    
    # Removed chat-container wrapper
    
    c_pad1, c_main, c_pad2 = st.columns([1, 6, 1])
    
    with c_main:
        user_input = st.text_area("", placeholder="Type your thoughts here...", height=150)
        
        if st.button("Analyze", use_container_width=True):
            if not user_input.strip():
                st.warning("Please enter some text.")
            else:
                try:
                    with st.spinner("Analyzing..."):
                        res = requests.post(f"{API_URL}/predict", json={"text": user_input, "user_id": USER_ID})
                        
                    if res.status_code == 200:
                        data = res.json()
                        lvl = data.get("anxiety_level", "Unknown")
                        expl = data.get("explanation", "")
                        suggs = data.get("suggestions", [])
                        
                        st.subheader("Analysis Result")
                        if "Low" in lvl:
                            st.success(f"**{lvl}**")
                        elif "Moderate" in lvl:
                            st.warning(f"**{lvl}**")
                        else:
                            st.error(f"**{lvl}**")
                        
                        st.write(expl)
                        
                        st.subheader("Suggested Actions")
                        for s in suggs:
                            st.markdown(f"- {s}")
                    else:
                        st.error("Error connecting to backend.")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
    
    
    # st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: HISTORY
# -----------------------------------------------------------------------------
elif st.session_state.page == "History":
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 1.5rem; border: 1px solid rgba(255,255,255,0.6); margin-bottom: 2rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); text-align: center; max-width: 38rem; margin-left: auto; margin-right: auto;'>
            <h2 style='color: #1E293B; margin: 0; font-family: Outfit, sans-serif; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em;'>Past Conversations</h2>
            <p style='color: #475569; margin-top: 0.5rem; font-size: 1rem; font-weight: 500;'>Review your journey and track your mental well-being over time.</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        res = requests.get(f"{API_URL}/history/{USER_ID}")
        if res.status_code == 200:
            history = res.json()
            
            # Header
            st.markdown("""
            <div style="display: flex; padding: 1rem; border-radius: 12px; font-size: 0.85rem; color: #1e293b; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem; background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.5);">
                <div style="width: 20%;">Date & Time</div>
                <div style="width: 45%;">Message</div>
                <div style="width: 20%; text-align: center;">Anxiety Level</div>
                <div style="width: 15%; text-align: right;">Action</div>
            </div>
            """, unsafe_allow_html=True)
            
            for item in history:
                timestamp = item.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(str(timestamp))
                    time_str = dt.strftime("%d %b %Y, %I:%M %p")
                except:
                    time_str = str(timestamp)
                    
                msg = item.get("message", "")
                lvl = item.get("anxiety_level", "Unknown")
                cid = item.get("id")
                
                lvl_cls = "low"
                if "Moderate" in lvl: lvl_cls = "moderate"
                elif "High" in lvl: lvl_cls = "high"
                
                with st.container():
                     col_d, col_m, col_l, col_a = st.columns([2, 4.5, 2, 1.5])
                     with col_d:
                         st.markdown(f"<div style='color: #64748B; font-size: 0.85rem; padding-top: 10px;'>{time_str}</div>", unsafe_allow_html=True)
                     with col_m:
                         st.markdown(f"<div style='color: #334155; font-weight: 500; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-top: 10px;'>{msg}</div>", unsafe_allow_html=True)
                     with col_l:
                         st.markdown(f"<div class='status-badge {lvl_cls}'>{lvl}</div>", unsafe_allow_html=True)
                     with col_a:
                         if st.button("🗑️", key=f"del_{cid}"):
                             requests.delete(f"{API_URL}/delete_chat/{cid}")
                             st.rerun()
                             
                     st.markdown("<hr style='margin: 0.5rem 0; border: none; border-bottom: 1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)

        else:
            st.error("Failed to load history.")
    except Exception as e:
        st.error(f"Error fetching history: {e}")

# -----------------------------------------------------------------------------
# VIEW: INSIGHTS
# -----------------------------------------------------------------------------
elif st.session_state.page == "Insights":
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 1.5rem; border: 1px solid rgba(255,255,255,0.6); margin-bottom: 2rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); text-align: center; max-width: 38rem; margin-left: auto; margin-right: auto;'>
            <h2 style='color: #1E293B; margin: 0; font-family: Outfit, sans-serif; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em;'>Anxiety Trends</h2>
            <p style='color: #475569; margin-top: 0.5rem; font-size: 1rem; font-weight: 500;'>Visualizing your emotional data to help you understand patterns.</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        res = requests.get(f"{API_URL}/get_insights/{USER_ID}")
        if res.status_code == 200:
            data = res.json()
            low = data.get("low", 0)
            mod = data.get("moderate", 0)
            high = data.get("high", 0)
            
            # Chart
            chart_data = pd.DataFrame({
                "Anxiety Level": ["Low", "Moderate", "High"],
                "Count": [low, mod, high]
            })
            
            st.bar_chart(chart_data, x="Anxiety Level", y="Count", color="#AED9E0") # Softer Pastel Teal
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Stats Cards
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="stat-card low">
                    <div class="stat-info">
                        <div class="stat-label">Low Anxiety</div>
                        <div class="stat-value">{low}</div>
                    </div>
                    <div style="font-size: 2rem;">😊</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="stat-card moderate">
                    <div class="stat-info">
                        <div class="stat-label">Moderate Anxiety</div>
                        <div class="stat-value">{mod}</div>
                    </div>
                    <div style="font-size: 2rem;">😐</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="stat-card high">
                    <div class="stat-info">
                        <div class="stat-label">High Anxiety</div>
                        <div class="stat-value">{high}</div>
                    </div>
                    <div style="font-size: 2rem;">😔</div>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.error("Failed to load insights.")
    except Exception as e:
        st.error(f"Error fetching insights: {e}")


