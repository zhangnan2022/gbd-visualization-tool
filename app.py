
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GBD 可视化助手", layout="wide")

st.title("🌍 GBD 可视化助手")
st.markdown("上传从 IHME 下载的 GBD 数据 CSV 文件，进行交互式可视化。")

uploaded_file = st.file_uploader("📤 上传你的 CSV 文件", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 上传成功！预览如下：")
    st.dataframe(df.head())

    with st.sidebar:
        st.header("🎛️ 筛选条件")

        dimension_cols = df.columns.tolist()

        disease_col = st.selectbox("疾病列", dimension_cols)
        metric_col = st.selectbox("指标列", dimension_cols)
        location_col = st.selectbox("地区列", dimension_cols)
        year_col = st.selectbox("年份列", dimension_cols)
        value_col = st.selectbox("数值列", dimension_cols)

        selected_disease = st.selectbox("选择疾病", df[disease_col].unique())
        selected_metric = st.selectbox("选择指标", df[metric_col].unique())
        selected_location = st.selectbox("选择地区", df[location_col].unique())

    # 过滤数据
    filtered = df[
        (df[disease_col] == selected_disease) &
        (df[metric_col] == selected_metric) &
        (df[location_col] == selected_location)
    ]

    # 转换年份为数值
    filtered[year_col] = pd.to_numeric(filtered[year_col], errors='coerce')

    # 折线图
    fig = px.line(filtered.sort_values(year_col), x=year_col, y=value_col,
                  title=f"{selected_location} | {selected_disease} | {selected_metric} 趋势图")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("请先上传 GBD 数据 CSV 文件以开始。")
