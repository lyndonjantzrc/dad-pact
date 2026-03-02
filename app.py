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

    /* Custom Checkmark Badge */
    .success-badge { 
        background-color: #1B5E20; color: white; padding: 5px 15px; 
        border-radius: 20px; font-size: 14px; font-weight: bold;
        display: inline-block; margin-top: 10px;
    }
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

# Data Fetch with Safety Catch
try:
    res = conn.table("daily_logs").select("*").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    if not df.empty: 
        df['log_date'] = pd.to_datetime(df['log_date']).dt.date
except:
    df = pd.DataFrame()

# --- PAGE 1: CHECK-IN ---
if page == "⚡ Check-In":
    st.title(f"Ready, {user}?")
    
    # Timer Logic
    midnight_cst = datetime.datetime.combine(today_cst + datetime.timedelta(days=1), datetime.time(0, 0), tzinfo=central_tz)
    time_left = midnight_cst - now_cst
    h, rem = divmod(int(time_left.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    
    st.markdown(f"""<div class="timer-container"><div style="color:#8B949E; font-size:12px;">TIME REMAINING</div><div class="timer-digits">{h:02d}:{m:02d}:{s:02d}</div></div>""", unsafe_allow_html=True)

    today = st.date_input("Workout Date", today_cst)
    
    # FIXED: Replaced st.pills with st.radio for stability
    mode = st.radio("Log Type", ["Workout", "Grace"], horizontal=True)
    st.markdown('<div class="success-badge">✅ Type Selected</div>', unsafe_allow_html=True)

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
            run = st.select_slider("Run Duration (Minutes)", options=[0, 10, 15, 20], value=0)
            c1, c2 = st.columns(2)
            with c1: strength = st.toggle("Strength (+15)")
            with c2: labor = st.toggle("Labor (+10)")
            points = min(30, run + (15 if strength else 0) + (10 if labor else 0))

    st.divider()
    st.markdown(f"### Total Earned: **{points} PTS**")
    
    if st.button("SUBMIT WORKOUT"):
        try:
            conn.table("daily_logs").insert({"participant_name": user, "log_date": str(today), "points": points, "entry_type": e_type}).execute()
            st.balloons()
            st.success("Data Sent!")
            st.rerun()
        except: 
            st.error("Entry already exists for this date.")

# --- PAGE 2: SCOREBOARD ---
elif page == "🏆 Scoreboard":
    st.title("The Standings")
    month_start = today_cst.replace(day=1)
    
    # Range of dates to check for penalties
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
        summary.append({"Dad": d, "Pts": logged_pts, "Penalty": missed_p, "Total": logged_pts + missed_p})
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    st.dataframe(score_df, use_container_width=True, hide_index=True)
    
    st.divider()
    if not score_df.empty:
        winner = score_df.iloc[0]['Dad']
        loser = score_df.iloc[-1]['Dad']
        st.markdown(f'<div class="status-banner winner-bg">🥇 Leader: {winner}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="status-banner loser-bg">⚓ Anchor: {loser}</div>', unsafe_allow_html=True)

# --- PAGE 3: TRENDS ---
elif page == "📊 Trends":
    st.title("Performance Stats")
    if not df.empty:
        df_sort = df.sort_values('log_date')
        df_sort['Cumulative Points'] = df_sort.groupby('participant_name')['points'].transform(pd.Series.cumsum)
        fig = px.line(df_sort, x='log_date', y='Cumulative Points', color='participant_name', markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for March yet. Get to work!")

# --- PAGE 4: ADMIN ---
elif page == "⚙️ Admin":
    if user == "Lyndon":
        st.warning("Danger Zone")
        if st.button("RESET MONTHLY BOARD"):
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()
            st.success("Wiped!")
            st.rerun()
