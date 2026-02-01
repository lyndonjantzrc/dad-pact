import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- UI SETUP ---
st.set_page_config(page_title="Dad Pact", layout="centered")

# FIXED: Changed unsafe_allow_index to unsafe_allow_html
st.markdown("""
<style>
    div.stButton > button:first-child { 
        height: 3rem; 
        width: 100%; 
        border-radius: 12px; 
        background-color: #D32F2F; 
        color: white; 
        font-weight: bold; 
    }
    .stMetric { 
        background: #f8f9fa; 
        border: 1px solid #eee; 
        padding: 15px; 
        border-radius: 15px; 
    }
</style>
""", unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: 
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Dad Pact Login")
    u_input = st.selectbox("Who are you?", ["Damien", "Jesse", "Lyndon", "Todd"])
    p_input = st.text_input("Password", type="password")
    if st.button("Login"):
        res = conn.table("participants").select("password").eq("name", u_input).execute()
        if res.data and str(res.data[0]['password']) == p_input:
            st.session_state['auth'], st.session_state['user'] = True, u_input
            st.rerun()
        else:
            st.error("Invalid Password")
    st.stop()

user = st.session_state['user']
page = st.sidebar.radio("Navigation", ["Check-In", "Scoreboard", "Stats Chart", "Admin"])

# Data Fetch
res = conn.table("daily_logs").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
if not df.empty: 
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date

# --- PAGE 1: CHECK-IN ---
if page == "Check-In":
    st.header(f"Log Entry: {user}")
    today = st.date_input("Date", datetime.now()).date()
    is_sun = today.strftime('%A') == 'Sunday'
    mode = st.radio("Log Type:", ["Workout", "Grace Day"])

    if mode == "Grace Day":
        points, e_type = 0, "grace"
    elif is_sun:
        u_logs = df[df['participant_name'] == user] if not df.empty else pd.DataFrame()
        month_start = today.replace(day=1)
        
        # Calculate missed days safely
        if today > month_start:
            date_range = pd.date_range(start=month_start, end=today - timedelta(days=1)).date
            logged_dates = u_logs['log_date'].tolist() if not u_logs.empty else []
            missed = sum(1 for d in date_range if d not in logged_dates and d.strftime('%A') != 'Sunday')
        else:
            missed = 0
            
        used_bonus = len(u_logs[u_logs['entry_type'] == 'sunday_bonus'])
        max_b = 2 if missed > 0 else 1
        st.info(f"Sunday Bonus: {used_bonus}/{max_b} used this month.")
        opt = st.radio("Option:", ["Free Day (0 pts)", "Bonus Day (+20 pts)"])
        points = 20 if "Bonus" in opt and used_bonus < max_b else 0
        e_type = "sunday_bonus" if points == 20 else "sunday_free"
    else:
        runs = {"0m": 0, "10m (5pts)": 5, "15m (10pts)": 10, "20m (15pts)": 15}
        run = st.selectbox("Run Duration:", list(runs.keys()))
        strength = st.checkbox("Strength (+15)")
        labor = st.checkbox("Labor/Sports (+10)")
        points = min(30, runs[run] + (15 if strength else 0) + (10 if labor else 0))
        e_type = "exercise"

    st.metric("Total Points", points)
    if st.button("SAVE ENTRY"):
        try:
            conn.table("daily_logs").insert({
                "participant_name": user, 
                "log_date": str(today), 
                "points": points, 
                "entry_type": e_type
            }).execute()
            st.success("Saved!")
            st.balloons()
        except Exception as e:
            st.error("Already logged for this date or Database Error.")

# --- PAGE 2: SCOREBOARD ---
elif page == "Scoreboard":
    st.header("🏆 Monthly Standings")
    today_obj = datetime.now().date()
    month_start = today_obj.replace(day=1)
    
    # Generate list of Mon-Sat days passed so far
    if today_obj > month_start:
        active_range = [d.date() for d in pd.date_range(start=month_start, end=today_obj - timedelta(days=1)) if d.strftime('%A') != 'Sunday']
    else:
        active_range = []
    
    summary = []
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:
        d_logs = df[df['participant_name'] == d] if not df.empty else pd.DataFrame()
        logged_pts = d_logs['points'].sum()
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []
        
        missed_penalty = sum(1 for day in active_range if day not in logged_dates) * -15
        consist = 20 if len(d_logs[(d_logs['entry_type'] == 'exercise') & (d_logs['points'] >= 25)]) >= 18 else 0
        
        summary.append({
            "Dad": d, 
            "Logged": logged_pts, 
            "Penalty": missed_penalty, 
            "Bonus": consist, 
            "Total": logged_pts + missed_penalty + consist
        })
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    score_df.index += 1
    st.table(score_df)
    st.error(f"Current Loser: {score_df.iloc[-1]['Dad']}")

# --- PAGE 3: PERFORMANCE CHART ---
elif page == "Stats Chart":
    st.header("📊 Performance Chart")
    if not df.empty:
        df_sort = df.sort_values('log_date')
        df_sort['Cumulative Points'] = df_sort.groupby('participant_name')['points'].transform(pd.Series.cumsum)
        fig = px.line(df_sort, x='log_date', y='Cumulative Points', color='participant_name', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data logged yet.")

# --- PAGE 4: ADMIN ---
elif page == "Admin":
    if user == "Lyndon":
        if st.button("WIPE DATA FOR NEW MONTH"):
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()
            st.success("Board Reset!")