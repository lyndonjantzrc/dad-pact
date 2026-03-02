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
    /* Dark Base with High Contrast Text */
    .stApp { background-color: #0B0E11; color: #FFFFFF; }
    h1, h2, h3, p { color: #FFFFFF !important; text-shadow: 1px 1px 2px black; }
    
    /* Winner/Loser Banners (Smaller & Bottom Aligned) */
    .status-banner {
        padding: 12px; border-radius: 10px; text-align: center;
        font-weight: 800; font-size: 16px; margin: 5px 0;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .winner-bg { background: linear-gradient(90deg, #1B5E20, #4CAF50); border: 1px solid #C8E6C9; color: white; }
    .loser-bg { background: linear-gradient(90deg, #B71C1C, #F44336); border: 1px solid #FFCDD2; color: white; }
    
    /* Countdown Timer */
    .timer-container {
        background: #1C2128; border: 2px solid #00E5FF;
        border-radius: 15px; padding: 15px; text-align: center; margin-bottom: 25px;
    }
    .timer-digits { font-family: 'Monaco', monospace; color: #00E5FF; font-size: 28px; font-weight: bold; }

    /* Pill Selection Buttons */
    .stSelectbox div[data-baseweb="select"] { border-radius: 20px; background-color: #1C2128; border: 1px solid #30363D; }
    
    /* Radio Button "Pills" Styling */
    div[data-testid="stMarkdownContainer"] > p { font-weight: 600; font-size: 1.1rem; }
    
    /* Success Checkmark Animation */
    @keyframes check { from { transform: scale(0); } to { transform: scale(1.2); } }
    .success-badge { color: #4CAF50; font-size: 24px; animation: check 0.3s ease-in-out; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

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

# Data Fetch
res = conn.table("daily_logs").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
if not df.empty: 
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date

# --- PAGE 1: CHECK-IN ---
if page == "⚡ Check-In":
    st.title(f"Ready, {user}?")
    
    # TIMER BOX
    midnight_cst = datetime.datetime.combine(today_cst + datetime.timedelta(days=1), datetime.time(0, 0), tzinfo=central_tz)
    time_left = midnight_cst - now_cst
    h, rem = divmod(int(time_left.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    
    st.markdown(f"""<div class="timer-container"><div style="color:#8B949E; font-size:12px;">TIME REMAINING</div><div class="timer-digits">{h:02d}:{m:02d}:{s:02d}</div></div>""", unsafe_allow_html=True)

    today = st.date_input("Workout Date", today_cst)
    
    # ENGAGING PILL SELECTION
    col1, col2 = st.columns(2)
    with col1:
        mode = st.pills("Log Type", ["Workout", "Grace"], index=0)
    with col2:
        if mode: st.markdown('<div class="success-badge">✅ Selection Locked</div>', unsafe_allow_html=True)

    points = 0
    e_type = "exercise"

    if mode == "Grace":
        points, e_type = 0, "grace"
    else:
        is_sun = today.strftime('%A') == 'Sunday'
        if is_sun:
            opt = st.radio("Sunday Slot:", ["Rest Day (0 pts)", "Bonus Catch-up (+20 pts)"], horizontal=True)
            points = 20 if "+20" in opt else 0
            e_type = "sunday_bonus" if points == 20 else "sunday_free"
        else:
            run = st.select_slider("Run Duration", options=[0, 10, 15, 20], value=0)
            st.caption(f"Run Points: {run}")
            
            c1, c2 = st.columns(2)
            with c1: strength = st.toggle("Strength Training (+15)")
            with c2: labor = st.toggle("Labor/Sports (+10)")
            
            points = min(30, run + (15 if strength else 0) + (10 if labor else 0))

    st.divider()
    st.markdown(f"### Total Earned: **{points} PTS**")
    
    if st.button("SUBMIT WORKOUT"):
        try:
            conn.table("daily_logs").insert({"participant_name": user, "log_date": str(today), "points": points, "entry_type": e_type}).execute()
            st.balloons()
            st.success("Data Sent to Database!")
        except: st.error("Entry already exists for this date.")

# --- PAGE 2: SCOREBOARD ---
elif page == "🏆 Scoreboard":
    st.title("The Standings")
    month_start = today_cst.replace(day=1)
    active_range = [d.date() for d in pd.date_range(start=month_start, end=today_cst - datetime.timedelta(days=1)) if d.strftime('%A') != 'Sunday']
    
    summary = []
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:
        d_logs = df[df['participant_name'] == d] if not df.empty else pd.DataFrame()
        logged_pts = d_logs['points'].sum()
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []
        missed_p = sum(1 for day in active_range if day not in logged_dates) * -15
        summary.append({"Dad": d, "Pts": logged_pts, "Penalty": missed_p, "Total": logged_pts + missed_p})
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    
    # CLEAN TABLE
    st.dataframe(score_df, use_container_width=True, hide_index=True)
    
    # BOTTOM BANNERS
    st.divider()
    winner = score_df.iloc[0]['Dad']
    loser = score_df.iloc[-1]['Dad']
    st.markdown(f'<div class="status-banner winner-bg">🥇 Leader: {winner}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-banner loser-bg">⚓ Anchor: {loser}</div>', unsafe_allow_html=True)

# --- PAGE 3: STATS ---
elif page ==
