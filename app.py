import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import plotly.express as px
import datetime
import pytz

# --- CONFIG & TIMEZONE ---
st.set_page_config(page_title="Dad Pact PRO", layout="centered")
central_tz = pytz.timezone('US/Central')

def get_now_central():
    return datetime.datetime.now(central_tz)

now_cst = get_now_central()
today_cst = now_cst.date()

# --- ADVANCED UI STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #FFFFFF; }
    h1, h2, h3, p { color: #FFFFFF !important; }
    
    /* Banners at Bottom */
    .status-banner {
        padding: 12px; border-radius: 10px; text-align: center;
        font-weight: 800; font-size: 16px; margin: 5px 0;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .winner-bg { background: linear-gradient(90deg, #1B5E20, #4CAF50); border: 1px solid #C8E6C9; color: white; }
    .loser-bg { background: linear-gradient(90deg, #B71C1C, #F44336); border: 1px solid #FFCDD2; color: white; }
    
    /* Timer */
    .timer-container {
        background: #1C2128; border: 2px solid #00E5FF;
        border-radius: 15px; padding: 15px; text-align: center; margin-bottom: 25px;
    }
    .timer-digits { font-family: 'Monaco', monospace; color: #00E5FF; font-size: 28px; font-weight: bold; }

    /* Checkmark Animation */
    @keyframes check { from { transform: scale(0); } to { transform: scale(1.2); } }
    .success-badge { color: #4CAF50; font-size: 18px; animation: check 0.3s ease-in-out; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: 
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ Dad Pact Access")
    u_input = st.selectbox("Who is logging in?", ["Damien", "Jesse", "Lyndon", "Todd"])
    p_input = st.text_input("Password", type="password")
    if st.button("UNLOCK APP"):
        res = conn.table("participants").select("password").eq("name", u_input).execute()
        if res.data and str(res.data[0]['password']) == p_input:
            st.session_state['auth'], st.session_state['user'] = True, u_input
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

user = st.session_state['user']
page = st.sidebar.radio("Navigation", ["⚡ Check-In", "🏆 Scoreboard", "📊 Trends", "⚙️ Admin"])
