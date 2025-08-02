# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64

# componentsから必要な関数をインポート
# （このコードでは、これらの関数がapp.pyと同じディレクトリにあることを前提としています）
# from components.graph_plotter import (
#     plot_line_chart, plot_bar_chart, plot_stacked_bar_chart,
#     plot_scatter_plot, plot_heatmap, PLOTLY_TEMPLATES
# )
# from components.data_processor import (
#     load_and_combine_csv, calculate_and_plot_average,
#     aggregate_and_plot_time_series, perform_advanced_statistics
# )

# --- 簡易的なダミー関数 ---
# 実際のアプリケーションでは、別途ファイルを定義してください
def plot_line_chart(df, x_col, y_cols, **kwargs):
    st.write(f"折れ線グラフをプロット: X={x_col}, Y={y_cols}")
    st.line_chart(df.set_index(x_col)[y_cols])

def plot_bar_chart(df, x_col, y_col, **kwargs):
    st.write(f"棒グラフをプロット: X={x_col}, Y={y_col}")
    st.bar_chart(df.set_index(x_col)[y_col])

def plot_stacked_bar_chart(df, x_col, y_cols, **kwargs):
    st.write(f"積み立てグラフをプロット: X={x_col}, Y={y_cols}")
    st.bar_chart(df.set_index(x_col)[y_cols])

def plot_scatter_plot(df, x_col, y_col, **kwargs):
    st.write(f"散布図をプロット: X={x_col}, Y={y_col}")
    st.scatter_chart(df.set_index(x_col).loc[:, [y_col]])

def plot_heatmap(df, x_col, y_col, z_col, **kwargs):
    st.write(f"ヒートマップをプロット: X={x_col}, Y={y_col}, Z={z_col}")
    st.warning("この簡易版ではヒートマップは表示されません。")

PLOTLY_TEMPLATES = ["plotly", "ggplot2", "seaborn", "simple_white"]

def load_and_combine_csv(uploaded_files):
    df_list = []
    for f in uploaded_files:
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(f, encoding='shift_jis')
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)

def calculate_and_plot_average(df):
    st.subheader('選択した列の平均値')
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.warning("数値列がありません。")
        return
    
    selected_cols = st.multiselect('平均値を計算する列を選択してください:', numeric_cols)
    if selected_cols:
        avg_df = df[selected_cols].mean().reset_index()
        avg_df.columns = ['列', '平均値']
        st.dataframe(avg_df)
        st.bar_chart(avg_df.set_index('列'))

def aggregate_and_plot_time_series(df):
    st.subheader('時系列データ集計と可視化')
    date_cols = df.select_dtypes(include='datetime').columns.tolist()
    if not date_cols:
        st.warning("日付/時刻型の列が見つかりません。")
        return
    
    date_col = st.selectbox('日付列を選択:', date_cols)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    y_cols = st.multiselect('集計する数値列を選択:', numeric_cols)

    if date_col and y_cols:
        freq = st.selectbox('集計単位:', ['日', '週', '月', '年'])
        freq_map = {'日': 'D', '週': 'W', '月': 'M', '年': 'Y'}
        
        agg_df = df.set_index(date_col).resample(freq_map[freq])[y_cols].sum().reset_index()
        
        st.write('集計後のデータ')
        st.dataframe(agg_df)
        plot_line_chart(agg_df, date_col, y_cols, title=f'{freq}ごとの合計')

def perform_advanced_statistics(df):
    st.subheader('高度な統計分析')
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.warning("数値列がありません。")
        return

    st.write('---')
    st.markdown('#### **相関行列ヒートマップ**')
    try:
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            st.dataframe(corr_matrix)
            # st.plotly_chart(px.imshow(corr_matrix)) # plotlyは簡易版では使用不可
        else:
            st.warning('相関行列を計算するには、複数の数値列が必要です。')
    except Exception as e:
        st.error(f'相関行列の計算中にエラーが発生しました: {e}')


# --- 統合アプリケーションの開始 ---
st.set_page_config(layout="wide")
st.title('統合データ処理アプリ')

# --- データの入力・アップロードセクション ---
st.header('1. データの入力とアップロード')
st.write('以下のいずれかの方法でデータを準備してください。')

upload_tab, editor_tab = st.tabs(["CSVファイルのアップロード", "テーブルでデータを直接入力"])

with upload_tab:
    uploaded_files = st.file_uploader("CSVファイルを選択", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        try:
            df = load_and_combine_csv(uploaded_files)
            st.session_state.data_df = df
            st.success(f'{len(uploaded_files)} 個のファイルをアップロードし、結合が完了しました！')
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")
            st.session_state.data_df = pd.DataFrame()
    else:
        st.info('CSVファイルをアップロードしてください。')

with editor_tab:
    if 'data_df' not in st.session_state or st.session_state.data_df.empty:
        sample_data_for_editor = {
            'Date': [datetime.now().date() - timedelta(days=i) for i in range(5)][::-1],
            'Product_A_Sales': [100, 105, 110, 95, 120],
            'Product_B_Sales': [50, 52, 55, 48, 60],
            'Customer_Rating': [4.5, 4.6, 4.7, 4.4, 4.8],
            'Region': ['East', 'West', 'East', 'Central', 'West']
        }
        st.session_state.data_df = pd.DataFrame(sample_data_for_editor)
    
    edited_df = st.data_editor(
        st.session_state.data_df,
        num_rows="dynamic",
        use_container_width=True,
        key='editor_table'
    )
    st.session_state.data_df = edited_df

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
    
    st.markdown('---')
    st.subheader('2. データ型の調整 (オプション)')
    st.write('もし日付や数値の列が正しく認識されていない場合、ここで手動で変換を試みてください。')

    current_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        selected_col_for_type_conversion = st.selectbox('型を変換したい列を選択:', [''] + current_cols, key='type_conv_col_select')
    with col2:
        conversion_type = st.selectbox('変換する型を選択:', ['選択してください', '日付/時刻', '数値'], key='conversion_type_select')

    if selected_col_for_type_conversion and conversion_type != '選択してください':
        if st.button(f"選択した列 '{selected_col_for_type_conversion}' を '{conversion_type}' に変換"):
            try:
                if conversion_type == '日付/時刻':
                    df[selected_col_for_type_conversion] = pd.to_datetime(df[selected_col_for_type_conversion], errors='coerce', infer_datetime_format=True)
                    st.session_state.data_df = df
                    st.success(f"列'{selected_col_for_type_conversion}'を日付/時刻型に変換しました。")
                elif conversion_type == '数値':
                    df[selected_col_for_type_conversion] = pd.to_numeric(df[selected_col_for_type_conversion], errors='coerce')
                    st.session_state.data_df = df
                    st.success(f"列'{selected_col_for_type_conversion}'を数値型に変換しました。")
                
                st.write('変換後のデータ型:')
                st.write(df.dtypes)
                st.dataframe(df.head())
            except Exception as e:
                st.error(f"型の変換中にエラーが発生しました: {e}")

    st.markdown('---')
    st.subheader('3. データ可視化と分析')
    st.write('---')

    viz_tab, analysis_tab = st.tabs(["グラフ描画", "データ分析"])

    with viz_tab:
        graph_type = st.selectbox(
            '表示するグラフの種類を選択してください:',
            ('選択してください', '折れ線グラフ', '棒グラフ', '積み立てグラフ', '散布図', 'ヒートマップ')
        )
        if graph_type != '選択してください':
            st.write(f'**{graph_type} の設定**')
            columns = df.columns.tolist()
            if graph_type in ['折れ線グラフ', '棒グラフ', '積み立てグラフ']:
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_cols = st.multiselect('Y軸に使う列を1つ以上選択してください:', columns)
                if x_axis_col and y_axis_cols:
                    if graph_type == '折れ線グラフ':
                        plot_line_chart(df, x_axis_col, y_axis_cols)
                    elif graph_type == '棒グラフ':
                        plot_bar_chart(df, x_axis_col, y_axis_cols[0])
                    elif graph_type == '積み立てグラフ':
                        plot_stacked_bar_chart(df, x_axis_col, y_axis_cols)
            elif graph_type == '散布図':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                if x_axis_col and y_axis_col:
                    plot_scatter_plot(df, x_axis_col, y_axis_col)
            elif graph_type == 'ヒートマップ':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                z_axis_col = st.selectbox('値を表すZ軸に使う列を選択してください (任意):', [''] + columns)
                if x_axis_col and y_axis_col:
                    plot_heatmap(df, x_axis_col, y_axis_col, z_axis_col)

    with analysis_tab:
        analysis_type = st.selectbox(
            '実行する分析を選択してください:',
            ('選択してください', '選択した列の平均値', '時系列データ集計と可視化', '高度な統計分析')
        )
        if analysis_type == '選択した列の平均値':
            calculate_and_plot_average(df)
        elif analysis_type == '時系列データ集計と可視化':
            aggregate_and_plot_time_series(df)
        elif analysis_type == '高度な統計分析':
            perform_advanced_statistics(df)
else:
    st.info('データを直接入力するか、CSVファイルをアップロードしてください。')
