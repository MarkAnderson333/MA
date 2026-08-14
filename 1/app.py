import difficulty_model_v1 as model
import streamlit as st
import pandas as pd
import altair as alt

st.title("Climbing Route Difficulty Evaluator ｜ 攀岩路线难度评估系统")

st.subheader("Enter Climber Information ｜ 输入攀爬者身体信息")
height = st.number_input("Height (cm) 身高（厘米）", min_value=100, max_value=230, value=165)
weight = st.number_input("Weight (kg) 体重（千克）", min_value=30, max_value=150, value=52)

left_strength = st.slider("Left-hand Strength (1-5) 左手力量（1-5）", 1, 5, 3)
right_strength = st.slider("Right-hand Strength (1-5) 右手力量（1-5）", 1, 5, 4)

# ========== 统一放在一起的力量等级说明表格 Tips ==========
st.caption("Strength Rating Reference Table ｜ 手部力量等级参考说明")
strength_table = pd.DataFrame([
    {"Score":1,
     "Description (English)":"Cannot do a single pull‑up; hands tire quickly when gripping",
     "描述（中文）":"引体向上一个都拉不起来，抓东西手会酸"},
    {"Score":2,
     "Description (English)":"Can do 1‑2 pull‑ups; carrying everyday items feels difficult",
     "描述（中文）":"能拉 1~2 个引体，日常提东西有点吃力"},
    {"Score":3,
     "Description (English)":"Can do 3‑5 pull‑ups; can lift 5 kg with one hand easily",
     "描述（中文）":"能拉 3~5 个引体，单手提 5kg 没问题"},
    {"Score":4,
     "Description (English)":"Can do 6‑10 pull‑ups; can carry a full bucket of water with one hand",
     "描述（中文）":"能拉 6~10 个引体，单手能拎一桶水"},
    {"Score":5,
     "Description (English)":"Can comfortably do more than 10 pull‑ups; rarely loses arm‑wrestling",
     "描述（中文）":"引体随便拉 10 个以上，掰手腕很少输"},
])
st.dataframe(strength_table, hide_index=True, use_container_width=True)
# =========================================================

route_num = st.number_input("Number of Generated Routes 生成路线数量", min_value=1, max_value=500, value=30)

st.caption("难度分说明：数字越小越容易；0.5~1.5 是适合你的甜点区（有挑战但能完成）。体重会通过'力量体重比'影响难度：同样力量下，越重难度越高。")

# 红色运行按钮
run_clicked = st.button("Run ｜ 运行", type="primary")

if run_clicked:
    model.USER = {
        "height": height,
        "weight": weight,
        "left_strength": left_strength,
        "right_strength": right_strength,
    }
    results = model.run_pipeline(model.generate_routes(route_num))

    st.success(f"Model finished. Evaluated {len(results)} routes. ｜ 模型运行完成，共评估 {len(results)} 条路线。")

    df = pd.DataFrame(results)
    # 重置 route_id，从 1 开始连续编号，表格和图表编号完全一致
    df["route_id"] = range(0, len(df))

    # 难度分布图：X轴标题、刻度水平；Y轴标题竖直排列
    chart = alt.Chart(df).mark_bar(color="#64b5f6").encode(
        x=alt.X(
            "route_id:O",
            title="Route ID ｜ 路线编号",
            axis=alt.Axis(labelAngle=0, titleAngle=0)
        ),
        y=alt.Y(
            "difficulty:Q",
            title="Difficulty Score ｜ 难度分数",
            axis=alt.Axis(titleAngle=-90)
        )
    ).properties(
        title="Route Difficulty Distribution ｜ 路线难度分布",
        width=700,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

    # 全部结果表格
    st.subheader("All Routes ｜ 全部路线难度")
    st.dataframe(df)

    # 推荐功能：挑出最适合的 3 条
    st.subheader("Recommended 3 Routes for You ｜ 推荐给你的 3 条路线")
    recs = model.recommend_routes(results)
    st.dataframe(pd.DataFrame(recs))

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download Result CSV File ｜ 下载结果CSV文件",
        data=csv_data,
        file_name="difficulty_results.csv",
        mime="text/csv",
    )