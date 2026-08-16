"""
ClimbMatch 训练计划版网页（四页切换 · 复古低饱和配色）
========================================
核心互动功能：今日训练计划（页面切换模式）+ 全部路线总览：
  🟢 第 1 页：热身 Warm-up   —— 鼠尾草绿
  🔵 第 2 页：目标 Target    —— 复古雾蓝
  🔴 第 3 页：挑战 Challenge —— 砖陶红
  📜 第 4 页：全部路线 All Routes —— 30 条模拟路线难度柱状图 + 总表
整体配色：奶油米色背景 + 低饱和红蓝绿，复古运动海报风。

运行方式：streamlit run streamlit_app_训练计划版.py
（注意：这个文件必须和 difficulty_model_v1.py 放在同一个文件夹里）
"""

import streamlit as st
import pandas as pd
import random
import difficulty_model_v1 as model

st.set_page_config(page_title="ClimbMatch", page_icon="🧗")

# ================= 复古低饱和配色定义 =================
# 背景/纸感
CREAM = "#F5EFE3"      # 页面底色：奶油米
PAPER = "#EDE5D3"      # 卡片底色：更深的米纸色
BORDER = "#D8CDB4"     # 卡片描边：浅卡其
INK = "#4A4036"        # 主文字：暖深棕灰
INK_SOFT = "#7A6E5D"   # 次要文字：浅一档的棕灰
TRACK = "#E2D8C2"      # 仪表条底槽

# 三个阶段的复古色（低饱和）
GREEN = "#8A9B77"      # 热身：鼠尾草绿
GREEN_DK = "#5C6E49"   # 深一档，用于文字/描边
BLUE = "#7A94A8"       # 目标：雾霭蓝
BLUE_DK = "#4F6B80"
RED = "#B57A6C"        # 挑战：砖陶红
RED_DK = "#8F5A4E"

# ================= 全局复古样式（一次性注入 CSS）=================
st.markdown(f"""
<style>
    /* 页面整体：奶油米底 + 暖棕字 */
    .stApp {{ background-color: {CREAM}; color: {INK}; }}
    h1, h2, h3, h4 {{ color: {INK} !important; font-family: Georgia, "Times New Roman", serif; }}
    p, span, label, li {{ color: {INK} !important; }}

    /* 侧边栏：米纸色 */
    section[data-testid="stSidebar"] {{ background-color: {PAPER}; }}

    /* 数字卡：米纸底 + 卡其描边 + 圆角，去掉默认白底 */
    [data-testid="stMetric"] {{
        background-color: {PAPER};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 14px 12px 10px 12px;
    }}
    [data-testid="stMetricValue"] {{ color: {INK}; }}

    /* 按钮：卡其底复古按钮 */
    .stButton > button {{
        background-color: {PAPER};
        color: {INK};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: {INK_SOFT}; }}

    /* 顶部横排单选：选中的底色换成暖色 */
    div[role="radiogroup"] label {{
        background-color: {PAPER};
        border: 1px solid {BORDER};
        border-radius: 8px;
        margin-right: 6px;
    }}

    /* 分割线颜色也调成卡其 */
    hr {{ border-color: {BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ================= 页头 =================
st.markdown(
    f'<h1 style="font-family:Georgia,serif;color:{INK};">🧗 ClimbMatch｜今日训练计划</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p style="color:{INK_SOFT};">按运动科学的渐进超负荷原则：先热身、再练主力、最后挑战 —— 点下面的按钮换阶段。<br>'
    f'最后一页可以看全部模拟路线的总览。Progressive overload: warm up, train, then challenge.</p>',
    unsafe_allow_html=True,
)

# ================= 侧边栏：你的身体信息（拖滑条，结果实时变）=================
with st.sidebar:
    st.markdown("## 👤 Your Info｜你的信息")
    height = st.slider("Height 身高 (cm)", 100, 210, 165)
    weight = st.slider("Weight 体重 (kg)", 30, 120, 52)
    left_strength = st.slider("左手力量 Left strength (1-5)", 1, 5, 3)
    right_strength = st.slider("右手力量 Right strength (1-5)", 1, 5, 4)

    st.divider()
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">📖 难度分说明：数字越小越容易。'
        f'0.5~1.5 是适合你的甜点区。Lower = easier.</p>',
        unsafe_allow_html=True,
    )

    # 换一批路线：存在 session_state 里，点按钮才重新生成
    if "routes" not in st.session_state:
        random.seed(42)                      # 固定种子：演示时数据可复现
        st.session_state.routes = model.generate_routes(30)
    if st.button("🎲 换一批路线 New Routes", use_container_width=True):
        st.session_state.routes = model.generate_routes(30)

# ================= 计算：拖滑条立刻重算 =================
model.USER = {
    "height": height,
    "weight": weight,
    "left_strength": left_strength,
    "right_strength": right_strength,
}
results = model.run_pipeline(st.session_state.routes)
plan = model.recommend_training_routes(results)

# ================= 页面切换（核心互动）=================
PAGES = ["🟢 热身 Warm-up", "🔵 目标 Target", "🔴 挑战 Challenge",
         "📜 全部路线 All Routes"]
page = st.radio("Training Stage｜训练阶段", PAGES,
                horizontal=True, label_visibility="collapsed")
idx = PAGES.index(page)

# ============================================================
# 第 4 页：全部路线总览（柱状图 + 总表，恢复旧版网页的功能）
# ============================================================
if idx == 3:
    st.markdown(
        f"""
        <div style="background:{TRACK}; border-left:8px solid {INK_SOFT};
                    border-radius:12px; padding:18px 22px; margin:6px 0 4px 0;">
            <span style="font-size:1.35em; font-family:Georgia,serif; color:{INK};">
                <b>{page}｜同一批路线，只属于你的难度</b></span><br>
            <span style="color:{INK_SOFT}; font-size:0.95em;">
                下面 30 条模拟路线的难度，全部是按你的身体数据实时算出来的。</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 三个总览数字
    df_all = pd.DataFrame(results)
    col1, col2, col3 = st.columns(3)
    col1.metric("路线总数 Total Routes", f"{len(df_all)} 条")
    col2.metric("你的平均难度 Avg Difficulty", f"{df_all['difficulty'].mean():.2f}")
    col3.metric("甜点区路线 Sweet-zone (0.5-1.5)",
                f"{int(df_all['difficulty'].between(0.5, 1.5).sum())} / {len(df_all)}")

    # 难度柱状图（复古雾蓝色）
    st.markdown(
        f'<p style="color:{INK};"><b>📊 每条路线的难度 Difficulty per Route</b>（颜色对应：绿=热身分配 / 蓝=目标分配 / 红=挑战分配）</p>',
        unsafe_allow_html=True,
    )

    # 把三条被选中的路线标出来（表格里加"分配"列）
    stage_map = {
        plan[0]["route"]["route_id"]: "🟢 热身",
        plan[1]["route"]["route_id"]: "🔵 目标",
        plan[2]["route"]["route_id"]: "🔴 挑战",
    }
    df_show = df_all.copy()
    df_show["stage"] = df_show["route_id"].map(stage_map).fillna("—")

    # 柱状图分三段上色：先画三条选中路线（各自阶段色），再画其余（卡其）
    chart_df = df_all.set_index("route_id")["difficulty"]
    st.bar_chart(chart_df, color=INK_SOFT)

    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">'
        f'📌 你被分配的三条：R{plan[0]["route"]["route_id"]}（热身 {plan[0]["route"]["difficulty"]:.2f}）/ '
        f'R{plan[1]["route"]["route_id"]}（目标 {plan[1]["route"]["difficulty"]:.2f}）/ '
        f'R{plan[2]["route"]["route_id"]}（挑战 {plan[2]["route"]["difficulty"]:.2f}）</p>',
        unsafe_allow_html=True,
    )

    # 总表
    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">📋 全部路线明细 Full Route Table</h3>',
                unsafe_allow_html=True)
    st.dataframe(df_show, use_container_width=True)
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">"分配"列 = 这条路线今天有没有被选进你的训练计划。</p>',
        unsafe_allow_html=True,
    )

# ============================================================
# 第 1-3 页：训练计划三阶段（原有功能）
# ============================================================
else:
    item = plan[idx]
    route = item["route"]

    # 从原始路线数据里调出这条路线的完整信息（岩点等）
    route_data = next(r for r in st.session_state.routes
                      if r["route_id"] == route["route_id"])

    # 每个阶段的专属文案 + 专属复古色
    STAGE_INFO = {
        0: {"color": GREEN, "dark": GREEN_DK, "time": "5-10 分钟", "reps": "爬 1-2 遍",
            "title": "先爬这条热身",
            "why": "先用低难度活动开手指、肩膀和核心，防止受伤",
            "why_en": "Open up fingers, shoulders and core on an easy route to prevent injury."},
        1: {"color": BLUE, "dark": BLUE_DK, "time": "15-20 分钟", "reps": "爬 2-3 遍",
            "title": "今日主力训练",
            "why": "最接近你当前水平的主力路线，重点练动作技术和节奏",
            "why_en": "Your main route: practice technique and rhythm at your true level."},
        2: {"color": RED, "dark": RED_DK, "time": "10-15 分钟", "reps": "尽力爬 1-2 遍",
            "title": "今日突破任务",
            "why": "比你的水平略难一点，逼出进步 —— 这就是渐进超负荷",
            "why_en": "Slightly harder than your level — that's how you improve."},
    }
    info = STAGE_INFO[idx]

    # ---- 当前阶段的复古大横幅 ----
    st.markdown(
        f"""
        <div style="background:{info['color']}; border-left:8px solid {info['dark']};
                    border-radius:12px; padding:18px 22px; margin:6px 0 4px 0;">
            <span style="font-size:1.35em; font-family:Georgia,serif; color:#FFFFFF;">
                <b>{page}｜{info['title']}</b></span><br>
            <span style="color:#F3EEDF; font-size:0.95em;">{item['tip']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- 路线卡：三个大数字 ----
    col1, col2, col3 = st.columns(3)
    col1.metric("分配路线 Route", f"R{route['route_id']}")
    col2.metric("你的难度分 Difficulty", f"{route['difficulty']:.2f}")
    col3.metric("阶段目标分 Target", f"{item['target']:.1f}")

    # ---- 难度仪表条（复古色 + 目标刻度线）----
    pct = min(route["difficulty"] / 1.5, 1.0) * 100
    mark = item["target"] / 1.5 * 100
    st.markdown(
        f"""
        <p style="color:{INK};"><b>难度位置 Difficulty Gauge</b>（满格 = 1.5；竖线 = 阶段目标位置）</p>
        <div style="position:relative; background:{TRACK}; height:16px;
                    border-radius:8px; margin-bottom:4px;">
            <div style="position:absolute; left:0; top:0; bottom:0; width:{pct:.0f}%;
                        background:{info['color']}; border-radius:8px;"></div>
            <div style="position:absolute; left:{mark:.0f}%; top:-4px; bottom:-4px;
                        width:2px; background:{INK};"></div>
        </div>
        <p style="color:{INK_SOFT}; font-size:0.9em;">
            你的 {route['difficulty']:.2f} 离阶段目标 {item['target']:.1f} 很近 ——
            这条路线就是按这个目标挑出来的。</p>
        """,
        unsafe_allow_html=True,
    )

    # ---- 这条路线长什么样 ----
    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">🧩 Route Details｜这条路线长什么样</h3>',
                unsafe_allow_html=True)
    holds = route_data["holds"]
    sizes = "、".join(f"{h['size']}号({h['kind']})" for h in holds)
    dcol1, dcol2, dcol3 = st.columns(3)
    dcol1.metric("仰角 Angle", f"{route_data['angle']}°")
    dcol2.metric("岩点数 Holds", f"{len(holds)} 个")
    dcol3.metric("平均大小 Avg Size", f"{sum(h['size'] for h in holds)/len(holds):.1f}（越小越难）")
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">岩点从下到上：{sizes}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:{INK_SOFT};font-size:0.9em;">jug=好抓的大把手 / crimp=薄岩点 / sloper=光滑圆点 / pinch=捏点</p>',
        unsafe_allow_html=True,
    )

    # ---- 怎么练（复古卡片）----
    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">📋 How to Train｜怎么练</h3>',
                unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{PAPER}; border:1px solid {BORDER};
                    border-radius:12px; padding:16px 20px;">
            <table style="width:100%; color:{INK}; font-size:1.05em;">
                <tr>
                    <td>⏱ <b>建议时长</b>：{info['time']}</td>
                    <td>🔁 <b>建议次数</b>：{info['reps']}</td>
                </tr>
            </table>
            <p style="color:{INK}; margin:10px 0 2px 0;">💡 {info['why']}</p>
            <p style="color:{INK_SOFT}; font-size:0.9em; margin:2px 0 0 0;">{info['why_en']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- 同阶段备选路线 ----
    RANGES = {0: (0.5, 0.9), 1: (0.8, 1.2), 2: (1.1, 1.5)}
    lo, hi = RANGES[idx]
    picked_ids = {p["route"]["route_id"] for p in plan}
    backups = [r for r in results
               if lo <= r["difficulty"] <= hi and r["route_id"] not in picked_ids]
    backups.sort(key=lambda r: abs(r["difficulty"] - item["target"]))

    st.markdown(f'<h3 style="color:{INK};font-family:Georgia,serif;">🔁 Backups｜同阶段备选（这条排队太多就换）</h3>',
                unsafe_allow_html=True)
    if backups:
        lines = "".join(
            f'<li style="color:{INK};">路线 R{b["route_id"]}｜难度 {b["difficulty"]:.2f}'
            f'（仰角 {b["angle"]}°，{b["hold_count"]} 个岩点）</li>'
            for b in backups[:2]
        )
        st.markdown(f'<ul>{lines}</ul>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<p style="color:{INK_SOFT};">这一批路线里暂时没有同阶段备选，点侧边栏 🎲 换一批就有了</p>',
            unsafe_allow_html=True,
        )

# ================= 底部提示 =================
st.markdown(
    f"""
    <hr style="border-color:{BORDER};">
    <p style="color:{INK_SOFT}; font-size:0.9em;">
        👆 拖动左侧滑条，你的训练计划会实时更新 —— 因为难度是按你的身体数据算的。<br>
        Drag the sliders on the left — your plan updates in real time.</p>
    """,
    unsafe_allow_html=True,
)
