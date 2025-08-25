import streamlit as st
import pandas as pd
import altair as alt

def show_group_trend_tab():
    st.header("分组趋势图")
    uploaded_file = st.file_uploader("上传 GBD CSV 数据文件", type=["csv"], key="chart")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        measure_options = df['measure'].dropna().unique().tolist()
        location_options = df['location'].dropna().unique().tolist()
        sex_options = df['sex'].dropna().unique().tolist()
        age_options = df['age'].dropna().unique().tolist()
        cause_options = df['cause'].dropna().unique().tolist()
        year_options = sorted(df['year'].dropna().unique().tolist())

        st.subheader("筛选条件")
        chart_type = st.selectbox("选择图表类型", ["折线图"], index=0)

        group_by = st.selectbox("选择分组字段", ["sex", "age", "location", "cause"], index=0)

        selected_measure = st.selectbox("请选择 measure", ["请选择"] + measure_options)
        selected_location = st.selectbox("请选择 location", ["请选择"] + location_options)
        selected_sex = st.multiselect("请选择 sex", sex_options) if group_by != "sex" else []
        selected_age = st.multiselect("请选择 age", age_options) if group_by != "age" else []
        selected_cause = st.selectbox("请选择 cause", ["请选择"] + cause_options)
        selected_years = st.slider("选择年份范围", min_value=min(year_options), max_value=max(year_options), value=(min(year_options), max(year_options)))

        show_ci = st.checkbox("显示置信区间 (upper/lower)")

        if selected_measure != "请选择" and selected_location != "请选择" and selected_cause != "请选择":
            chart_df = df[(df['measure'] == selected_measure) &
                          (df['location'] == selected_location) &
                          (df['cause'] == selected_cause) &
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