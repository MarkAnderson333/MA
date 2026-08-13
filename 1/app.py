import difficulty_model_v1 as model
import streamlit as st
import pandas as pd

st.title("Climbing Route Difficulty Evaluator ｜ 攀岩路线难度评估系统")

st.subheader("Enter Climber Information ｜ 输入攀爬者身体信息")
height = st.number_input("Height (cm) 身高（厘米）", min_value=100, max_value=230, value=165)
weight = st.number_input("Weight (kg) 体重（千克）", min_value=30, max_value=150, value=52)
left_strength = st.slider("Left‑hand Strength (1‑5) 左手力量（1‑5）", 1, 5, 3)
right_strength = st.slider("Right‑hand Strength (1‑5) 右手力量（1‑5）", 1, 5, 4)
route_num = st.number_input("Number of Random Routes 随机路线数量", min_value=1, max_value=500, value=30)

if st.button("Run Difficulty Model ｜ 运行难度模型"):
    model.USER = {
        "height": height,
        "weight": weight,
        "left_strength": left_strength,
        "right_strength": right_strength
    }
    results = model.run_pipeline(model.generate_routes(route_num))

    st.success(f"Model finished. Evaluated {len(results)} routes. ｜ 模型运行完成，共评估 {len(results)} 条路线。")
    df = pd.DataFrame(results)
    st.dataframe(df)

    csv_data = df.to_csv(index=False).encode("utf‑8‑sig")
    st.download_button(
        label="Download Result CSV File ｜ 下载结果CSV文件",
        data=csv_data,
        file_name="difficulty_results.csv",
        mime="text/csv"
    )