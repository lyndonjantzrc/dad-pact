import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import plotly.express as px
import datetime
import pytz  # For Central Time logic

# --- CONFIG & TIMEZONE ---
st.set_page_config(page_title="Dad Pact 2.0", layout="centered")
central_tz = pytz.timezone('US/Central')

def get_now_central():
    return datetime.datetime.now(central_tz)

now_cst = get_now_central()
today_cst = now_cst.date()

# --- STYLING (The "Fun" Part) ---
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* Winner/Loser Banners */
    .winner-box { 
        background: linear-gradient(90deg, #2E7D32, #43A047); 
        color: white; padding: 20px; border-radius: 15px; 
        text-align: center; font-weight: bold; font-size: 24px;
        margin-bottom: 10px; border: 2px solid #A5D6A7;
    }
    .loser-box { 
        background: linear-gradient(90deg, #C62828, #E53935); 
        color: white; padding: 20px; border-radius: 15px; 
        text-align: center; font-weight: bold; font-size: 24px;
        margin-top: 10px; border: 2px solid #EF9A9A;
    }
    
    /* Countdown Timer Style */
    .timer-text { 
        font-family: 'Courier New', Courier, monospace;
        color: #FFB300; font-size: 22px; text-align: center;
        background: #262730; padding: 10px; border-radius: 10px;
        border: 1px solid #FFB300; margin-bottom: 20px;
    }

    /* Custom Buttons */
    div.stButton > button:first-child { 
        background: #1E88E5; color: white; border-radius: 30px;
        height: 3.5rem; width: 100%; border: none; font-size: 18px;
    }
    div.stButton > button:hover { background: #1565C0; border: none; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ Dad Pact: Season 2")
    u_input = st.selectbox("Identify yourself:", ["Damien", "Jesse", "Lyndon", "Todd"])
    p_input = st.text_input("Access Code", type="password")
    if st.button("AUTHENTICATE"):
        res = conn.table("participants").select("password").eq("name", u_input).execute()
        if res.data and str(res.data[0]['password']) == p_input:
            st.session_state['auth'], st.session_state['user'] = True, u_input
            st.rerun()
        else:
            st.error("Invalid Code")
    st.stop()

user = st.session_state['user']
page = st.sidebar.radio("Command Center", ["Log Activity", "Scoreboard", "Data Visuals", "Admin"])

# Data Fetch
res = conn.table("daily_logs").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
if not df.empty: 
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date

# --- PAGE 1: CHECK-IN ---
if page == "Log Activity":
    st.title(f"Welcome back, {user}")
    
    # COUNTDOWN TIMER LOGIC
    midnight_cst = datetime.datetime.combine(today_cst + datetime.timedelta(days=1), datetime.time(0, 0), tzinfo=central_tz)
    time_left = midnight_cst - now_cst
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""<div class="timer-text">⏳ TIME UNTIL DEADLINE: {hours:02d}h {minutes:02d}m {seconds:02d}s</div>""", unsafe_allow_html=True)

    today = st.date_input("Entry Date", today_cst)
    is_sun = today.strftime('%A') == 'Sunday'
    mode = st.radio("What's the play?", ["🔥 Workout", "🛡️ Grace Day"])

    if mode == "🛡️ Grace Day":
        points, e_type = 0, "grace"
    elif is_sun:
        u_logs = df[df['participant_name'] == user] if not df.empty else pd.DataFrame()
        month_start = today.replace(day=1)
        used_bonus = len(u_logs[u_logs['entry_type'] == 'sunday_bonus'])
        st.info(f"Sunday Bonus: {used_bonus}/2 used this month.")
        opt = st.radio("Sunday Option:", ["Rest Day (0 pts)", "Bonus Catch-up (+20 pts)"])
        points = 20 if "+20" in opt else 0
        e_type = "sunday_bonus" if points == 20 else "sunday_free"
    else:
        runs = {"None": 0, "10m (5pts)": 5, "15m (10pts)": 10, "20m (15pts)": 15}
        run = st.selectbox("Run Duration:", list(runs.keys()))
        strength = st.checkbox("Strength Training (+15)")
        labor = st.checkbox("Manual Labor/Sports (+10)")
        points = min(30, runs[run] + (15 if strength else 0) + (10 if labor else 0))
        e_type = "exercise"

    st.metric("Points to be Earned", points)
    if st.button("LOCK IN ENTRY"):
        try:
            conn.table("daily_logs").insert({"participant_name": user, "log_date": str(today), "points": points, "entry_type": e_type}).execute()
            st.success("Entry Secured!"); st.balloons()
        except: st.error("Date already logged!")

# --- PAGE 2: SCOREBOARD ---
elif page == "Scoreboard":
    st.title("🏆 Leaderboard")
    month_start = today_cst.replace(day=1)
    
    # Penalty calculation (only for Mon-Sat)
    active_range = [d.date() for d in pd.date_range(start=month_start, end=today_cst - datetime.timedelta(days=1)) if d.strftime('%A') != 'Sunday']
    
    summary = []
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:
        d_logs = df[df['participant_name'] == d] if not df.empty else pd.DataFrame()
        logged_pts = d_logs['points'].sum()
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []
        missed_penalty = sum(1 for day in active_range if day not in logged_dates) * -15
        summary.append({"Dad": d, "Logged": logged_pts, "Penalty": missed_penalty, "Total": logged_pts + missed_penalty})
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    
    # WINNER AND LOSER BANNERS
    winner = score_df.iloc[0]['Dad']
    loser = score_df.iloc[-1]['Dad']
    
    st.markdown(f"""<div class="winner-box">👑 CURRENT LEADER: {winner.upper()}</div>""", unsafe_allow_html=True)
    st.table(score_df)
    st.markdown(f"""<div class="loser-box">🤡 CURRENT LOSER: {loser.upper()}</div>""", unsafe_allow_html=True)

# --- PAGE 3: STATS ---
elif page == "Data Visuals":
    st.header("📈 Growth Chart")
    if not df.empty:
        df_sort = df.sort_values('log_date')
        df_sort['Cumulative Points'] = df_sort.groupby('participant_name')['points'].transform(pd.Series.cumsum)
        fig = px.line(df_sort, x='log_date', y='Cumulative Points', color='participant_name', markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 4: ADMIN ---
elif page == "Admin":
    if user == "Lyndon":
        if st.button("RESET SEASON (WIPE ALL DATA)"):
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()
            st.success("Board Reset for the new month!")
