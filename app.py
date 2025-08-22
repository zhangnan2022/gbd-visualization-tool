
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="GBD 可视化助手", layout="wide")
st.title("🌍 GBD 可视化助手（内侧）——zhangnan")
st.markdown("上传从 IHME 下载的 GBD 数据 CSV 文件，进行交互式可视化。")

uploaded_file = st.file_uploader("📤 上传你的 GBD CSV 文件", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 数据成功加载！")

    # 可选择的分组字段
    group_fields = ["sex", "age", "measure", "location", "cause", "metric"]
    st.sidebar.header("图表设置")
    chart_type = st.sidebar.selectbox("选择图表类型", ["折线图"])
    group_by = st.sidebar.selectbox("选择分组字段", ["无分组"] + group_fields)

    # 用于筛选的字段（排除分组字段）
    filter_fields = [col for col in group_fields if col != group_by] if group_by != "无分组" else group_fields

    filters = {}
    for field in filter_fields:
        options = sorted(df[field].dropna().unique().tolist())
        selected = st.sidebar.multiselect(f"{field}（多选）", options, default=options)
        filters[field] = selected

    # 年份选择
    years = sorted(df["year"].dropna().unique().tolist())
    year_range = st.sidebar.slider("选择年份范围", min_value=min(years), max_value=max(years), value=(min(years), max(years)))

    # 是否显示置信区间
    show_ci = st.sidebar.checkbox("显示置信区间（upper/lower）", value=False)

    # 应用筛选条件
    filtered_df = df.copy()
    for field, values in filters.items():
        filtered_df = filtered_df[filtered_df[field].isin(values)]
    filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])]

    if filtered_df.empty:
        st.warning("❗ 没有找到匹配的数据，请调整筛选条件。")
    else:
        # 折线图
        base = alt.Chart(filtered_df).mark_line(point=True).encode(
            x="year:O",
            y="val:Q",
            tooltip=["year", "val"] + ([group_by] if group_by != "无分组" else [])
        ).properties(width=800, height=400)

        if group_by != "无分组":
            base = base.encode(color=f"{group_by}:N")

        chart = base

        if show_ci:
            band = alt.Chart(filtered_df).mark_area(opacity=0.2).encode(
                x="year:O",
                y="lower:Q",
                y2="upper:Q",
                color=f"{group_by}:N" if group_by != "无分组" else alt.value("lightgray")
            )
            chart = band + base

        st.subheader("📊 可视化结果")
        st.altair_chart(chart, use_container_width=True)
