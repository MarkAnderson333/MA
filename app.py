"""
ClimbMatch Training Plan App (4 pages · retro low-saturation colors)
=================================================================
All interface text is in plain, friendly English (no jargon).
  Page 1: Warm-up  (sage green)
  Page 2: Target   (misty blue)
  Page 3: Challenge(brick red)
  Page 4: All Routes (30 simulated routes bar chart + table)

Run: streamlit run streamlit_app_训练计划版.py
(Keep this file in the same folder as difficulty_model_v1.py)
"""

import streamlit as st
import pandas as pd
import random
import difficulty_model_v1 as model

st.set_page_config(page_title="ClimbFit", page_icon="🧗")

# ================= retro colors =================
CREAM = "#F5EFE3"      # page background: cream
PAPER = "#EDE5D3"      # card background: darker paper
BORDER = "#D8CDB4"     # card border: khaki
INK = "#4A4036"        # main text: warm dark brown
INK_SOFT = "#7A6E5D"   # secondary text
TRACK = "#E2D8C2"      # gauge track

GREEN = "#8A9B77"      # warm-up: sage green
GREEN_DK = "#5C6E49"
BLUE = "#7A94A8"       # target: misty blue
BLUE_DK = "#4F6B80"
RED = "#B57A6C"        # challenge: brick red
RED_DK = "#8F5A4E"

# ================= global retro styles =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {CREAM}; color: {INK}; }}
    h1, h2, h3, h4 {{ color: {INK} !important; font-family: Georgia, "Times New Roman", serif; }}
    p, span, label, li {{ color: {INK} !important; }}

    section[data-testid="stSidebar"] {{ background-color: {PAPER}; }}

    [data-testid="stMetric"] {{
        background-color: {PAPER};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 14px 12px 10px 12px;
    }}
    [data-testid="stMetricValue"] {{ color: {INK}; }}

    .stButton > button {{
        background-color: {PAPER};
        color: {INK};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: {INK_SOFT}; }}

    div[role="radiogroup"] label {{
        background-color: {PAPER};
        border: 1px solid {BORDER};
        border-radius: 8px;
        margin-right: 6px;
    }}

    hr {{ border-color: {BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ================= header =================
st.markdown(
    f'<h1 style="font-family:Georgia,serif;color:{INK};">🧗 ClimbMatch | Today\'s Training Plan</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p style="color:{INK_SOFT};">Easy first, then your main route, then a challenge '
    f'— that is how progress happens. Pick a stage below.<br>'
    f'The last page shows all simulated routes.</p>',
    unsafe_allow_html=True,
)

# ================= sidebar: your info =================
with st.sidebar:
    st.markdown("## 👤 Your Info")
    height = st.slider("Height (cm)", 100, 210, 165)
    weight = st.slider("Weight (kg)", 30, 120, 52)
    left_strength = st.slider("Left strength (1-5)", 1, 5, 3)
    right_strength = st.slider("Right strength (1-5)", 1, 5, 4)

    st.divider()
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">📖 Lower score = easier. '
        f'0.5~1.5 is your sweet spot.</p>',
        unsafe_allow_html=True,
    )

    if "routes" not in st.session_state:
        random.seed(42)                      # fixed seed: reproducible demo
        st.session_state.routes = model.generate_routes(30)
    if st.button("🎲 New Routes", use_container_width=True):
        st.session_state.routes = model.generate_routes(30)

# ================= compute: sliders recalc instantly =================
model.USER = {
    "height": height,
    "weight": weight,
    "left_strength": left_strength,
    "right_strength": right_strength,
}
results = model.run_pipeline(st.session_state.routes)
plan = model.recommend_training_routes(results)

# ================= page switcher =================
PAGES = ["🟢 Warm-up", "🔵 Target", "🔴 Challenge",
         "📜 All Routes"]
page = st.radio("Training Stage", PAGES,
                horizontal=True, label_visibility="collapsed")
idx = PAGES.index(page)

# ============================================================
# Page 4: all routes overview
# ============================================================
if idx == 3:
    st.markdown(
        f"""
        <div style="background:{TRACK}; border-left:8px solid {INK_SOFT};
                    border-radius:12px; padding:18px 22px; margin:6px 0 4px 0;">
            <span style="font-size:1.35em; font-family:Georgia,serif; color:{INK};">
                <b>{page} | Same routes, scored just for you</b></span><br>
            <span style="color:{INK_SOFT}; font-size:0.95em;">
                All 30 simulated routes below are scored in real time from your body data.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_all = pd.DataFrame(results)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Routes", f"{len(df_all)}")
    col2.metric("Avg Difficulty", f"{df_all['difficulty'].mean():.2f}")
    col3.metric("Sweet-spot Routes (0.5-1.5)",
                f"{int(df_all['difficulty'].between(0.5, 1.5).sum())} / {len(df_all)}")

    st.markdown(
        f'<p style="color:{INK};"><b>📊 Difficulty per Route</b>'
        f' (green = warm-up pick, blue = target, red = challenge)</p>',
        unsafe_allow_html=True,
    )

    stage_map = {
        plan[0]["route"]["route_id"]: "🟢 Warm-up",
        plan[1]["route"]["route_id"]: "🔵 Target",
        plan[2]["route"]["route_id"]: "🔴 Challenge",
    }
    df_show = df_all.copy()
    df_show["stage"] = df_show["route_id"].map(stage_map).fillna("—")
    df_show = df_show.rename(columns={"stage": "picked"})

    chart_df = df_all.set_index("route_id")["difficulty"]
    st.bar_chart(chart_df, color=INK_SOFT)

    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">'
        f'📌 Today\'s picks: R{plan[0]["route"]["route_id"]} (warm-up '
        f'{plan[0]["route"]["difficulty"]:.2f}) / '
        f'R{plan[1]["route"]["route_id"]} (target '
        f'{plan[1]["route"]["difficulty"]:.2f}) / '
        f'R{plan[2]["route"]["route_id"]} (challenge '
        f'{plan[2]["route"]["difficulty"]:.2f})</p>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">📋 Full Route Table</h3>',
                unsafe_allow_html=True)
    st.dataframe(df_show, use_container_width=True)
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">'
        f'The "picked" column shows which routes were chosen for today\'s plan.</p>',
        unsafe_allow_html=True,
    )

# ============================================================
# Pages 1-3: three training stages
# ============================================================
else:
    item = plan[idx]
    route = item["route"]

    route_data = next(r for r in st.session_state.routes
                      if r["route_id"] == route["route_id"])

    STAGE_INFO = {
        0: {"color": GREEN, "dark": GREEN_DK, "time": "5-10 min", "reps": "1-2 laps",
            "title": "Warm up on this one",
            "why": "Easy route first — open up fingers, shoulders and core to stay safe."},
        1: {"color": BLUE, "dark": BLUE_DK, "time": "15-20 min", "reps": "2-3 laps",
            "title": "Today's main set",
            "why": "The route closest to your level — practice technique and rhythm."},
        2: {"color": RED, "dark": RED_DK, "time": "10-15 min", "reps": "Try 1-2 times",
            "title": "Today's challenge",
            "why": "A bit harder than your level — that's how you improve."},
    }
    info = STAGE_INFO[idx]

    # friendly English tip (overrides the Chinese tip from the model file)
    TIP_EN = {
        0: "Start here — open up your body first.",
        1: "Your main route — give it your focus.",
        2: "A bit harder — this is where progress lives.",
    }

    st.markdown(
        f"""
        <div style="background:{info['color']}; border-left:8px solid {info['dark']};
                    border-radius:12px; padding:18px 22px; margin:6px 0 4px 0;">
            <span style="font-size:1.35em; font-family:Georgia,serif; color:#FFFFFF;">
                <b>{page} | {info['title']}</b></span><br>
            <span style="color:#F3EEDF; font-size:0.95em;">{TIP_EN[idx]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Assigned Route", f"R{route['route_id']}")
    col2.metric("Your Difficulty", f"{route['difficulty']:.2f}")
    col3.metric("Target", f"{item['target']:.1f}")

    pct = min(route["difficulty"] / 1.5, 1.0) * 100
    mark = item["target"] / 1.5 * 100
    st.markdown(
        f"""
        <p style="color:{INK};"><b>Difficulty Gauge</b> (full = 1.5; line = your target)</p>
        <div style="position:relative; background:{TRACK}; height:16px;
                    border-radius:8px; margin-bottom:4px;">
            <div style="position:absolute; left:0; top:0; bottom:0; width:{pct:.0f}%;
                        background:{info['color']}; border-radius:8px;"></div>
            <div style="position:absolute; left:{mark:.0f}%; top:-4px; bottom:-4px;
                        width:2px; background:{INK};"></div>
        </div>
        <p style="color:{INK_SOFT}; font-size:0.9em;">
            Your {route['difficulty']:.2f} is close to the target of {item['target']:.1f}
            — that's why we picked it.</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">🧩 Route Details</h3>',
                unsafe_allow_html=True)
    holds = route_data["holds"]
    sizes = "、".join(f"{h['kind']} (size {h['size']})" for h in holds)
    dcol1, dcol2, dcol3 = st.columns(3)
    dcol1.metric("Angle", f"{route_data['angle']}°")
    dcol2.metric("Holds", f"{len(holds)}")
    dcol3.metric("Avg Size", f"{sum(h['size'] for h in holds)/len(holds):.1f} ")
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">Holds from bottom to top: {sizes}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">'
        f'jug = big & comfy / crimp = tiny edge / sloper = smooth & round / pinch = pinch grip</p>',
        unsafe_allow_html=True,
    )

    # ---- hold feedback ----
    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">🧗 Hold Feedback</h3>',
                unsafe_allow_html=True)
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">'
        f'Climbed it? Mark how each hold felt — we\'ll remember your weak spots.</p>',
        unsafe_allow_html=True,
    )

    KIND_EN = {"jug": "big & comfy", "crimp": "tiny edge",
               "sloper": "smooth & round", "pinch": "pinch grip"}
    FEED_LABEL = {"easy": "Easy", "ok": "OK", "hard": "Hard"}
    FEED_COLOR = {"easy": GREEN_DK, "ok": "#A08A4F", "hard": RED_DK}

    for i, h in enumerate(holds):
        fb_key = f"fb_{route['route_id']}_{i}"
        state = st.session_state.get(fb_key, None)
        fcol1, fcol2, fcol3, fcol4 = st.columns([3, 1, 1, 1])
        status_txt = FEED_LABEL[state] if state else "Not yet"
        status_col = FEED_COLOR[state] if state else INK_SOFT
        fcol1.markdown(
            f'<span style="color:{INK};"><b>Hold {i + 1}</b> | {h["kind"]}'
            f' ({KIND_EN[h["kind"]]})</span><br>'
            f'<span style="color:{status_col};font-size:0.85em;">Marked: {status_txt}</span>',
            unsafe_allow_html=True,
        )
        if fcol2.button("👍 Easy", key=f"{fb_key}_easy", use_container_width=True):
            st.session_state[fb_key] = "easy"
        if fcol3.button("👌 OK", key=f"{fb_key}_ok", use_container_width=True):
            st.session_state[fb_key] = "ok"
        if fcol4.button("💪 Hard", key=f"{fb_key}_hard", use_container_width=True):
            st.session_state[fb_key] = "hard"

    # summary: weakest hold type
    hard_count = {}
    marked_count = 0
    for i, h in enumerate(holds):
        stt = st.session_state.get(f"fb_{route['route_id']}_{i}", None)
        if stt:
            marked_count += 1
            if stt == "hard":
                hard_count[h["kind"]] = hard_count.get(h["kind"], 0) + 1

    if marked_count == 0:
        st.markdown(
            f'<p style="color:{INK_SOFT};font-size:0.9em;">'
            f'💡 Mark a few holds — your weakest hold type shows up here.</p>',
            unsafe_allow_html=True,
        )
    elif hard_count:
        weakest = max(hard_count, key=hard_count.get)
        st.markdown(
            f'<div style="background:{PAPER};border:1px solid {BORDER};border-radius:10px;'
            f'padding:12px 16px;margin-top:6px;">'
            f'<span style="color:{RED_DK};"><b>💡 Your weak spot: {weakest}</b>'
            f' ({KIND_EN[weakest]})</span><br>'
            f'<span style="color:{INK_SOFT};font-size:0.9em;">'
            f'You marked {sum(hard_count.values())} hold(s) as hard — '
            f'{weakest} most often. Practice those and you\'ll improve faster.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:{PAPER};border:1px solid {BORDER};border-radius:10px;'
            f'padding:12px 16px;margin-top:6px;">'
            f'<span style="color:{GREEN_DK};"><b>💪 No hard holds marked</b></span><br>'
            f'<span style="color:{INK_SOFT};font-size:0.9em;">'
            f'This route felt fine for you — go for it.</span></div>',
            unsafe_allow_html=True,
        )

    # ---- how to train ----
    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">📋 How to Train</h3>',
                unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{PAPER}; border:1px solid {BORDER};
                    border-radius:12px; padding:16px 20px;">
            <table style="width:100%; color:{INK}; font-size:1.05em;">
                <tr>
                    <td>⏱ <b>Time</b>: {info['time']}</td>
                    <td>🔁 <b>Sets</b>: {info['reps']}</td>
                </tr>
            </table>
            <p style="color:{INK}; margin:10px 0 2px 0;">💡 {info['why']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- backups ----
    RANGES = {0: (0.5, 0.9), 1: (0.8, 1.2), 2: (1.1, 1.5)}
    lo, hi = RANGES[idx]
    picked_ids = {p["route"]["route_id"] for p in plan}
    backups = [r for r in results
               if lo <= r["difficulty"] <= hi and r["route_id"] not in picked_ids]
    backups.sort(key=lambda r: abs(r["difficulty"] - item["target"]))

    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">🔁 Backups（pick one if this route is crowded）</h3>',
                unsafe_allow_html=True)
    if backups:
        backup_lines = []
        for b in backups[:2]:
            bdata = next(r for r in st.session_state.routes
                         if r["route_id"] == b["route_id"])
            holds_b = bdata["holds"]
            sizes_b = "、".join(f"{h['kind']} (size {h['size']})" for h in holds_b)
            backup_lines.append(
                f'<li style="color:{INK};">Route R{b["route_id"]} | difficulty {b["difficulty"]:.2f}'
                f' (angle {b["angle"]}°, {b["hold_count"]} holds)<br>'
                f'<span style="color:{INK_SOFT};font-size:0.9em;">'
                f'Holds from bottom to top: {sizes_b}</span></li>'
            )
        st.markdown(f'<ul>{"".join(backup_lines)}</ul>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<p style="color:{INK_SOFT};">No backup in this batch yet — '
            f'hit 🎲 New Routes for a fresh set.</p>',
            unsafe_allow_html=True,
        )

# ================= footer =================
st.markdown(
    f"""
    <hr style="border-color:{BORDER};">
    <p style="color:{INK_SOFT}; font-size:0.9em;">
        👆 Drag the sliders — your plan updates instantly, because difficulty
        is scored from your body data.</p>
    """,
    unsafe_allow_html=True,
)
