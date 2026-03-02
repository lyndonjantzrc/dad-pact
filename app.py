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


@st.fragment(run_every=datetime.timedelta(hours=4))
def keep_alive():
    """Runs periodically to prevent Streamlit from putting the app to sleep."""
    pass


now_cst = get_now_central()
today_cst = now_cst.date()

# --- STYLING: Dark blue and grey theme (all pages) ---
st.markdown("""
<style>
    /* Dark blue/grey theme – not too dark, wording stands out */
    :root {
        --bg-app: #1e293b;
        --bg-card: #334155;
        --border-subtle: #475569;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --accent: #3b82f6;
        --accent-dark: #2563eb;
        --radius-lg: 18px;
        --shadow-soft: 0 18px 40px rgba(0, 0, 0, 0.25);
    }

    .stApp {
        background: radial-gradient(circle at top, #243447 0, #1e293b 50%, #1a2332 100%);
        color: var(--text-main);
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        font-size: 16px;
    }

    .page-section {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        border: 1px solid var(--border-subtle);
        box-shadow: var(--shadow-soft);
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        color: var(--text-main);
    }

    .section-description {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 0.9rem;
    }

    .winner-box {
        background: linear-gradient(135deg, #14532d, #166534);
        color: #dcfce7;
        padding: 10px 14px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        border: 1px solid #22c55e;
    }
    .loser-box {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        color: #fecaca;
        padding: 10px 14px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        border: 1px solid #f87171;
    }

    .timer-text {
        font-family: "SF Mono", ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        color: #93c5fd;
        font-size: 1.1rem;
        text-align: center;
        background: #1e3a5f;
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid var(--accent);
        margin-bottom: 1.2rem;
    }

    /* Primary action button – blue accent */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border-radius: 999px;
        height: 3.1rem;
        width: 100%;
        border: none;
        font-size: 1.05rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.4);
        transition: transform 0.08s ease-out, box-shadow 0.08s ease-out, filter 0.08s ease-out;
    }
    div.stButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
        box-shadow: 0 18px 40px rgba(59, 130, 246, 0.5);
    }
    div.stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.45);
    }

    /* Strength/Labor clicker buttons – theme blue (no green when selected) */
    div:has(.clicker-wrapper) button,
    .clicker-wrapper ~ div button,
    .clicker-wrapper + * button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: 1px solid var(--accent);
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35) !important;
    }

    .pill-select {
        border-radius: 999px;
        border: 1px solid var(--border-subtle);
        background: #475569;
        padding: 0 0.25rem;
    }
    .pill-select [data-baseweb="select"] {
        border-radius: 999px !important;
        border: none;
        background: transparent;
        min-height: 44px;
        color: var(--text-main);
    }

    /* Grace Day toggle – theme colors (style unchanged, colors match) */
    [data-testid="stToggle"] label {
        color: var(--text-main) !important;
    }
    [data-testid="stToggle"] [role="switch"] {
        background-color: #475569 !important;
    }
    [data-testid="stToggle"] [role="switch"][aria-checked="true"] {
        background-color: var(--accent) !important;
    }

    /* Sidebar – dark blue/grey theme (readable, style unchanged) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #1a2332 100%) !important;
        color: var(--text-main) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: var(--text-main) !important;
    }
    .sidebar-menu [role="radiogroup"] > div[role="radio"] {
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
        color: var(--text-main) !important;
    }
    .sidebar-menu [role="radiogroup"] > div[role="radio"]:hover {
        background: #334155;
    }
    .sidebar-menu [role="radiogroup"] > div[role="radio"][aria-checked="true"] {
        background: #1e3a5f;
        border-left: 3px solid var(--accent);
        font-weight: 600;
        color: white !important;
    }

    /* Tables and general text in Streamlit widgets */
    .stTable, [data-testid="stDataFrame"] {
        color: var(--text-main);
    }
    .stMarkdown, p, label {
        color: var(--text-main);
    }
    /* Points earned / metric value – high contrast (white or light grey) */
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-weight: 700;
    }
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
st.sidebar.markdown("<div class='sidebar-menu'>", unsafe_allow_html=True)
page = st.sidebar.radio("MAIN MENU", ["⚡ LOG WORKOUT", "🏆 MONTHLY STANDINGS", "📊 PROGRESS", "⚙️ SYSTEM ADMIN"])
st.sidebar.markdown("</div>", unsafe_allow_html=True)

keep_alive()

# Data Fetch
res = conn.table("daily_logs").select("*").execute()
df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
if not df.empty: 
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date

# Pauses Data
pauses_res = conn.table("pauses").select("*").execute()
pauses_df = pd.DataFrame(pauses_res.data) if pauses_res.data else pd.DataFrame()
if not pauses_df.empty:
    pauses_df["start_date"] = pd.to_datetime(pauses_df["start_date"]).dt.date
    # end_date can be null; coerce to dates where present
    pauses_df["end_date"] = pd.to_datetime(pauses_df["end_date"], errors="coerce").dt.date

# --- PAGE 1: CHECK-IN ---
if page == "⚡ LOG WORKOUT":
    # HEADER CARD
    midnight_cst = datetime.datetime.combine(
        today_cst + datetime.timedelta(days=1),
        datetime.time(0, 0),
        tzinfo=central_tz,
    )
    time_left = midnight_cst - now_cst
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    header_html = f"""
    <div class="page-section">
        <div class="section-title">Welcome back, {user}</div>
        <div class="section-description">
            Log today&apos;s effort before midnight Central to stay on pace.
        </div>
        <div class="timer-text">
            ⏳ TIME UNTIL DEADLINE: {hours:02d}h {minutes:02d}m {seconds:02d}s
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # MAIN INPUTS (no extra card wrapper)
    today = st.date_input("Entry Date", today_cst)
    is_sun = today.strftime('%A') == 'Sunday'

    # Determine if user has an active pause
    active_pause = None
    if not pauses_df.empty:
        user_pauses = pauses_df[pauses_df["participant_name"] == user]
        for _, row in user_pauses.iterrows():
            start = row["start_date"]
            end = row["end_date"]
            # Active = started by today and not yet ended (no end_date, or end is in the future)
            if start and start <= today_cst and (pd.isna(end) or end is None or end > today_cst):
                # If multiple match, prefer the latest start_date
                if active_pause is None or start > active_pause["start_date"]:
                    active_pause = row

    # Pull any existing entry for the selected date
    user_logs = df[df["participant_name"] == user] if not df.empty else pd.DataFrame()
    today_entry = (
        user_logs[user_logs["log_date"] == today] if not user_logs.empty else pd.DataFrame()
    )

    if active_pause is not None:
        # Show pause status and resume option; no logging controls available
        st.markdown('<div class="page-section">', unsafe_allow_html=True)
        st.subheader("Pact Paused")
        reason_text = active_pause.get("reason", "")
        start_date = active_pause["start_date"]
        st.write(
            f"Your pact has been **paused since {start_date}**. "
            "No missed-day penalties will accrue while paused."
        )
        if reason_text:
            st.markdown(f"**Reason:** {reason_text}")

        if st.button("Resume Pact"):
            try:
                # Update by participant and null end_date so we don't rely on id type (e.g. numpy.int64)
                conn.table("pauses").update(
                    {"end_date": str(today_cst)}
                ).eq("participant_name", user).is_("end_date", "null").execute()
                st.success("Pact resumed. Logging is now re-enabled.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to resume pact: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    elif not today_entry.empty:
        # Day already has an entry: show summary and hide all inputs
        entry = today_entry.iloc[0]
        st.markdown('<div class="page-section">', unsafe_allow_html=True)
        st.subheader("Entry already submitted for this day")
        st.write(f"**Date:** {today}")
        st.write(f"**Points:** {entry['points']}")
        st.write(f"**Type:** {entry['entry_type']}")
        st.info("All entry options are hidden because this day has already been logged.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # No active pause and no existing entry: normal logging UI plus pause controls
        if "show_pause_form" not in st.session_state:
            st.session_state["show_pause_form"] = False

        is_grace_day = st.toggle("Grace Day 🎟️", value=False)

        if is_grace_day:
            points, e_type = 0, "grace"
            st.info("Grace Day selected. Workout inputs are disabled for this entry.")
        else:
            if is_sun:
                u_logs = df[df['participant_name'] == user] if not df.empty else pd.DataFrame()
                month_start = today.replace(day=1)
                used_bonus = len(u_logs[u_logs['entry_type'] == 'sunday_bonus'])
                st.info(f"Sunday Bonus: {used_bonus}/2 used this month.")
                opt = st.radio("Sunday Option:", ["Rest Day (0 pts)", "Bonus Catch-up (+20 pts)"])
                points = 20 if "+20" in opt else 0
                e_type = "sunday_bonus" if points == 20 else "sunday_free"
            else:
                runs = {"None": 0, "10m (5pts)": 5, "15m (10pts)": 10, "20m (15pts)": 15}
                st.markdown("**Run Duration**", unsafe_allow_html=True)
                st.markdown('<div class="pill-select">', unsafe_allow_html=True)
                duration_label = st.selectbox(
                    "",
                    list(runs.keys()),
                    key="run_duration_select",
                )
                st.markdown("</div>", unsafe_allow_html=True)

                if "strength_on" not in st.session_state:
                    st.session_state["strength_on"] = False
                if "labor_on" not in st.session_state:
                    st.session_state["labor_on"] = False

                strength = st.session_state["strength_on"]
                labor = st.session_state["labor_on"]

                cols = st.columns(2)
                with cols[0]:
                    st.markdown(
                        f'<div class="clicker-wrapper strength-{"on" if strength else "off"}">',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "✔ Strength Training (+15)" if strength else "Strength Training (+15)",
                        key="strength_btn",
                    ):
                        st.session_state["strength_on"] = not st.session_state["strength_on"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(
                        f'<div class="clicker-wrapper labor-{"on" if labor else "off"}">',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "✔ Manual Labor/Sports (+10)" if labor else "Manual Labor/Sports (+10)",
                        key="labor_btn",
                    ):
                        st.session_state["labor_on"] = not st.session_state["labor_on"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                points = min(30, runs[duration_label] + (15 if strength else 0) + (10 if labor else 0))
                e_type = "exercise"

        # SUMMARY CARD
        with st.container():
            st.markdown('<div class="page-section">', unsafe_allow_html=True)
            if not is_grace_day or (is_grace_day and not is_sun):
                # Show metric only when we have a defined points variable
                st.metric("Points to be Earned", points)
            if st.button("Submit Entry"):
                try:
                    conn.table("daily_logs").insert(
                        {
                            "participant_name": user,
                            "log_date": str(today),
                            "points": points,
                            "entry_type": e_type,
                        }
                    ).execute()
                    st.success("Entry Secured!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Date already logged or failed to save: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        # PAUSE CONTROLS
        st.markdown('<div class="page-section">', unsafe_allow_html=True)
        st.subheader("Need a break?")
        st.caption("Pause the pact to avoid missed-day penalties while you're away.")

        if not st.session_state["show_pause_form"]:
            if st.button("Pause Pact"):
                st.session_state["show_pause_form"] = True
                st.rerun()
        else:
            pause_start = st.date_input(
                "Pause start date",
                today_cst,
                key="pause_start_date",
            )
            pause_reason = st.text_area(
                "Reason for pause (required)",
                key="pause_reason",
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Confirm Pause"):
                    if not pause_reason.strip():
                        st.error("Please provide a reason for the pause.")
                    else:
                        try:
                            conn.table("pauses").insert(
                                {
                                    "participant_name": user,
                                    "start_date": str(pause_start),
                                    "end_date": None,
                                    "reason": pause_reason.strip(),
                                }
                            ).execute()
                            st.session_state["show_pause_form"] = False
                            st.success("Pact paused. No missed-day penalties will accrue during this pause.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to pause pact: {e}")
            with c2:
                if st.button("Cancel"):
                    st.session_state["show_pause_form"] = False
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE 2: SCOREBOARD ---
elif page == "🏆 MONTHLY STANDINGS":
    st.markdown(
        """
        <div class="page-section">
            <div class="section-title">Monthly Standings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    month_start = today_cst.replace(day=1)

    # Penalty calculation (only for Mon-Sat)
    active_range = [
        d.date()
        for d in pd.date_range(
            start=month_start, end=today_cst - datetime.timedelta(days=1)
        )
        if d.strftime("%A") != "Sunday"
    ]

    summary = []
    for d in ["Damien", "Jesse", "Lyndon", "Todd"]:
        d_logs = df[df['participant_name'] == d] if not df.empty else pd.DataFrame()
        logged_pts = d_logs['points'].sum()
        logged_dates = d_logs['log_date'].tolist() if not d_logs.empty else []
        # Build set of paused days for this participant
        paused_days = set()
        if not pauses_df.empty:
            user_pauses = pauses_df[pauses_df["participant_name"] == d]
            for _, row in user_pauses.iterrows():
                start = row["start_date"]
                if pd.isna(start) or start is None:
                    continue
                end = row["end_date"]
                if pd.isna(end) or end is None:
                    end = today_cst
                for day in pd.date_range(start=start, end=end):
                    paused_days.add(day.date())

        missed_penalty = sum(
            1 for day in active_range if (day not in logged_dates) and (day not in paused_days)
        ) * -15

        # Is this participant currently paused? (same logic as Log Activity page)
        is_paused = False
        if not pauses_df.empty:
            user_pauses = pauses_df[pauses_df["participant_name"] == d]
            for _, row in user_pauses.iterrows():
                start = row["start_date"]
                end = row["end_date"]
                if start and start <= today_cst and (pd.isna(end) or end is None or end > today_cst):
                    is_paused = True
                    break

        summary.append(
            {
                "Dad": d,
                "Logged": logged_pts,
                "Penalty": missed_penalty,
                "Total": logged_pts + missed_penalty,
                "Status": "Paused" if is_paused else "Active",
            }
        )
    
    score_df = pd.DataFrame(summary).sort_values(by="Total", ascending=False).reset_index(drop=True)
    
    st.table(score_df)

    st.markdown(
        f"""
        <div class="winner-box">👑 CURRENT LEADER: {score_df.iloc[0]['Dad'].upper()}</div>
        <div class="loser-box">🤡 CURRENT LOSER: {score_df.iloc[-1]['Dad'].upper()}</div>
        """,
        unsafe_allow_html=True,
    )

# --- PAGE 3: STATS ---
elif page == "📊 PROGRESS":
    st.markdown(
        """
        <div class="page-section">
            <div class="section-title">📈 Pace over the season</div>
            <div class="section-description">
                Track cumulative points over time for each dad to see who is surging and who is slipping.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not df.empty:
        df_sort = df.sort_values('log_date')
        df_sort['Cumulative Points'] = df_sort.groupby('participant_name')['points'].transform(pd.Series.cumsum)
        fig = px.line(
            df_sort,
            x='log_date',
            y='Cumulative Points',
            color='participant_name',
            markers=True,
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 4: ADMIN ---
elif page == "⚙️ SYSTEM ADMIN":
    if user == "Lyndon":
        st.markdown(
            """
            <div class="page-section">
                <div class="section-title">⚙️ Admin controls</div>
                <div class="section-description">
                    Season-wide actions that permanently affect all data. Use only at the start of a new season.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="page-section">
                <div class="section-title">❗ Reset season</div>
                <div class="section-description">
                    This will <strong>irreversibly wipe</strong> all existing daily logs for every participant.
                    Make sure scores are recorded elsewhere before continuing.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("RESET SEASON (WIPE ALL DATA)"):
            conn.table("daily_logs").delete().neq("participant_name", "nobody").execute()
            st.success("Board Reset for the new month!")
