# components/analysis_functions.py

import streamlit as st
import pandas as pd

def calculate_and_plot_average(df: pd.DataFrame):
    """
    選択した数値列の平均値を計算して表示します。
    """
    st.write('選択した数値列の平均値を計算して表示します。')
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    selected_cols = st.multiselect('平均値を計算する列を選択してください:', numeric_cols, key='avg_cols')
    
    if selected_cols:
        avg_df = df[selected_cols].mean().to_frame().T
        avg_df.index = ['Average']
        st.subheader('選択した列の平均値')
        st.dataframe(avg_df)

def aggregate_and_plot_time_series(df: pd.DataFrame):
    """
    時系列データを集計して可視化します。
    """
    st.write('時系列データを期間ごとに集計し、グラフで可視化します。')
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if not datetime_cols:
        st.warning('このデータには日付/時刻型の列がありません。')
        return

    time_col = st.selectbox('時間軸の列を選択してください:', datetime_cols, key='time_series_col')
    value_cols = st.multiselect('集計する数値列を選択してください:', df.select_dtypes(include=['number']).columns.tolist(), key='time_series_values')
    interval = st.selectbox('集計期間を選択:', ['日', '週', '月', '年'], key='time_series_interval')

    if time_col and value_cols:
        period_map = {'日': 'D', '週': 'W', '月': 'M', '年': 'Y'}
        df.set_index(time_col, inplace=True)
        aggregated_df = df[value_cols].resample(period_map[interval]).mean().reset_index()
        st.subheader(f'{interval}ごとの集計データ')
        st.line_chart(aggregated_df.set_index(time_col))

def perform_advanced_statistics(df: pd.DataFrame):
    """
    高度な統計分析（例：記述統計）を行います。
    """
    st.write('データフレーム全体の記述統計量を表示します。')
    st.subheader('記述統計')
    st.dataframe(df.describe())
