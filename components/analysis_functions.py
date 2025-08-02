# components/analysis_functions.py
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

def aggregate_and_plot_time_series(df: pd.DataFrame):
    """
    時系列データを集計し、折れ線グラフで可視化します。
    """
    st.subheader('時系列データ集計と可視化')
    
    # 日付/時刻型の列を抽出
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if not datetime_cols:
        st.warning('データに日付/時刻型の列がありません。データ型の調整を行ってください。')
        return
        
    date_col = st.selectbox('タイムスタンプ列を選択:', datetime_cols)
    
    # ユーザーが時間帯を選択できるようにするUIを追加
    st.write("---")
    st.markdown("**時間帯でデータを絞り込む (任意)**")
    
    use_time_filter = st.checkbox("時間帯でフィルタリングする")
    start_time = end_time = None
    
    if use_time_filter:
        col_start, col_end = st.columns(2)
        with col_start:
            start_time = st.time_input("開始時間:", value=pd.to_datetime("09:00").time())
        with col_end:
            end_time = st.time_input("終了時間:", value=pd.to_datetime("17:00").time())

    # 集計とプロットのオプション
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.warning('数値型の列がありません。')
        return

    value_col = st.selectbox('集計する数値列を選択:', numeric_cols)
    
    # 集計の粒度を選択
    resample_freq = st.selectbox(
        '集計の粒度を選択:',
        {'日別': 'D', '週別': 'W', '月別': 'M', '年別': 'Y'}
    )
    
    if st.button('集計とプロットを実行'):
        try:
            # 時間帯でフィルタリング
            filtered_df = df.copy()
            if use_time_filter and start_time and end_time:
                # dt.timeはdatetimeオブジェクトにのみ適用可能なので、先に変換する
                if pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
                    filtered_df = filtered_df[
                        (filtered_df[date_col].dt.time >= start_time) &
                        (filtered_df[date_col].dt.time <= end_time)
                    ]
                else:
                    st.warning("タイムスタンプ列が日付/時刻型ではありません。データ型の調整を行ってください。")
                    return

            # フィルタリング後のデータが空でないか確認
            if filtered_df.empty:
                st.warning("指定された時間帯に一致するデータが見つかりませんでした。")
                return

            # 集計を実行
            agg_df = filtered_df.set_index(date_col).resample(resample_freq)[value_col].mean().reset_index()
            agg_df.columns = ['Timestamp', 'Average_Value']
            
            # 結果を可視化
            st.success('集計が完了しました！')
            st.dataframe(agg_df.head(), hide_index=True)
            
            fig = px.line(
                agg_df, 
                x='Timestamp', 
                y='Average_Value', 
                title=f'{value_col}の{resample_freq}別平均値',
                labels={'Timestamp': 'タイムスタンプ', 'Average_Value': '平均値'}
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"時系列データの集計中にエラーが発生しました: {e}")

def perform_advanced_statistics(df: pd.DataFrame):
    """
    高度な統計分析（記述統計量、相関行列）を表示します。
    """
    st.subheader('高度な統計分析')

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    if not numeric_cols:
        st.warning('数値型の列がありません。')
        return

    # 記述統計量の表示
    st.markdown('### 記述統計量')
    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
