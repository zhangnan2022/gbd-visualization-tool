
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="GBD 可视化助手", layout="wide")
st.title("🌍 GBD 可视化助手")
st.markdown("上传从 IHME 下载的 GBD 数据 CSV 文件，进行交互式可视化。")

uploaded_file = st.file_uploader("📤 上传你的 CSV 文件", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 显示基础信息
    st.success("✅ 数据成功加载！请从下方选择要可视化的内容。")

    # 动态字段选择
    measure = st.selectbox("选择 Measure", sorted(df["measure"].unique()))
    location = st.selectbox("选择 Location", sorted(df["location"].unique()))
    cause = st.selectbox("选择 Cause", sorted(df["cause"].unique()))
    age = st.selectbox("选择 Age", sorted(df["age"].unique()))
    metric = st.selectbox("选择 Metric", sorted(df["metric"].unique()))
    show_ci = st.checkbox("显示上下限 (Confidence Interval)", value=False)

    # 多选 sex 和 year
    sex_options = st.multiselect("选择性别 (Sex)", df["sex"].unique(), default=list(df["sex"].unique()))
    year_range = sorted(df["year"].unique())
    year_selected = st.slider("选择年份范围", min_value=min(year_range), max_value=max(year_range),
                              value=(min(year_range), max(year_range)))

    # 过滤数据
    filtered = df[
        (df["measure"] == measure) &
        (df["location"] == location) &
        (df["cause"] == cause) &
        (df["age"] == age) &
        (df["metric"] == metric) &
        (df["sex"].isin(sex_options)) &
        (df["year"] >= year_selected[0]) & (df["year"] <= year_selected[1])
    ]

    # 图表
    if filtered.empty:
        st.warning("没有找到匹配的数据，请尝试更换筛选条件。")
    else:
        line = alt.Chart(filtered).mark_line(point=True).encode(
            x="year:O",
            y="val:Q",
            color="sex:N",
            tooltip=["year", "sex", "val"]
        ).properties(title="GBD 折线图", width=800, height=400)

        chart = line

        if show_ci:
            band = alt.Chart(filtered).mark_area(opacity=0.2).encode(
                x="year:O",
                y="lower:Q",
                y2="upper:Q",
                color="sex:N"
            )
            chart = band + line

        st.altair_chart(chart, use_container_width=True)
