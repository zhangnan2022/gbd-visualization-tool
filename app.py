import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import io
import base64
from docx import Document
from docx.shared import Inches
from io import BytesIO
import math
from scipy import stats

st.set_page_config(page_title="GBD 可视化助手", layout="wide")

st.title("GBD 可视化助手 · 内测版")
st.markdown("作者：zhangnan")


TABS = st.tabs(["分组趋势图", "Table 1 生成器"])

with TABS[0]:
    st.header("分组趋势图")
    uploaded_file = st.file_uploader("上传 GBD CSV 数据文件", type=["csv"], key="chart")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # 获取可选项
        measure_options = df['measure'].dropna().unique().tolist()
        location_options = df['location'].dropna().unique().tolist()
        sex_options = df['sex'].dropna().unique().tolist()
        age_options = df['age'].dropna().unique().tolist()
        cause_options = df['cause'].dropna().unique().tolist()
        metric_options = df['metric'].dropna().unique().tolist()
        year_options = sorted(df['year'].dropna().unique().tolist())

        st.subheader("筛选条件")
        chart_type = st.selectbox("选择图表类型", ["折线图"], index=0)

        group_by = st.selectbox("选择分组字段", ["sex", "age", "location", "cause"], index=0)

        selected_measure = st.selectbox("请选择 measure", ["请选择"] + measure_options)
        selected_location = st.selectbox("请选择 location", ["请选择"] + location_options)
        selected_sex = st.multiselect("请选择 sex", sex_options) if group_by != "sex" else []
        selected_age = st.multiselect("请选择 age", age_options) if group_by != "age" else []
        selected_cause = st.selectbox("请选择 cause", ["请选择"] + cause_options)
        selected_metric = st.selectbox("请选择 metric", ["请选择"] + metric_options)
        selected_years = st.slider("选择年份范围", min_value=min(year_options), max_value=max(year_options), value=(min(year_options), max(year_options)))

        show_ci = st.checkbox("显示置信区间 (upper/lower)")

        if selected_measure != "请选择" and selected_location != "请选择" and selected_cause != "请选择" and selected_metric != "请选择":
            chart_df = df[(df['measure'] == selected_measure) &
                          (df['location'] == selected_location) &
                          (df['cause'] == selected_cause) &
                          (df['metric'] == selected_metric) &
                          (df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

            if group_by != "sex" and selected_sex:
                chart_df = chart_df[chart_df['sex'].isin(selected_sex)]
            if group_by != "age" and selected_age:
                chart_df = chart_df[chart_df['age'].isin(selected_age)]

            if not chart_df.empty:
                base = alt.Chart(chart_df).encode(
                    x=alt.X('year:O', title='Year'),
                    y=alt.Y('val:Q', title='Value'),
                    color=group_by + ":N"
                )

                lines = base.mark_line(point=True)
                if show_ci:
                    band = base.mark_area(opacity=0.3).encode(
                        y='lower:Q',
                        y2='upper:Q'
                    )
                    chart = (band + lines).properties(width=800, height=400)
                else:
                    chart = lines.properties(width=800, height=400)

                st.altair_chart(chart, use_container_width=True)


with TABS[1]:
    st.header("Table 1 生成器")
    table_file = st.file_uploader("上传 GBD CSV 文件用于生成 Table 1", type=["csv"], key="table")

    if table_file is not None:
        df = pd.read_csv(table_file)

        st.subheader("选择生成参数")
        available_causes = df['cause'].dropna().unique().tolist()
        available_ages = df['age'].dropna().unique().tolist()
        available_locations = df['location'].dropna().unique().tolist()
        available_sexes = df['sex'].dropna().unique().tolist()
        available_measures = df['measure'].dropna().unique().tolist()
        available_metrics = df['metric'].dropna().unique().tolist()

        selected_cause = st.selectbox("请选择病因 (cause)", available_causes)
        selected_age = st.selectbox("请选择年龄组 (age)", available_ages)
        selected_sex = st.selectbox("请选择性别 (sex)", available_sexes)
        selected_measure = st.selectbox("请选择指标 (measure)", available_measures)
        selected_metric = st.selectbox("请选择计量类型 (metric)", available_metrics)

        year_range = [1990, 2021]

        def format_val(val, lower, upper, digits=2):
            return f"{round(val, digits)} ({round(lower, digits)} to {round(upper, digits)})"

        def get_row(location):
            row = {"Feature": location}

            use_age = selected_age
            if selected_age == "Age-standardized" and selected_metric == "Number":
                use_age = "All ages"

            for year in year_range:
                d_number = df[(df['location'] == location) & (df['year'] == year) & (df['cause'] == selected_cause) &
                              (df['metric'] == 'Number') & (df['measure'] == selected_measure) &
                              (df['age'] == use_age) & (df['sex'] == selected_sex)]

                d_rate = df[(df['location'] == location) & (df['year'] == year) & (df['cause'] == selected_cause) &
                            (df['metric'] == 'Rate') & (df['measure'] == selected_measure) &
                            (df['age'] == selected_age) & (df['sex'] == selected_sex)]

                row[f"Cases_{year}"] = format_val(d_number['val'].sum(), d_number['lower'].sum(), d_number['upper'].sum(), 0) if not d_number.empty else "NA"
                row[f"Rates_{year}"] = format_val(d_rate['val'].sum(), d_rate['lower'].sum(), d_rate['upper'].sum()) if not d_rate.empty else "NA"

            d_1990 = df[(df['location'] == location) & (df['year'] == 1990) & (df['cause'] == selected_cause) &
                        (df['metric'] == 'Number') & (df['measure'] == selected_measure) &
                        (df['age'] == use_age) & (df['sex'] == selected_sex)]
            d_2021 = df[(df['location'] == location) & (df['year'] == 2021) & (df['cause'] == selected_cause) &
                        (df['metric'] == 'Number') & (df['measure'] == selected_measure) &
                        (df['age'] == use_age) & (df['sex'] == selected_sex)]

            if not d_1990.empty and not d_2021.empty:
                v1 = d_1990['val'].sum()
                v2 = d_2021['val'].sum()
                change = ((v2 - v1) / v1) * 100 if v1 != 0 else np.nan
                row['Cases_change'] = f"{round(change, 2)}%"
            else:
                row['Cases_change'] = "NA"

            d_rate_all = df[(df['location'] == location) & (df['cause'] == selected_cause) &
                            (df['metric'] == 'Rate') & (df['measure'] == selected_measure) &
                            (df['age'] == selected_age) & (df['sex'] == selected_sex)]
            eapc_ci = "NA"
            if d_rate_all.shape[0] >= 2:
                try:
                    d_rate_all = d_rate_all[d_rate_all['val'] > 0]
                    d_rate_all['y'] = np.log(d_rate_all['val'])
                    slope, _, _, _, std_err = stats.linregress(d_rate_all['year'], d_rate_all['y'])
                    eapc = (np.exp(slope) - 1) * 100
                    lci = (np.exp(slope - 1.96 * std_err) - 1) * 100
                    uci = (np.exp(slope + 1.96 * std_err) - 1) * 100
                    eapc_ci = f"{round(eapc, 2)} ({round(lci, 2)} to {round(uci, 2)})"
                except:
                    pass
            row['EAPC_CI'] = eapc_ci

            return row

        if st.button("生成 Table 1"):
            summary_df = []
            locations = df['location'].dropna().unique().tolist()
            sdi_groups = ['High SDI', 'High-middle SDI', 'Middle SDI', 'Low-middle SDI', 'Low SDI']
            region_groups = [x for x in locations if x not in ['Global'] + sdi_groups]
            ordered = ['Global'] + sdi_groups + sorted(region_groups)

            for loc in ordered:
                if loc in locations:
                    summary_df.append(get_row(loc))

            summary_table = pd.DataFrame(summary_df)
            st.dataframe(summary_table)

            doc = Document()
            doc.add_heading("Table 1", level=1)

            table = doc.add_table(rows=1, cols=len(summary_table.columns))
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(summary_table.columns):
                hdr_cells[i].text = str(col)

            for _, row in summary_table.iterrows():
                row_cells = table.add_row().cells
                for i, item in enumerate(row):
                    row_cells[i].text = str(item)

            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)

            st.download_button(
                label="下载 Word 文件",
                data=buf,
                file_name="Table1.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
