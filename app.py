import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NoteNest | Your little corner",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).parent / "notenest.db"

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root { --ink:#342842; --muted:#82748e; --pink:#e8a9c7; --purple:#a994df; --lilac:#eee8ff; }
.stApp {
    background:
      radial-gradient(circle at 10% 5%, rgba(246,210,228,.62), transparent 28%),
      radial-gradient(circle at 95% 12%, rgba(207,195,255,.48), transparent 26%),
      linear-gradient(135deg,#fffafd 0%,#f8f5ff 52%,#fff8fb 100%);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1250px; }
h1,h2,h3 { color: var(--ink) !important; font-family: 'Playfair Display', serif !important; }
p, label, .stMarkdown { color: var(--ink); }
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.82);
    border: 1px solid #f0dce9;
    padding: 19px 20px;
    border-radius: 22px;
    box-shadow: 0 8px 25px rgba(94,65,116,.055);
}
div[data-testid="stMetricLabel"] { color:#887792; font-weight:600; }
div[data-testid="stMetricValue"] { color:#5b426d; }
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    border-radius: 13px; border: 1px solid #e5cce2;
    background: linear-gradient(135deg,#fff,#f8efff);
    color: #634876; font-weight: 700; transition: all .2s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    border-color:#c5a5df; color:#4d315e; transform: translateY(-1px);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#f9eaf4 0%,#f1edff 100%);
    border-right: 1px solid #ead9f0;
}
section[data-testid="stSidebar"] * { color:#5b426d; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 12px !important;
}
div[data-testid="stExpander"] {
    background: rgba(255,255,255,.68);
    border: 1px solid #eee0f0;
    border-radius: 16px;
}
div[data-testid="stAlert"] { border-radius: 14px; }
.hero {
    padding: 30px 32px; border-radius: 28px; margin-bottom: 22px;
    background: linear-gradient(115deg,rgba(255,255,255,.96),rgba(255,240,248,.94) 48%,rgba(239,233,255,.95));
    border: 1px solid #f0ddec; box-shadow: 0 14px 38px rgba(102,70,125,.07);
}
.hero-kicker { text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:700; color:#a06e9b; }
.hero-title { font-family:'Playfair Display',serif; font-size:clamp(30px,4vw,44px); line-height:1.12; font-weight:700; color:#3c2d4d; margin:8px 0 10px; }
.hero-sub { font-size:15px; color:#7d6c89; max-width:620px; line-height:1.7; }
.pill { display:inline-block; padding:6px 11px; margin:3px 4px 0 0; border-radius:99px; background:#fff; border:1px solid #efdfef; color:#8b6596; font-size:12px; font-weight:600; }
.soft-card { background:rgba(255,255,255,.78); border:1px solid #f0dfef; border-radius:20px; padding:19px 21px; margin:6px 0 12px; box-shadow:0 7px 22px rgba(90,62,112,.04); }
.small-muted { color:#8b7c94; font-size:13px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:12px 12px 0 0; padding:10px 16px; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
def connect():
    return sqlite3.connect(DB_PATH)

def setup_database():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                content TEXT NOT NULL DEFAULT '',
                pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                day TEXT PRIMARY KEY,
                mood TEXT NOT NULL,
                energy INTEGER NOT NULL,
                journal TEXT NOT NULL DEFAULT ''
            )
        """)

setup_database()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<div style='font-size:34px'>🌷</div><div style='font-family:Playfair Display,serif;font-size:27px;font-weight:700'>NoteNest</div><div style='font-size:12px;color:#92769e;margin:3px 0 20px'>A softer space for busy minds</div>", unsafe_allow_html=True)
    page = st.radio("YOUR SPACE", ["🏡  Home", "📝  My Notes", "🌦️  MoodMap"], label_visibility="visible")
    st.divider()
    st.markdown("**A little reminder**")
    st.caption("You don't have to do everything today. One small step is still progress. ✨")
    st.divider()
    st.caption("🔒 Your notes are stored in a local SQLite database.")

# ---------- DATA HELPERS ----------
def load_notes():
    with connect() as con:
        return pd.read_sql_query("SELECT * FROM notes ORDER BY pinned DESC, updated_at DESC", con)

def load_moods(limit=None):
    query = "SELECT * FROM moods ORDER BY day DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with connect() as con:
        return pd.read_sql_query(query, con)

def hero(kicker, title, subtitle, pills=""):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-kicker">{kicker}</div>
      <div class="hero-title">{title}</div>
      <div class="hero-sub">{subtitle}</div>
      <div style="margin-top:13px">{pills}</div>
    </div>
    """, unsafe_allow_html=True)

today = date.today().isoformat()
notes = load_notes()
moods = load_moods()

# ---------- HOME ----------
if page == "🏡  Home":
    hero("YOUR PERSONAL SPACE  ·  NOTES + WELLBEING",
         "Make room for your thoughts. ✨",
         "A calm little dashboard to collect ideas, organize college notes, and check in with yourself — all in one place.",
         '<span class="pill">📝 Smart notes</span><span class="pill">📌 Pin what matters</span><span class="pill">🌦️ Daily mood</span><span class="pill">📈 Weekly trends</span>')

    c1, c2, c3 = st.columns(3)
    c1.metric("📝 Notes collected", len(notes), help="Your saved notes")
    c2.metric("📌 Pinned notes", int(notes["pinned"].sum()) if not notes.empty else 0)
    c3.metric("🌷 Mood check-ins", len(moods))

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### ✨ Recently saved")
        if notes.empty:
            st.markdown('<div class="soft-card"><b>Your first note starts here</b><br><span class="small-muted">Save a thought, class note, idea, or reminder in My Notes.</span></div>', unsafe_allow_html=True)
        else:
            for _, n in notes.head(4).iterrows():
                pin = "📌 " if n["pinned"] else ""
                st.markdown(f'<div class="soft-card"><b>{pin}{n["title"]}</b><br><span class="small-muted">{n["subject"]} · Updated {str(n["updated_at"])[:10]}</span><br><br>{str(n["content"])[:155]}{"…" if len(str(n["content"]))>155 else ""}</div>', unsafe_allow_html=True)
    with right:
        st.markdown("### 🌷 Today, gently")
        with connect() as con:
            today_mood = con.execute("SELECT mood, energy, journal FROM moods WHERE day=?", (today,)).fetchone()
        if today_mood:
            st.markdown(f'<div class="soft-card"><div style="font-size:28px">💗</div><b>{today_mood[0]}</b><br><span class="small-muted">Energy level: {today_mood[1]}/5</span><br><br>{today_mood[2] or "You checked in with yourself today. That counts."}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="soft-card"><div style="font-size:28px">☁️</div><b>How are you feeling today?</b><br><span class="small-muted">Take a minute to record your mood and energy in MoodMap.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="soft-card"><b>🌱 Tiny goal for today</b><br><span class="small-muted">Write one thing you want to remember, and one thing you appreciate.</span></div>', unsafe_allow_html=True)

    st.markdown("### 🪄 Your quick start")
    q1, q2, q3 = st.columns(3)
    q1.markdown('<div class="soft-card"><b>01 · Capture</b><br><span class="small-muted">Turn a thought into a note before it slips away.</span></div>', unsafe_allow_html=True)
    q2.markdown('<div class="soft-card"><b>02 · Organize</b><br><span class="small-muted">Use subjects, search, and pins to find things fast.</span></div>', unsafe_allow_html=True)
    q3.markdown('<div class="soft-card"><b>03 · Reflect</b><br><span class="small-muted">Track mood and energy without judging the day.</span></div>', unsafe_allow_html=True)

# ---------- NOTES ----------
elif page == "📝  My Notes":
    hero("YOUR IDEAS, SAFELY GATHERED", "A home for every thought. 📝",
         "Create, search, pin, edit, and organize your notes by subject.",
         '<span class="pill">✍️ Create</span><span class="pill">🔎 Search</span><span class="pill">📌 Pin</span><span class="pill">📤 Export CSV</span>')

    with st.expander("＋  Create a new note", expanded=True):
        with st.form("create_note", clear_on_submit=True):
            title = st.text_input("Note title", placeholder="e.g. Python revision — loops & functions")
            subject = st.text_input("Subject / category", value="College", placeholder="College, Personal, Ideas...")
            content = st.text_area("Your note", height=150, placeholder="Start writing here...")
            pinned = st.checkbox("Keep this note pinned 📌")
            save = st.form_submit_button("Save my note ✨", use_container_width=True)
            if save:
                if not title.strip():
                    st.warning("Please add a title before saving.")
                else:
                    now = pd.Timestamp.now().isoformat(timespec="seconds")
                    with connect() as con:
                        con.execute("INSERT INTO notes (title,subject,content,pinned,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                                    (title.strip(), subject.strip() or "General", content.strip(), int(pinned), now, now))
                    st.success("Saved to your NoteNest! 💗")
                    st.rerun()

    st.markdown("### Your collection")
    notes = load_notes()
    search_col, subject_col = st.columns([1.4, 1])
    search = search_col.text_input("🔎 Search notes", placeholder="Search title or content...")
    subject_options = ["All subjects"] + (sorted(notes["subject"].dropna().unique().tolist()) if not notes.empty else [])
    selected_subject = subject_col.selectbox("Filter by subject", subject_options)
    filtered = notes.copy()
    if search:
        match = filtered["title"].str.contains(search, case=False, na=False) | filtered["content"].str.contains(search, case=False, na=False)
        filtered = filtered[match]
    if selected_subject != "All subjects":
        filtered = filtered[filtered["subject"] == selected_subject]
    if not filtered.empty:
        st.download_button("⬇️ Export visible notes as CSV", filtered.to_csv(index=False).encode("utf-8"),
                           "notenest_notes.csv", "text/csv")
        for _, n in filtered.iterrows():
            prefix = "📌 " if n["pinned"] else ""
            with st.expander(f"{prefix}{n['title']}  ·  {n['subject']}"):
                with st.form(f"edit_{int(n['id'])}"):
                    et = st.text_input("Title", value=n["title"])
                    es = st.text_input("Subject", value=n["subject"])
                    ec = st.text_area("Content", value=n["content"], height=140)
                    ep = st.checkbox("Pinned", value=bool(n["pinned"]))
                    a, b = st.columns(2)
                    update = a.form_submit_button("Save changes")
                    delete = b.form_submit_button("Delete note")
                    if update:
                        now = pd.Timestamp.now().isoformat(timespec="seconds")
                        with connect() as con:
                            con.execute("UPDATE notes SET title=?,subject=?,content=?,pinned=?,updated_at=? WHERE id=?",
                                        (et.strip() or "Untitled", es.strip() or "General", ec.strip(), int(ep), now, int(n["id"])))
                        st.success("Your changes are saved.")
                        st.rerun()
                    if delete:
                        with connect() as con:
                            con.execute("DELETE FROM notes WHERE id=?", (int(n["id"]),))
                        st.rerun()
    else:
        st.info("No notes match that search yet. Try another word or create a new note.")

# ---------- MOODMAP ----------
elif page == "🌦️  MoodMap":
    hero("A CHECK-IN, NOT A SCORECARD", "Listen to your day. 🌦️",
         "Record how you feel, notice your energy, and leave a little note for yourself.",
         '<span class="pill">💗 Daily check-in</span><span class="pill">📈 Energy trends</span><span class="pill">🪞 Journal</span>')

    with connect() as con:
        previous = con.execute("SELECT mood,energy,journal FROM moods WHERE day=?", (today,)).fetchone()
    mood_options = ["😊 Happy", "😌 Calm", "🥰 Excited", "😐 Okay", "😴 Tired", "😟 Anxious", "😔 Sad", "😤 Frustrated"]
    mood_index = mood_options.index(previous[0]) if previous and previous[0] in mood_options else 0
    with st.form("daily_checkin"):
        st.markdown("### 💗 Today's check-in")
        mood = st.selectbox("What best describes your mood?", mood_options, index=mood_index)
        energy = st.slider("How much energy do you have?", 1, 5, previous[1] if previous else 3,
                           help="1 = low energy · 5 = lots of energy")
        journal = st.text_area("Anything you'd like to get off your mind?", value=previous[2] if previous else "",
                               height=130, placeholder="A small win, a worry, a thought, or just a few words...")
        submitted = st.form_submit_button("Save today's check-in 💗", use_container_width=True)
        if submitted:
            with connect() as con:
                con.execute("""INSERT INTO moods(day,mood,energy,journal) VALUES(?,?,?,?)
                    ON CONFLICT(day) DO UPDATE SET mood=excluded.mood,energy=excluded.energy,journal=excluded.journal""",
                    (today, mood, energy, journal.strip()))
            st.success("Check-in saved. Thank you for taking a moment for yourself. 🌷")
            st.rerun()

    history = load_moods(7)
    if not history.empty:
        st.markdown("### 📈 Your last 7 check-ins")
        chart_data = history.sort_values("day")
        fig = px.line(chart_data, x="day", y="energy", markers=True,
                      labels={"day": "Date", "energy": "Energy level"},
                      range_y=[0, 5], template="simple_white")
        fig.update_traces(line_color="#a994df", marker_color="#e8a9c7", line_width=3,
                          marker_size=9, fill="tozeroy", fillcolor="rgba(169,148,223,.12)")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.55)",
            margin=dict(l=10,r=10,t=20,b=10), yaxis=dict(dtick=1, gridcolor="#eee5f4"),
            xaxis=dict(gridcolor="#f3eaf5")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 💌 Recent reflections")
        for _, entry in history.iterrows():
            with st.expander(f"{entry['day']}  ·  {entry['mood']}"):
                st.write(f"**Energy:** {entry['energy']}/5")
                st.write(entry["journal"] or "No written reflection saved for this day.")

st.markdown("<div style='text-align:center;color:#a08ba8;font-size:12px;padding:28px 0 4px'>Made with care · NoteNest + MoodMap 🌷</div>", unsafe_allow_html=True)
