
import streamlit as st
import pandas as pd
import altair as alt
import io
from PIL import Image

st.set_page_config(page_title="GBD 可视化助手", layout="wide")
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
}
.main .block-container {
    padding-top: 2rem;
}
.stSelectbox, .stMultiSelect, .stSlider, .stCheckbox {
    background-color: white;
    border-radius: 6px;
    padding: 10px;
    border: 1px solid #d3d3d3;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🌍 GBD 可视化助手</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #2980b9;'>内测版 · 由 Zhangnan 开发</h4><br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📤 上传 GBD CSV 文件", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 数据成功加载！")

    tabs = st.tabs(["📊 分组趋势图", "🌎 地区对比（开发中）", "📁 疾病对比（开发中）"])

    with tabs[0]:
        group_fields = ["sex", "age", "measure", "location", "cause", "metric"]
        st.sidebar.header("🎛️ 图表控制面板")

        chart_type = st.sidebar.selectbox("图表类型", ["折线图"])
        group_by = st.sidebar.selectbox("分组字段", ["无分组"] + group_fields)

        years = sorted(df["year"].dropna().unique().tolist())
        year_range = st.sidebar.slider("选择年份范围", min_value=min(years), max_value=max(years), value=(min(years), max(years)))
        show_ci = st.sidebar.checkbox("显示置信区间", value=False)

        if group_by != "无分组":
            group_options = sorted(df[group_by].dropna().unique().tolist())
            selected_groups = st.sidebar.multiselect(f"选择要展示的 {group_by}", group_options)
        else:
            selected_groups = []

        filter_fields = [col for col in group_fields if col != group_by] if group_by != "无分组" else group_fields
        filters = {}
        st.sidebar.markdown("---")
        st.sidebar.markdown("📌 其他筛选条件")
        for field in filter_fields:
            options = sorted(df[field].dropna().unique().tolist())
            selected = st.sidebar.multiselect(f"{field}（请选择）", options)
            filters[field] = selected

        filtered_df = df.copy()
        for field, values in filters.items():
            if values:
                filtered_df = filtered_df[filtered_df[field].isin(values)]
        filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])]

        if group_by != "无分组" and selected_groups:
            filtered_df = filtered_df[filtered_df[group_by].isin(selected_groups)]

        if filtered_df.empty:
            st.warning("❗ 当前筛选无数据，请尝试修改条件。")
        else:
            st.markdown("### 📈 可视化图表")
            selection_text = (
                f"**当前选择：** "
                f"{filters.get('measure', [''])[0] if filters.get('measure') else ''} · "
                f"{filters.get('sex', [''])[0] if filters.get('sex') else ''} · "
                f"{filters.get('location', [''])[0] if filters.get('location') else ''} · "
                f"{filters.get('cause', [''])[0] if filters.get('cause') else ''} · "
                f"{year_range[0]}–{year_range[1]}"
            )
            st.markdown(selection_text)

            base = alt.Chart(filtered_df).mark_line(point=True).encode(
                x="year:O",
                y="val:Q",
                tooltip=["year", "val"] + ([group_by] if group_by != "无分组" else [])
            ).properties(width=850, height=400)

            if group_by != "无分组":
                base = base.encode(color=f"{group_by}:N")
            chart = base

            if show_ci:
                band = alt.Chart(filtered_df).mark_area(opacity=0.2).encode(
                    x="year:O",
                    y="lower:Q",
                    y2="upper:Q",
                    color=f"{group_by}:N" if group_by != "无分组" else alt.value("#d0d0d0")
                )
                chart = band + base

            st.altair_chart(chart, use_container_width=True)

            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 下载筛选后的数据", csv_data, file_name="filtered_gbd_data.csv", mime="text/csv")

