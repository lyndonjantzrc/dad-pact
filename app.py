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

# --- THE ULTIMATE HIGH-CONTRAST CSS ---
st.markdown("""
<style>
    /* 1. GLOBAL DARK THEME */
    .stApp { background-color: #0B0E11; color: #FFFFFF; }
    
    /* 2. SIDEBAR NAVIGATION STYLING */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    /* Sidebar Text & Radio Buttons */
    [data-testid="stSidebar"] .st-emotion-cache-17l243g, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    /* Highlight the selected menu item */
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
        background: #21262D;
        margin-top: 5px;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363D;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: #1F6FEB !important;
        border: 1px solid #58A6FF !important;
    }

    /* 3. BUTTON OVERHAUL */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1F6FEB, #1158C7);
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF;
        border-radius: 12px;
        height: 3.5rem;
        width: 100%;
        font-size: 20px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    /* 4. SCOREBOARD TABLE STYLING */
    [data-testid="stDataFrame"] {
        background-color: #161B22;
        border-radius: 10px;
        border: 1px solid #30363D;
    }

    /* 5. BANNERS */
    .status-banner {
        padding: 15px; border-radius: 12px; text-align: center;
        font-weight: 900; font-size: 18px; margin: 10px 0;
        text-transform: uppercase; border: 2px solid #FFFFFF;
    }
    .winner-bg { background: linear-gradient(90deg, #238636, #2EA043); color: white; box-shadow: 0 0 15px rgba(46, 160, 67, 0.4); }
    .loser-bg { background: linear-gradient(90deg, #DA3633, #F85149); color: white; box-shadow: 0 0 15px rgba(248, 81, 73, 0.4); }
    
    /* 6. TIMER CARD */
    .timer-container {
        background: #1C2128; border: 2px solid #00E5FF;
        border-radius: 15px; padding: 15px; text-align: center; margin-bottom: 25px;
    }
    .timer-digits { font-family: 'Courier New', monospace; color: #00E5FF; font-size: 36px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: 
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ DAD PACT: SEASON 2")
    u_input = st.selectbox("Select Participant", ["Damien", "Jesse", "Lyndon", "Todd"])
    p_input = st.text_input("Enter Passcode", type="password")
    if st.button("🔓 UNLOCK APP"):
        res = conn.table("participants").select("password").eq("name", u_input).execute()
        if res.data and str(res.data[0]['password']) == p_input:
            st.session_state['auth'], st.session_state['user'] = True, u_input
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

user = st.session_state['user']

# Updated Sidebar Menu Labels
page = st.sidebar.radio("MAIN MENU", ["⚡ LOG WORKOUT", "🏆 LEADERBOARD", "📊 PROGRESS", "⚙️ SYSTEM ADMIN"])

# Data Fetch
try:
    res = conn.table("daily_logs").select("*").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    if not df.empty: 
        df['log_date'] = pd.to_datetime(df['log_date']).dt.date
except:
    df = pd.DataFrame()

# --- PAGE 1: CHECK-IN ---
if page == "⚡ LOG WORKOUT":
    st.title(f"Log Entry: {user}")
    
    # Timer Display
    midnight_cst = datetime.datetime.combine(today_cst + datetime.timedelta(days=1), datetime.time(0, 0), tzinfo=central_tz)
    time_left = midnight_cst - now_cst
    h, rem = divmod(int(time_left.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    
    st.markdown(f"""
    <div class="timer-container">
        <div style="color:#8B949E; font-size:14px; font-weight:bold;">TIME REMAINING TODAY (CST)</div>
        <div class="timer-digits">{h:02d}:{m:02d}:{s:02d}</div>
    </div>
    """, unsafe_allow_html=True)

    today = st.date_input("Date", today_cst)
    mode = st.radio("Entry Type:", ["Workout", "Grace"], horizontal=True)

    points = 0
    e_type = "exercise"

    if mode == "Grace":
        points, e_type = 0, "grace"
    else:
        is_sun = today.strftime('%A') == 'Sunday'
        if is_sun:
            opt = st.radio("Sunday Rest/Bonus:", ["Rest (0 pts)", "Bonus (+20 pts)"], horizontal=True)
            points = 20 if "+20" in opt else 0
            e_type = "sunday_bonus" if points == 20 else "sunday_free"
        else:
            run = st.select_slider("Run Minutes", options=[0, 10, 15, 20], value=0)
            c1, c2 = st.columns(2)
            with c1: strength = st.toggle("Strength (+15)")
            with c2: labor = st.toggle("Labor (+10)")
            points = min(30, run + (15 if strength else 0) + (10 if labor else 0))

    st.divider()
    st.markdown(f"### Points Earned: <span style='color:#00E5FF; font-size:40px;'>{points}</span>", unsafe_allow_html=True)
    
    if st.button("🚀 SUBMIT ENTRY"):
        try:
            conn.table("daily_logs").insert({"participant_name": user, "log_date": str(today), "points": points, "entry_type": e_type}).execute()
            st.balloons()
            st.success("Entry Secured!")
            st.rerun()
        except: 
            st.error("Date already logged.")

# --- PAGE 2: SCOREBOARD ---
elif page == "🏆 LEADERBOARD":
    st.title("Monthly Standings")
    month_start = today_cst.replace(day=1)
    
    if today_cst > month_start:
        active_range = [d.date() for d in pd.date_range(start=month_start, end=today_cst - datetime.timedelta(days=1)) if d.strftime('%A') != 'Sunday']
    else:
        active_range = []
    
    summary = []
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:
        d_logs = df[df['participant_name'] == d] if not df.empty else pd.DataFrame()
        logged_pts = d_logs['points'].sum()
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []
        missed_p = sum(1 for day in active_range if day not in logged_dates) * -15
        summary.append({"Participant": d, "Base Pts": logged_pts, "Penalty": missed_p, "Total": logged_pts + missed_p})
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    
    # Modern High-Contrast Table
    st.table(score_df)
    
    st.divider()
    if not score_df.empty:
        winner = score_df.iloc[0]['Participant']
        loser = score_df.iloc[-1]['Participant']
        st.markdown(f'<div class="status-banner winner-bg">🥇 CURRENT LEADER: {winner.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="status-banner loser-bg">⚓ CURRENT ANCHOR: {loser.upper()}</div>', unsafe_allow_html=True)

# --- PAGE 3: TRENDS ---
elif page == "📊 PROGRESS":
    st.title("Season Trends")
    if not df.empty:
        df_sort = df.sort_values('log_date')
        df_sort['Cumulative Points'] = df_sort.groupby('participant_name')['points'].transform(pd.Series.cumsum)
        fig = px.line(df_sort, x='log_date', y='Cumulative Points', color='participant_name', markers=True, template="plotly_dark")
        fig.update_layout(font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No logs found for March.")

# --- PAGE 4: ADMIN ---
elif page == "⚙️ SYSTEM ADMIN":
    if user == "Lyndon":
        st.title("Admin Controls")
        if st.button("⚠️ WIPE ALL DATA"):
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()
            st.success("Board Reset.")
            st.rerun()
