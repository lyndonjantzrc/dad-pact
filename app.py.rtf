{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
from st_supabase_connection import SupabaseConnection\
import pandas as pd\
import plotly.express as px\
from datetime import datetime, timedelta\
\
# --- UI SETUP ---\
st.set_page_config(page_title="Dad Pact", layout="centered")\
st.markdown("""<style>\
    div.stButton > button:first-child \{ height: 3rem; width: 100%; border-radius: 10px; background-color: #D32F2F; color: white; font-weight: bold; \}\
    .stMetric \{ background: #ffffff; border: 1px solid #eee; padding: 15px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); \}\
</style>""", unsafe_allow_index=True)\
\
conn = st.connection("supabase", type=SupabaseConnection)\
\
# --- AUTHENTICATION SYSTEM ---\
if 'authenticated' not in st.session_state:\
    st.session_state['authenticated'] = False\
\
if not st.session_state['authenticated']:\
    st.title("\uc0\u55357 \u56592  Dad Pact Login")\
    user_input = st.selectbox("Who are you?", ["Damien", "Jesse", "Lyndon", "Todd"])\
    pass_input = st.text_input("Password", type="password")\
\
    if st.button("Login"):\
        res = conn.table("participants").select("password").eq("name", user_input).execute()\
        if res.data and res.data[0]['password'] == pass_input:\
            st.session_state['authenticated'] = True\
            st.session_state['user'] = user_input\
            st.rerun()\
        else:\
            st.error("Invalid Password")\
    st.stop()\
\
# --- APP NAVIGATION (POST-LOGIN) ---\
user = st.session_state['user']\
page = st.sidebar.radio("Menu", ["Daily Check-In", "Scoreboard", "Performance Chart", "Admin Panel"])\
if st.sidebar.button("Logout"):\
    st.session_state['authenticated'] = False\
    st.rerun()\
\
# Data Fetch (once per session after login)\
res = conn.table("daily_logs").select("*").execute()\
all_logs = pd.DataFrame(res.data) if res.data else pd.DataFrame()\
if not all_logs.empty:\
    all_logs['log_date'] = pd.to_datetime(all_logs['log_date']).dt.date\
\
# --- PAGE 1: DAILY CHECK-IN ---\
if page == "Daily Check-In":\
    st.header(f"Hello, \{user\} \uc0\u55357 \u56394 ")\
    today = st.date_input("Date", datetime.now()).date()\
    is_sunday = today.strftime('%A') == 'Sunday'\
\
    entry_mode = st.radio("What happened today?", ["Workout", "Grace Day"])\
\
    if entry_mode == "Grace Day":\
        points, entry_type = 0, "grace"\
    elif is_sunday:\
        # Sunday Logic with Missed Day check\
        month_start = today.replace(day=1)\
        date_range = pd.date_range(start=month_start, end=today - timedelta(days=1)).date\
        u_logs = all_logs[all_logs['participant_name'] == user] if not all_logs.empty else pd.DataFrame()\
        logged_dates = u_logs['log_date'].tolist() if not u_logs.empty else []\
        missed_count = sum(1 for d in date_range if d not in logged_dates and d.strftime('%A') != 'Sunday')\
        bonus_count = len(u_logs[u_logs['entry_type'] == 'sunday_bonus'])\
\
        max_bonuses = 2 if missed_count > 0 else 1\
        sun_opt = st.radio(f"Sunday Bonus (\{bonus_count\}/\{max_bonuses\} used):", ["Free Day (0 pts)", "Bonus Day (+20 pts)"])\
        points = 20 if "Bonus" in sun_opt and bonus_count < max_bonuses else 0\
        entry_type = "sunday_bonus" if points == 20 else "sunday_free"\
    else:\
        run_map = \{"0 min": 0, "10 min (5pts)": 5, "15 min (10pts)": 10, "20 min (15pts)": 15\}\
        run = st.selectbox("Run Duration:", list(run_map.keys()))\
        strength = st.checkbox("Strength (+15 pts)")\
        labor = st.checkbox("Physical Labor / Sports (+10 pts)")\
        points = min(30, run_map[run] + (15 if strength else 0) + (10 if labor else 0))\
        entry_type = "exercise"\
\
    if st.button("SAVE ENTRY", key="save_entry"):\
        try:\
            conn.table("daily_logs").insert(\{"participant_name": user, "log_date": str(today), "points": points, "entry_type": entry_type\}).execute()\
            st.success("Log Saved!")\
            st.balloons()\
            st.rerun() # Refresh to show updated logs/bonuses\
        except:\
            st.error("Already logged for this date!")\
\
# --- PAGE 2: SCOREBOARD (MONTH-TO-DATE) ---\
elif page == "Scoreboard":\
    st.header("\uc0\u55356 \u57286  Monthly Leaderboard")\
    today_date_obj = datetime.now().date()\
    month_start = today_date_obj.replace(day=1)\
    active_days = [d for d in pd.date_range(start=month_start, end=today_date_obj - timedelta(days=1)).date if d.strftime('%A') != 'Sunday']\
\
    summary = []\
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:\
        d_logs = all_logs[all_logs['participant_name'] == d] if not all_logs.empty else pd.DataFrame()\
\
        # 1. Base Points from logs\
        base_pts = d_logs['points'].sum() if not d_logs.empty else 0\
\
        # 2. Auto-Calculate Missed Penalties (-15 per empty Mon-Sat)\
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []\
        missed_count_for_penalty = sum(1 for day in active_days if day not in logged_dates)\
        penalty_total = missed_count_for_penalty * -15\
\
        # 3. Consistency Bonus (+20) - Rule 9\
        # Requires 18 days of 25+ points (mon-sat only) from 'exercise' type\
        ex_logs = d_logs[d_logs['entry_type'] == 'exercise'] if not d_logs.empty else pd.DataFrame()\
        consistency_days_achieved = len(ex_logs[ex_logs['points'] >= 25])\
        consist_bonus = 20 if consistency_days_achieved >= 18 else 0\
\
        summary.append(\{\
            "Dad": d, \
            "Logged Pts": base_pts, \
            "Missed Penalty": penalty_total,\
            "Consistency Bonus": consist_bonus,\
            "Total Score": base_pts + penalty_total + consist_bonus\
        \})\
\
    score_df = pd.DataFrame(summary).sort_values(by="Total Score", ascending=False).reset_index(drop=True)\
    score_df.index += 1 # Ranks 1, 2, 3, 4\
    st.table(score_df)\
    st.success(f"\uc0\u55357 \u56401  Winner: \{score_df.iloc[0]['Dad']\}")\
    st.error(f"\uc0\u55357 \u56448  Loser: \{score_df.iloc[-1]['Dad']\}")\
\
# --- PAGE 3: PERFORMANCE CHART ---\
elif page == "Performance Chart":\
    st.header("\uc0\u55357 \u56520  Month-to-Date Performance")\
    if not all_logs.empty:\
        # Prepare data for charting\
        chart_data = all_logs.copy()\
\
        # Fill in missed days for accurate cumulative plot\
        full_date_range = pd.date_range(start=all_logs['log_date'].min(), end=datetime.now().date(), freq='D')\
\
        all_participants_data = []\
        for p in participants:\
            p_df = chart_data[chart_data['participant_name'] == p].set_index('log_date')\
            p_df = p_df.reindex(full_date_range).fillna(0) # Fill missing dates with 0 points\
\
            # Apply missed penalties to chart data\
            for d_idx, d_date in enumerate(p_df.index):\
                if d_date.strftime('%A') != 'Sunday' and p_df.loc[d_date, 'points'] == 0 and p_df.loc[d_date, 'entry_type'] == 0:\
                    p_df.loc[d_date, 'points'] = -15\
                    p_df.loc[d_date, 'entry_type'] = 'missed' # For visualization\
\
            p_df['Cumulative Points'] = p_df['points'].cumsum()\
            p_df['participant_name'] = p\
            all_participants_data.append(p_df.reset_index().rename(columns=\{'index': 'log_date'\}))\
\
        final_chart_df = pd.concat(all_participants_data)\
\
        fig = px.line(final_chart_df, x='log_date', y='Cumulative Points', color='participant_name', \
                      markers=True, title="Cumulative Points by Dad")\
        st.plotly_chart(fig, use_container_width=True)\
    else:\
        st.info("No data to chart yet. Log some workouts!")\
\
# --- PAGE 4: ADMIN PANEL ---\
elif page == "Admin Panel":\
    if user == "Lyndon": # Admin check\
        st.subheader("Lyndon's Admin Controls")\
        if st.button("RESET DATABASE FOR NEW MONTH"):\
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()\
            st.success("All Scores Cleared for the New Month.")\
            st.rerun() # Refresh to show empty board\
    else:\
        st.error("Access Denied: Only Lyndon can use Admin Panel.")}