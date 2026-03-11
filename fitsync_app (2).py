import streamlit as st
import json
import os
from datetime import date, timedelta

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FitSync ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── THEME DEFINITIONS ─────────────────────────────────────────────────────────
DARK_THEME = {
    "bg":           "#0a0a0f",
    "bg2":          "#12121a",
    "bg3":          "#1a1a28",
    "border":       "#2a2a40",
    "text":         "#e8e8f0",
    "text2":        "#9090b0",
    "text3":        "#555570",
    "accent":       "#4d7cff",
    "accent2":      "#7b9fff",
    "accent_glow":  "rgba(77,124,255,0.18)",
    "orange":       "#ff6a00",
    "orange2":      "#ff9500",
    "success":      "#00d4aa",
    "danger":       "#ff4466",
    "card_shadow":  "0 4px 24px rgba(0,0,0,0.5)",
    "hero_grad":    "linear-gradient(90deg, #4d7cff, #7b9fff)",
    "btn_grad":     "linear-gradient(90deg, #4d7cff, #7b9fff)",
    "bar_grad":     "linear-gradient(90deg, #4d7cff, #7b9fff)",
    "mode_label":   "☀️ Light Mode",
}

LIGHT_THEME = {
    "bg":           "#f0f4ff",
    "bg2":          "#ffffff",
    "bg3":          "#e8eeff",
    "border":       "#cdd8ff",
    "text":         "#1a1a3a",
    "text2":        "#4a4a7a",
    "text3":        "#9090bb",
    "accent":       "#2a5cff",
    "accent2":      "#5580ff",
    "accent_glow":  "rgba(42,92,255,0.12)",
    "orange":       "#ff6a00",
    "orange2":      "#ff9500",
    "success":      "#00aa88",
    "danger":       "#dd2244",
    "card_shadow":  "0 4px 24px rgba(42,92,255,0.08)",
    "hero_grad":    "linear-gradient(90deg, #2a5cff, #5580ff)",
    "btn_grad":     "linear-gradient(90deg, #2a5cff, #5580ff)",
    "bar_grad":     "linear-gradient(90deg, #2a5cff, #5580ff)",
    "mode_label":   "🌙 Dark Mode",
}

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []   # list of (user, exercise_dict) for undo

T = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    background-color: {T['bg']} !important;
    color: {T['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
#MainMenu, footer, header {{visibility: hidden;}}
.block-container {{padding: 1.5rem 2rem !important;}}

/* ── ALL LABELS visible in both modes ── */
label, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label,
.stSlider label, .stSlider [data-testid="stWidgetLabel"],
p, .stMarkdown p,
div[data-testid="stWidgetLabel"] > div,
div[data-testid="stWidgetLabel"] p {{
    color: {T['text2']} !important;
    opacity: 1 !important;
}}

/* Selectbox selected value text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="ValueContainer"] {{
    color: {T['text']} !important;
}}

/* Slider value + tick labels */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
.stSlider [aria-valuetext] {{
    color: {T['text2']} !important;
}}

/* Number input +/- buttons */
.stNumberInput button {{
    color: {T['text']} !important;
    background: {T['bg3']} !important;
    border-color: {T['border']} !important;
}}

.hero-title {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4.5rem;
    letter-spacing: 8px;
    background: {T['hero_grad']};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    line-height: 1;
    margin-bottom: 0;
}}
.hero-sub {{
    text-align: center;
    color: {T['text3']};
    letter-spacing: 4px;
    font-size: 0.78rem;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}
.card {{
    background: {T['bg2']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: {T['card_shadow']};
}}
.card h3 {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 3px;
    color: {T['text3']};
    margin: 0 0 0.4rem 0;
    text-transform: uppercase;
}}
.big-num {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    color: {T['accent']};
    line-height: 1;
}}
.unit {{ font-size: 0.85rem; color: {T['text3']}; margin-left: 4px; }}
.leader-card {{
    background: {T['bg2']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 1.8rem 1.2rem;
    text-align: center;
    box-shadow: {T['card_shadow']};
}}
.leader-card.winner {{
    border-color: {T['accent']};
    box-shadow: 0 0 40px {T['accent_glow']};
}}
.leader-card .rank   {{ font-family:'Bebas Neue'; font-size:3.5rem; color:{T['accent']}; line-height:1; }}
.leader-card .lname  {{ font-family:'Bebas Neue'; font-size:2rem; letter-spacing:4px; color:{T['text']}; }}
.leader-card .streak {{ font-family:'Bebas Neue'; font-size:2rem; color:{T['orange']}; }}
.leader-card .pts    {{ font-size:0.8rem; color:{T['text3']}; letter-spacing:2px; text-transform:uppercase; }}
.log-entry {{
    background: {T['bg3']};
    border-left: 3px solid {T['accent']};
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}}
.log-entry .log-date {{ color:{T['text3']}; font-size:0.72rem; letter-spacing:1px; }}
.log-entry .log-ex   {{ color:{T['accent2']}; font-weight:700; font-size:1rem; }}
.log-entry .log-det  {{ color:{T['text2']}; font-size:0.85rem; }}
.badge {{
    display:inline-block;
    background:{T['accent_glow']};
    color:{T['accent2']};
    border-radius:6px;
    padding:1px 8px;
    font-size:0.78rem;
    margin-right:4px;
}}
.cal-chip {{
    display:inline-block;
    background: linear-gradient(90deg,{T['orange']},{T['orange2']});
    color:#fff;
    border-radius:20px;
    padding:2px 12px;
    font-size:0.78rem;
    font-weight:700;
    margin-left:6px;
}}
.prog-wrap {{ background:{T['bg3']}; border-radius:20px; height:10px; overflow:hidden; margin:0.4rem 0; }}
.prog-fill {{ height:100%; border-radius:20px; background:{T['bar_grad']}; transition:width 0.6s ease; }}
.divider {{ height:1px; background:linear-gradient(90deg,{T['accent']},transparent); margin:1.2rem 0; border:none; }}
.section-label {{
    font-family:'Bebas Neue',sans-serif;
    letter-spacing:3px;
    color:{T['text3']};
    font-size:0.9rem;
    text-transform:uppercase;
    margin-bottom:0.5rem;
    display:block;
}}
.session-header {{
    background:{T['bg3']};
    border:1px solid {T['border']};
    border-radius:12px;
    padding:0.8rem 1.2rem;
    margin-bottom:0.6rem;
}}
.session-header .sh-date  {{ font-family:'Bebas Neue'; letter-spacing:3px; color:{T['accent']}; font-size:1rem; }}
.session-header .sh-stats {{ color:{T['text3']}; font-size:0.82rem; }}
.weight-badge {{
    display:inline-block;
    background:{T['accent_glow']};
    border:1px solid {T['border']};
    color:{T['accent2']};
    border-radius:20px;
    padding:2px 12px;
    font-size:0.82rem;
    font-weight:600;
    margin:2px;
}}

/* ── THEME TOGGLE — tiny, fixed top-right ── */
.theme-toggle-wrap {{
    position: fixed;
    top: 0.6rem;
    right: 1rem;
    z-index: 9999;
}}
.theme-toggle-wrap .stButton > button {{
    background: {T['bg3']} !important;
    color: {T['text2']} !important;
    border: 1px solid {T['border']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.25rem 0.7rem !important;
    border-radius: 20px !important;
    width: auto !important;
    min-height: unset !important;
    line-height: 1.4 !important;
}}
.theme-toggle-wrap .stButton > button:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
    opacity: 1 !important;
}}

/* ── REMOVE (✕) button — small red inline ── */
.remove-wrap .stButton > button {{
    background: transparent !important;
    border: 1px solid {T['danger']} !important;
    color: {T['danger']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0 !important;
    padding: 0.15rem 0.5rem !important;
    border-radius: 6px !important;
    width: auto !important;
    min-height: unset !important;
    line-height: 1.4 !important;
}}
.remove-wrap .stButton > button:hover {{
    background: {T['danger']} !important;
    color: #fff !important;
    opacity: 1 !important;
}}

/* ── UNDO button — small ghost ── */
.undo-wrap .stButton > button {{
    background: transparent !important;
    border: 1px solid {T['border']} !important;
    color: {T['text2']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.2rem 0.8rem !important;
    border-radius: 8px !important;
    width: auto !important;
    min-height: unset !important;
}}
.undo-wrap .stButton > button:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
    opacity: 1 !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background-color:{T['bg2']} !important;
    border-radius:12px; padding:4px; gap:4px;
    border:1px solid {T['border']};
}}
.stTabs [data-baseweb="tab"] {{
    background-color:transparent !important;
    color:{T['text2']} !important;
    font-family:'Bebas Neue',sans-serif !important;
    letter-spacing:2px !important;
    font-size:0.95rem !important;
    border-radius:8px !important;
    padding:8px 18px !important;
}}
.stTabs [aria-selected="true"] {{
    background:{T['btn_grad']} !important;
    color:#fff !important;
}}
.stButton > button {{
    background:{T['btn_grad']} !important;
    color:white !important;
    font-family:'Bebas Neue',sans-serif !important;
    letter-spacing:3px !important;
    font-size:1rem !important;
    border:none !important;
    border-radius:10px !important;
    padding:0.55rem 1.5rem !important;
    width:100%;
}}
.stButton > button:hover {{ opacity:0.88 !important; }}
.stTextInput input, .stNumberInput input {{
    background-color:{T['bg3']} !important;
    border:1px solid {T['border']} !important;
    color:{T['text']} !important;
    border-radius:10px !important;
}}
div[data-baseweb="select"] > div {{
    background-color:{T['bg3']} !important;
    border:1px solid {T['border']} !important;
    border-radius:10px !important;
}}
ul[data-baseweb="menu"] {{ background-color:{T['bg2']} !important; border:1px solid {T['border']} !important; }}
li[role="option"] {{ color:{T['text']} !important; }}
li[role="option"]:hover {{ background-color:{T['bg3']} !important; }}
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
DATA_FILE = "fitsync_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "Aryan": {"sessions": [], "daily_logs": {}, "weight_log": {}, "target_weight": None},
        "Ved":   {"sessions": [], "daily_logs": {}, "weight_log": {}, "target_weight": None},
    }

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def migrate(d):
    for u in ["Aryan", "Ved"]:
        if "workouts" in d[u] and "sessions" not in d[u]:
            old = d[u].pop("workouts")
            by_date = {}
            for w in old:
                dt = w["date"]
                if dt not in by_date:
                    by_date[dt] = {"date": dt, "exercises": [], "total_calories": 0}
                by_date[dt]["exercises"].append(w)
            d[u]["sessions"] = list(by_date.values())
        for key in ["sessions", "daily_logs", "weight_log"]:
            if key not in d[u]: d[u][key] = {} if key != "sessions" else []
        if "target_weight" not in d[u]: d[u]["target_weight"] = None
    return d

def get_today_session(ud):
    today = str(date.today())
    for s in ud["sessions"]:
        if s["date"] == today:
            return s
    return None

def calc_streak(ud):
    if not ud["sessions"]: return 0
    dates = sorted(set(s["date"] for s in ud["sessions"]), reverse=True)
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    if dates[0] not in [today, yesterday]: return 0
    streak = 0
    check = date.fromisoformat(dates[0])
    for d in dates:
        if str(check) == d:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak

def estimate_cals(sets, reps, weight_kg, rpe, rir, bw=75, ex_type="Compound"):
    vol = sets * reps * weight_kg
    vol_factor = vol * 0.0045
    type_mult = {"Compound": 1.3, "Isolation": 0.85, "Cardio": 1.5, "Bodyweight": 1.0}.get(ex_type, 1.0)
    bw_mult = (bw / 75) ** 0.4
    effort = (rpe / 10) * 0.7 + max(0, (5 - min(rir, 5)) / 5) * 0.3
    effort_mult = 0.6 + effort * 0.8
    base = sets * (3.0 if ex_type == "Compound" else 1.8)
    return round((base + vol_factor) * type_mult * bw_mult * effort_mult, 1)

def get_score(ud):
    s = len(ud["sessions"])
    st2 = calc_streak(ud)
    steps = sum(v.get("steps", 0) for v in ud["daily_logs"].values())
    cals = sum(s2.get("total_calories", 0) for s2 in ud["sessions"])
    return s * 10 + st2 * 5 + int(steps / 1000) + int(cals / 50)

data = migrate(load_data())

# ─── FIXED TOGGLE (top-right corner) ──────────────────────────────────────────
st.markdown('<div class="theme-toggle-wrap">', unsafe_allow_html=True)
if st.button(T["mode_label"], key="theme_toggle"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">FITSYNC ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Aryan & Ved · Train Together · Win Together</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆  LEADERBOARD", "💪  LOG WORKOUT",
    "👟  STEPS & CALS", "⚖️  WEIGHT", "📋  HISTORY"
])

# ── TAB 1: LEADERBOARD ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    a_sc = get_score(data["Aryan"])
    v_sc = get_score(data["Ved"])
    total = max(a_sc + v_sc, 1)

    c1, c2 = st.columns(2)
    for col, name, score in [(c1, "Aryan", a_sc), (c2, "Ved", v_sc)]:
        other = v_sc if name == "Aryan" else a_sc
        win   = score >= other
        medal = "🥇" if win else "🥈"
        wc    = "winner" if win else ""
        streak = calc_streak(data[name])
        nsess  = len(data[name]["sessions"])
        ncal   = sum(s.get("total_calories", 0) for s in data[name]["sessions"])
        with col:
            st.markdown(f"""
            <div class="leader-card {wc}">
                <div class="rank">{medal}</div>
                <div class="lname">{name.upper()}</div>
                <div class="streak">🔥 {streak} DAY STREAK</div>
                <div class="pts">{score} PTS · {nsess} SESSIONS · ~{int(ncal)} KCAL</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ap = int(a_sc / total * 100)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-family:'Bebas Neue';
    letter-spacing:2px;font-size:0.9rem;color:{T['text3']};">
        <span>ARYAN {ap}%</span><span>VED {100-ap}%</span>
    </div>
    <div style="background:{T['bg3']};border-radius:20px;height:16px;overflow:hidden;">
        <div style="height:100%;width:{ap}%;background:{T['bar_grad']};border-radius:20px;"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card"><h3>HOW POINTS WORK</h3>
    <span style="color:{T['text2']};font-size:0.88rem;">
    💪 +10 per session &nbsp;|&nbsp; 🔥 +5 per streak day &nbsp;|&nbsp;
    👟 +1 per 1,000 steps &nbsp;|&nbsp; 🔥 +1 per 50 kcal burned
    </span></div>""", unsafe_allow_html=True)

# ── TAB 2: LOG WORKOUT ─────────────────────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    wu = st.selectbox("WHO'S LOGGING?", ["Aryan", "Ved"], key="wu")
    today_sess = get_today_session(data[wu])
    today_str  = str(date.today())

    # ── Today's session with X buttons ──
    if today_sess and today_sess["exercises"]:
        exs  = today_sess["exercises"]
        tcal = today_sess.get("total_calories", 0)
        st.markdown(f"""
        <div class="session-header">
            <div class="sh-date">TODAY'S SESSION — {wu.upper()}</div>
            <div class="sh-stats">{len(exs)} exercise(s) · ~{tcal:.0f} kcal estimated</div>
        </div>""", unsafe_allow_html=True)

        for i, ex in enumerate(exs):
            rpe_b = f'<span class="badge">RPE {ex["rpe"]}</span>' if ex.get("rpe") else ""
            rir_b = f'<span class="badge">RIR {ex["rir"]}</span>' if ex.get("rir") is not None else ""
            w_s   = f" · {ex['weight']}kg" if ex.get("weight", 0) > 0 else ""
            n_s   = f" · <i>{ex['notes']}</i>" if ex.get("notes") else ""
            c_s   = f'<span class="cal-chip">~{ex.get("calories_est",0):.0f} kcal</span>' if ex.get("calories_est") else ""

            row_left, row_right = st.columns([9, 1])
            with row_left:
                st.markdown(f"""
                <div class="log-entry">
                    <div class="log-ex">{ex['exercise']}{c_s}</div>
                    <div class="log-det">{ex['sets']}×{ex['reps']}{w_s} · {ex.get('ex_type','')}&nbsp;{rpe_b}{rir_b}{n_s}</div>
                </div>""", unsafe_allow_html=True)
            with row_right:
                st.markdown("<div class='remove-wrap' style='margin-top:0.35rem;'>", unsafe_allow_html=True)
                if st.button("✕", key=f"remove_{wu}_{i}", help=f"Remove {ex['exercise']}"):
                    removed = exs.pop(i)
                    today_sess["total_calories"] = round(
                        today_sess.get("total_calories", 0) - removed.get("calories_est", 0), 1
                    )
                    # If session is now empty, remove it entirely
                    if not exs:
                        data[wu]["sessions"] = [s for s in data[wu]["sessions"] if s["date"] != today_str]
                    st.session_state.undo_stack.append((wu, removed))
                    save_data(data)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Undo last removal ──
        st.markdown("<br>", unsafe_allow_html=True)
        undo_col, _ = st.columns([2, 6])
        with undo_col:
            can_undo = len(st.session_state.undo_stack) > 0 and st.session_state.undo_stack[-1][0] == wu
            if can_undo:
                last_name = st.session_state.undo_stack[-1][1]["exercise"]
                st.markdown("<div class='undo-wrap'>", unsafe_allow_html=True)
                if st.button(f"↩ undo: {last_name}", key="undo_btn"):
                    undo_user, undo_entry = st.session_state.undo_stack.pop()
                    sess = get_today_session(data[undo_user])
                    if sess:
                        sess["exercises"].append(undo_entry)
                        sess["total_calories"] = round(sess.get("total_calories", 0) + undo_entry.get("calories_est", 0), 1)
                    else:
                        data[undo_user]["sessions"].append({
                            "date": today_str,
                            "exercises": [undo_entry],
                            "total_calories": undo_entry.get("calories_est", 0),
                        })
                    save_data(data)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="card" style="text-align:center;color:{T['text3']};padding:1rem;">
            No exercises logged today yet — add your first one below! 💪
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'<span class="section-label">ADD EXERCISE TO TODAY\'S SESSION</span>', unsafe_allow_html=True)

    exercise = st.text_input("EXERCISE NAME", placeholder="e.g. Bench Press, Squats, Pull-ups", key="exname")
    ex_type  = st.selectbox("EXERCISE TYPE", ["Compound", "Isolation", "Bodyweight", "Cardio"], key="extype")

    c1, c2, c3 = st.columns(3)
    with c1: sets   = st.number_input("SETS",        min_value=1,   max_value=20,    value=3,   key="sets")
    with c2: reps   = st.number_input("REPS",        min_value=1,   max_value=100,   value=10,  key="reps")
    with c3: weight = st.number_input("WEIGHT (kg)", min_value=0.0, max_value=500.0, value=0.0, step=0.5, key="wt")

    c4, c5 = st.columns(2)
    with c4:
        rpe = st.select_slider("RPE",
              options=[round(x * 0.5, 1) for x in range(2, 21)],
              value=7.0, key="rpe",
              help="Rate of Perceived Exertion: how hard did it feel? (1=very easy, 10=max effort)")
    with c5:
        rir = st.number_input("RIR (Reps in Reserve)",
              min_value=0, max_value=20, value=2, key="rir",
              help="How many more reps could you have done before failure?")

    wlog   = data[wu]["weight_log"]
    bw     = float(list(wlog.values())[-1]) if wlog else 75.0
    cal_est = estimate_cals(sets, reps, weight, rpe, rir, bw, ex_type)

    st.markdown(f"""
    <div style="color:{T['text2']};font-size:0.82rem;margin:-0.2rem 0 0.8rem 0;">
        ⚡ Estimated burn: <strong style="color:{T['orange']};">{cal_est} kcal</strong>
        <span style="font-size:0.75rem;color:{T['text3']};">— volume · RPE {rpe} · RIR {rir} · {ex_type.lower()} · {bw}kg bodyweight</span>
    </div>""", unsafe_allow_html=True)

    notes = st.text_input("NOTES (optional)", placeholder="e.g. PR! / felt tired / increased weight", key="notes")

    if st.button("⚡ ADD TO SESSION"):
        if exercise.strip():
            entry = {
                "exercise": exercise.strip(), "sets": sets, "reps": reps,
                "weight": weight, "rpe": rpe, "rir": rir,
                "ex_type": ex_type, "notes": notes.strip(), "calories_est": cal_est,
            }
            found = False
            for s in data[wu]["sessions"]:
                if s["date"] == today_str:
                    s["exercises"].append(entry)
                    s["total_calories"] = round(s.get("total_calories", 0) + cal_est, 1)
                    found = True
                    break
            if not found:
                data[wu]["sessions"].append({
                    "date": today_str, "exercises": [entry], "total_calories": cal_est
                })
            save_data(data)
            st.success(f"✅ {exercise.strip()} added to today's session!")
            st.rerun()
        else:
            st.error("Please enter an exercise name!")

# ── TAB 3: STEPS & CALS ────────────────────────────────────────────────────────
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1: du = st.selectbox("WHO?", ["Aryan", "Ved"], key="du")
    with c2: dd = st.date_input("DATE", value=date.today(), key="dd")

    ex_log = data[du]["daily_logs"].get(str(dd), {})
    c3, c4 = st.columns(2)
    with c3: steps    = st.number_input("STEPS", min_value=0, max_value=100000,
                                         value=ex_log.get("steps", 0), step=100)
    with c4: ext_cals = st.number_input("EXTRA CALS BURNED (cardio, sport, etc.)",
                                         min_value=0, max_value=10000,
                                         value=ex_log.get("calories", 0), step=10)

    if st.button("💾 SAVE DAILY LOG"):
        data[du]["daily_logs"][str(dd)] = {"steps": steps, "calories": ext_cals}
        save_data(data)
        st.success("✅ Saved!")
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    STEP_GOAL, CAL_GOAL = 10000, 500
    ca, cv = st.columns(2)
    for col, name in [(ca, "Aryan"), (cv, "Ved")]:
        with col:
            tl  = data[name]["daily_logs"].get(str(date.today()), {})
            s   = tl.get("steps", 0)
            ec  = tl.get("calories", 0)
            wc  = sum(ex.get("calories_est", 0)
                      for sess in data[name]["sessions"]
                      if sess["date"] == str(date.today())
                      for ex in sess.get("exercises", []))
            tc  = ec + wc
            sp  = min(int(s / STEP_GOAL * 100), 100)
            cp  = min(int(tc / CAL_GOAL * 100), 100)
            st.markdown(f"""
            <div class="card">
                <h3>{name.upper()} — TODAY</h3>
                <div style="margin-bottom:1rem;">
                    <span style="color:{T['text3']};font-size:0.78rem;letter-spacing:1px;">👟 STEPS</span>
                    <div class="big-num">{s:,}<span class="unit">/ {STEP_GOAL:,}</span></div>
                    <div class="prog-wrap"><div class="prog-fill" style="width:{sp}%;"></div></div>
                </div>
                <div>
                    <span style="color:{T['text3']};font-size:0.78rem;letter-spacing:1px;">🔥 TOTAL CALORIES</span>
                    <div class="big-num">{int(tc)}<span class="unit">/ {CAL_GOAL} kcal</span></div>
                    <div style="color:{T['text3']};font-size:0.75rem;">Workout: ~{int(wc)} kcal · Extra: {ec} kcal</div>
                    <div class="prog-wrap"><div class="prog-fill" style="width:{cp}%;"></div></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ── TAB 4: WEIGHT ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    wu2 = st.selectbox("WHO?", ["Aryan", "Ved"], key="wu2")
    wlog = data[wu2]["weight_log"]
    last_w = float(list(wlog.values())[-1]) if wlog else 70.0
    cur_tgt = data[wu2].get("target_weight")

    c1, c2, c3 = st.columns(3)
    with c1: w_date  = st.date_input("DATE", value=date.today(), key="wdate")
    with c2: w_val   = st.number_input("BODYWEIGHT (kg)", min_value=30.0, max_value=250.0,
                                        value=last_w, step=0.1, key="wval")
    with c3: target  = st.number_input("TARGET WEIGHT (kg)", min_value=30.0, max_value=250.0,
                                        value=float(cur_tgt) if cur_tgt else last_w, step=0.1, key="wtgt")

    if st.button("⚖️ SAVE WEIGHT"):
        data[wu2]["weight_log"][str(w_date)] = w_val
        data[wu2]["target_weight"] = target
        save_data(data)
        st.success(f"✅ {w_val} kg logged for {wu2}!")
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    ca, cv = st.columns(2)
    for col, name in [(ca, "Aryan"), (cv, "Ved")]:
        with col:
            wl  = data[name]["weight_log"]
            tgt = data[name].get("target_weight")
            if wl:
                sd   = sorted(wl.keys())
                lw   = wl[sd[-1]]
                sw   = wl[sd[0]]
                diff = lw - sw
                dc   = T['danger'] if diff > 0 else T['success']
                ds   = f"{'▲' if diff > 0 else '▼'} {abs(diff):.1f} kg since start"
                pp   = min(int(abs(lw - sw) / abs(tgt - sw) * 100), 100) if tgt and tgt != sw else 0
                tgt_html = f"""
                <div style="color:{T['text3']};font-size:0.78rem;margin-top:0.5rem;">🎯 Target: {tgt} kg</div>
                <div class="prog-wrap"><div class="prog-fill" style="width:{pp}%;"></div></div>
                <div style="color:{T['text3']};font-size:0.75rem;">{pp}% to goal</div>
                """ if tgt else ""
                st.markdown(f"""
                <div class="card">
                    <h3>{name.upper()} — WEIGHT</h3>
                    <div class="big-num">{lw}<span class="unit">kg</span></div>
                    <div style="color:{dc};font-size:0.85rem;margin:0.2rem 0;">{ds}</div>
                    {tgt_html}
                </div>""", unsafe_allow_html=True)
                st.markdown(f'<span class="section-label">LAST 7 ENTRIES</span>', unsafe_allow_html=True)
                for d2 in reversed(sd[-7:]):
                    st.markdown(f'<span class="weight-badge">{d2}: {wl[d2]} kg</span>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card" style="text-align:center;color:{T['text3']};">
                    No weight logged yet for {name}.
                </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'<span class="section-label">WEIGHT PROGRESS CHART</span>', unsafe_allow_html=True)

    all_dates = sorted(set(list(data["Aryan"]["weight_log"]) + list(data["Ved"]["weight_log"])))
    if all_dates:
        import pandas as pd
        rows = []
        for d2 in all_dates:
            row = {"Date": d2}
            if d2 in data["Aryan"]["weight_log"]: row["Aryan"] = data["Aryan"]["weight_log"][d2]
            if d2 in data["Ved"]["weight_log"]:   row["Ved"]   = data["Ved"]["weight_log"][d2]
            rows.append(row)
        df = pd.DataFrame(rows).set_index("Date")
        st.line_chart(df, use_container_width=True)
    else:
        st.markdown(f"<span style='color:{T['text3']};font-size:0.88rem;'>Log some weights to see the chart!</span>",
                    unsafe_allow_html=True)

# ── TAB 5: HISTORY ─────────────────────────────────────────────────────────────
with tab5:
    st.markdown("<br>", unsafe_allow_html=True)
    hu = st.selectbox("VIEW HISTORY FOR", ["Aryan", "Ved"], key="hu")

    sessions   = data[hu]["sessions"]
    streak     = calc_streak(data[hu])
    total_cal  = sum(s.get("total_calories", 0) for s in sessions)
    total_steps= sum(v.get("steps", 0) for v in data[hu]["daily_logs"].values())
    total_vol  = sum(ex.get("sets",0)*ex.get("reps",0)*ex.get("weight",0)
                     for s in sessions for ex in s.get("exercises",[]))

    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val, unt in [
        (c1, "STREAK",   f"🔥 {streak}",       "days"),
        (c2, "SESSIONS", len(sessions),          "total"),
        (c3, "KCAL",     f"~{int(total_cal)}",   "burned"),
        (c4, "VOLUME",   f"{int(total_vol):,}",  "kg lifted"),
    ]:
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <h3>{lbl}</h3>
                <div class="big-num" style="font-size:2.2rem;">{val}</div>
                <div style="color:{T['text3']};font-size:0.78rem;">{unt}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'<span class="section-label">ALL SESSIONS — {hu.upper()}</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if sessions:
        for sess in reversed(sessions):
            exs  = sess.get("exercises", [])
            tcal = sess.get("total_calories", 0)
            st.markdown(f"""
            <div class="session-header">
                <div class="sh-date">📅 {sess['date']}</div>
                <div class="sh-stats">{len(exs)} exercises · ~{tcal:.0f} kcal</div>
            </div>""", unsafe_allow_html=True)
            for ex in exs:
                rpe_b = f'<span class="badge">RPE {ex["rpe"]}</span>' if ex.get("rpe") else ""
                rir_b = f'<span class="badge">RIR {ex["rir"]}</span>' if ex.get("rir") is not None else ""
                w_s   = f" · {ex['weight']}kg" if ex.get("weight",0) > 0 else ""
                n_s   = f" · <i>{ex['notes']}</i>" if ex.get("notes") else ""
                c_s   = f'<span class="cal-chip">~{ex.get("calories_est",0):.0f} kcal</span>' if ex.get("calories_est") else ""
                st.markdown(f"""
                <div class="log-entry">
                    <div class="log-ex">{ex['exercise']}{c_s}</div>
                    <div class="log-det">{ex['sets']}×{ex['reps']}{w_s} · {ex.get('ex_type','')}&nbsp;{rpe_b}{rir_b}{n_s}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:{T['text3']};'>No sessions yet. Start grinding! 💪</span>",
                    unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f"<span style='color:{T['text3']};font-size:0.8rem;'>DANGER ZONE</span>", unsafe_allow_html=True)
    if st.button(f"🗑️ CLEAR ALL DATA FOR {hu.upper()}"):
        data[hu] = {"sessions": [], "daily_logs": {}, "weight_log": {}, "target_weight": None}
        save_data(data)
        st.warning(f"All data cleared for {hu}.")
        st.rerun()
