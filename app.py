# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# componentsから必要な関数をインポート
from components.data_uploader import display_data_uploader_and_editor
from components.data_type_converter import display_data_type_converter
from components.data_filtering import display_data_filtering
from components.graph_plotter import (
    plot_line_chart,
    plot_bar_chart,
    plot_stacked_bar_chart,
    plot_scatter_plot,
    plot_heatmap,
    plot_pie_chart,
    plot_box_plot,
    plot_histogram,
    plot_correlation_heatmap, # 新しくインポート
    PLOTLY_TEMPLATES
)
from components.analysis_functions import (
    # calculate_and_plot_average, # 削除
    aggregate_and_plot_time_series,
    perform_advanced_statistics
)
from components.ai_insights import display_ai_insights

# --- 統合アプリケーションの開始 ---
st.set_page_config(layout="wide")
st.title('統合データ処理アプリ')

# セッション状態を初期化
if 'data_df' not in st.session_state:
    st.session_state.data_df = pd.DataFrame()
if 'ai_analysis_triggered' not in st.session_state:
    st.session_state.ai_analysis_triggered = False
if 'ai_insight_text' not in st.session_state:
    st.session_state.ai_insight_text = None

# 1. データの入力とアップロード
st.header('1. データの入力とアップロード')
st.write('以下のいずれかの方法でデータを準備してください。')
display_data_uploader_and_editor()
df = st.session_state.data_df.copy()

if not df.empty:
    st.markdown('---')
    st.subheader('現在のデータのプレビューとダウンロード')
    st.dataframe(df.head())

    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="CSVファイルをダウンロード",
        data=csv_data,
        file_name='edited_data.csv',
        mime='text/csv',
    )
    
    # 2. データ型の調整 (オプション)
    st.markdown('---')
    st.subheader('2. データ型の調整 (オプション)')
    display_data_type_converter(df)
    df = st.session_state.data_df.copy()

    # 3. データ可視化と分析
    st.markdown('---')
    st.subheader('3. データ可視化と分析')
    st.write('---')

    viz_tab, analysis_tab, ai_tab = st.tabs(["グラフ描画", "データ分析", "AIによるインサイト"])

    with viz_tab:
        # フィルタリング機能の呼び出し
        filtered_df = display_data_filtering(df)
        df = filtered_df 

        graph_type = st.selectbox(
            '表示するグラフの種類を選択してください:',
            ('選択してください', '折れ線グラフ', '棒グラフ', '積み立てグラフ', '散布図', 'ヒートマップ', '円グラフ', '箱ひげ図', 'ヒストグラム')
        )
        
        if graph_type != '選択してください':
            st.write(f'**{graph_type} の設定**')
            columns = df.columns.tolist()

            # 共通のグラフ設定
            col_settings_1, col_settings_2 = st.columns([1, 1])
            with col_settings_1:
                title = st.text_input('グラフのタイトル', value='')
            with col_settings_2:
                title_x_pos = st.slider('タイトルの位置', 0.0, 1.0, 0.5, 0.01)
            col_labels, col_theme = st.columns(2)
            with col_labels:
                x_label = st.text_input('X軸のラベル (任意)', value='')
                y_label = st.text_input('Y軸のラベル (任意)', value='')
            with col_theme:
                color_theme = st.selectbox('カラーテーマを選択', PLOTLY_TEMPLATES, index=6)

            if graph_type in ['折れ線グラフ', '棒グラフ', '積み立てグラフ']:
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_cols = st.multiselect('Y軸に使う列を1つ以上選択してください:', columns)
                if x_axis_col and y_axis_cols:
                    if graph_type == '折れ線グラフ':
                        plot_line_chart(df, x_axis_col, y_axis_cols, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
                    elif graph_type == '棒グラフ':
                        plot_bar_chart(df, x_axis_col, y_axis_cols[0], title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
                    elif graph_type == '積み立てグラフ':
                        plot_stacked_bar_chart(df, x_axis_col, y_axis_cols, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
            elif graph_type == '散布図':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                color_col = st.selectbox('色分けに使う列 (任意)', [''] + columns)
                if x_axis_col and y_axis_col:
                    plot_scatter_plot(df, x_axis_col, y_axis_col, color_col=color_col if color_col else None, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
            elif graph_type == 'ヒートマップ':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                z_axis_col = st.selectbox('値を表すZ軸に使う列を選択してください (任意):', [''] + columns)
                if x_axis_col and y_axis_col:
                    plot_heatmap(df, x_axis_col, y_axis_col, z_col=z_axis_col if z_axis_col else None, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
            elif graph_type == '円グラフ':
                names_col = st.selectbox('カテゴリを表す列を選択してください:', columns)
                values_col = st.selectbox('値を表す列を選択してください:', columns)
                if names_col and values_col:
                    plot_pie_chart(df, names_col, values_col, title=title, color_theme=color_theme, title_x_pos=title_x_pos)
            elif graph_type == '箱ひげ図':
                x_axis_col = st.selectbox('カテゴリを表す列を選択してください:', [''] + columns)
                y_axis_col = st.selectbox('値を表す列を選択してください:', columns)
                if y_axis_col:
                    plot_box_plot(df, x_axis_col if x_axis_col else None, y_axis_col, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)
            elif graph_type == 'ヒストグラム':
                x_axis_col = st.selectbox('列を選択してください:', columns)
                if x_axis_col:
                    plot_histogram(df, x_axis_col, title=title, x_label=x_label, y_label=y_label, color_theme=color_theme, title_x_pos=title_x_pos)

    with analysis_tab:
        analysis_type = st.selectbox(
            '実行する分析を選択してください:',
            ('選択してください', '時系列データ集計と可視化', '高度な統計分析', '相関行列ヒートマップ')
        )
        if analysis_type == '時系列データ集計と可視化':
            aggregate_and_plot_time_series(df)
        elif analysis_type == '高度な統計分析':
            perform_advanced_statistics(df)
        elif analysis_type == '相関行列ヒートマップ':
            plot_correlation_heatmap(df)
                
    with ai_tab:
        # AIインサイトUIの呼び出し
        display_ai_insights(df)

else:
    st.info('データを直接入力するか、CSVファイルをアップロードしてください。')
