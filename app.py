import streamlit as st
from group_trend_chart import show_group_trend_tab
from table1_generator import show_table1_tab

st.set_page_config(page_title="GBD 可视化助手", layout="wide")
st.title("GBD 可视化助手 · 内测版")
st.markdown("作者：zhangnan")

tabs = st.tabs(["分组趋势图", "Table 1 生成器"])

with tabs[0]:
    show_group_trend_tab()

with tabs[1]:
    show_table1_tab()