# app.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# componentsから必要な関数をインポート
from components.graph_plotter import (
    plot_line_chart,
    plot_bar_chart,
    plot_stacked_bar_chart,
    plot_scatter_plot,
    plot_heatmap,
    PLOTLY_TEMPLATES
)
from components.data_processor import (
    load_and_combine_csv,
    calculate_and_plot_average,
    aggregate_and_plot_time_series,
    perform_advanced_statistics
)

st.set_page_config(layout="wide")

st.title('データ可視化Webアプリケーション')

# --- データ入力・編集セクション ---
st.header('1. CSVファイルをアップロード')
st.write('CSVファイルをアップロードしてください。複数選択すると、自動で結合されます。')

uploaded_files = st.file_uploader("CSVファイルを選択", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    try:
        # アップロードされたファイルを結合する
        df = load_and_combine_csv(uploaded_files)
        st.session_state.data_df = df
        st.info(f'{len(uploaded_files)} 個のファイルをアップロードし、結合が完了しました！')
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {e}")
        st.session_state.data_df = pd.DataFrame()
else:
    st.header('2. または、以下のテーブルでデータを直接入力')
    st.write('CSVファイルがアップロードされていない場合、こちらのデータが使用されます。')

    if 'data_df' not in st.session_state or st.session_state.data_df.empty:
        sample_data_for_editor = {
            'Date': [datetime.now() - timedelta(days=i) for i in range(5)][::-1],
            'Product_A_Sales': [100, 105, 110, 95, 120],
            'Product_B_Sales': [50, 52, 55, 48, 60],
            'Customer_Rating': [4.5, 4.6, 4.7, 4.4, 4.8],
            'Region': ['East', 'West', 'East', 'Central', 'West']
        }
        st.session_state.data_df = pd.DataFrame(sample_data_for_editor)
        st.session_state.data_df['Date'] = pd.to_datetime(st.session_state.data_df['Date']).dt.date
    
    # データエディタの表示とセッションステートへの保存
    edited_df_from_editor = st.data_editor(
        st.session_state.data_df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor"
    )
    st.session_state.data_df = edited_df_from_editor

df = st.session_state.data_df

if not df.empty:
    st.markdown('---')
    st.subheader('現在のデータのプレビュー（最初の5行）')
    st.dataframe(df.head())

    st.subheader('現在のデータの基本情報')
    st.write(f'行数: {df.shape[0]}, 列数: {df.shape[1]}')
    st.write('データ型:')
    st.write(df.dtypes)

    # --- 手動でのデータ型変換セクションを追加 ---
    st.subheader('3. データ型の調整 (オプション)')
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
                    original_series = df[selected_col_for_type_conversion]
                    
                    converted_series = pd.to_datetime(original_series, errors='coerce', infer_datetime_format=True)
                    
                    if converted_series.isnull().all():
                        converted_series = pd.to_datetime(original_series, unit='s', errors='coerce')

                    if not converted_series.isnull().all():
                        df[selected_col_for_type_conversion] = converted_series
                        st.session_state.data_df = df
                        st.success(f"列'{selected_col_for_type_conversion}'を日付/時刻型に変換しました。")
                    else:
                        st.error(f"列'{selected_col_for_type_conversion}'を日付/時刻型に変換できませんでした。元の形式のままです。")
                
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

    # --- グラフ描画セクション ---
    st.subheader('グラフ描画セクション')
    st.write('---')

    graph_type = st.selectbox(
        '表示するグラフの種類を選択してください:',
        ('選択してください', '折れ線グラフ', '棒グラフ', '積み立てグラフ', '散布図', 'ヒートマップ')
    )

    if graph_type != '選択してください':
        st.write(f'**{graph_type} の設定**')

        columns = df.columns.tolist()

        st.sidebar.subheader('グラフカスタマイズオプション')
        custom_title = st.sidebar.text_input('グラフタイトル (任意):', '')
        custom_x_label = st.sidebar.text_input('X軸ラベル (任意):', '')
        custom_y_label = st.sidebar.text_input('Y軸ラベル (任意):', '')

        selected_color_theme = st.sidebar.selectbox(
            'カラーテーマを選択:',
            PLOTLY_TEMPLATES,
            index=PLOTLY_TEMPLATES.index("plotly")
        )

        if graph_type in ['折れ線グラフ', '棒グラフ', '積み立てグラフ']:
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_cols = st.multiselect('Y軸に使う列を1つ以上選択してください:', columns)

            if x_axis_col and y_axis_cols:
                if graph_type == '折れ線グラフ':
                    plot_line_chart(df, x_axis_col, y_axis_cols,
                                     title=custom_title, x_label=custom_x_label,
                                     y_label=custom_y_label, color_theme=selected_color_theme)
                elif graph_type == '棒グラフ':
                    plot_bar_chart(df, x_axis_col, y_axis_cols[0],
                                    title=custom_title, x_label=custom_x_label,
                                    y_label=custom_y_label, color_theme=selected_color_theme)
                elif graph_type == '積み立てグラフ':
                    plot_stacked_bar_chart(df, x_axis_col, y_axis_cols,
                                           title=custom_title, x_label=custom_x_label,
                                           y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

        elif graph_type == '散布図':
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
            color_col = st.selectbox('色分けに使う列を選択してください (任意):', [''] + columns)

            if x_axis_col and y_axis_col:
                plot_scatter_plot(df, x_axis_col, y_axis_col, color_col if color_col else None,
                                  title=custom_title, x_label=custom_x_label,
                                  y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

        elif graph_type == 'ヒートマップ':
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
            z_axis_col = st.selectbox('値を表すZ軸に使う列を選択してください (任意):', [''] + columns)

            if x_axis_col and y_axis_col:
                plot_heatmap(df, x_axis_col, y_axis_col, z_axis_col if z_axis_col else None,
                             title=custom_title, x_label=custom_x_label,
                             y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

    else:
        st.info('グラフの種類を選択すると、設定オプションが表示されます。')

    # --- データ分析セクション ---
    st.subheader('データ分析')
    st.write('---')

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
    elif analysis_type == '相関行列':
        st.subheader('相関行列ヒートマップ')
        try:
            # 数値列のみを抽出
            numeric_df = df.select_dtypes(include=np.number)
            if not numeric_df.empty and len(numeric_df.columns) > 1:
                # 相関行列を計算
                corr_matrix = numeric_df.corr()
                # ヒートマップとして表示
                st.write(f"以下の**{len(corr_matrix)}**個の数値列間の相関行列を表示します:")
                st.write(corr_matrix.columns.tolist())
                plot_heatmap(corr_matrix, x_axis_col=corr_matrix.columns.name, y_axis_col=None, z_axis_col=None, 
                             title='相関行列ヒートマップ', x_label='', y_label='', color_theme=st.session_state.get('selected_color_theme', 'plotly'))
            else:
                st.warning('相関行列を計算するには、複数の数値列が必要です。')
        except Exception as e:
            st.error(f'相関行列の計算中にエラーが発生しました: {e}')
    else:
        st.info('分析の種類を選択すると、オプションが表示されます。')

else:
    st.info('データを直接入力するか、CSVファイルをアップロードしてください。')
