# components/data_type_converter.py

import streamlit as st
import pandas as pd
import numpy as np

def display_data_type_converter(df: pd.DataFrame):
    """
    データ型を手動で変換するためのUIを表示します。
    """
    st.write('もし日付や数値の列が正しく認識されていない場合、ここで手動で変換を試みてください。')

    current_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        selected_col_for_type_conversion = st.selectbox(
            '型を変換したい列を選択:',
            [''] + current_cols,
            key='type_conv_col_select'
        )
    with col2:
        conversion_type = st.selectbox(
            '変換する型を選択:',
            ['選択してください', '日付/時刻', '数値'],
            key='conversion_type_select'
        )

    if selected_col_for_type_conversion and conversion_type != '選択してください':
        if st.button(f"選択した列 '{selected_col_for_type_conversion}' を '{conversion_type}' に変換"):
            try:
                # pandasのコピーを作成し、元のDataFrameに影響を与えないようにする
                df_copy = df.copy()

                if conversion_type == '日付/時刻':
                    # 非推奨の引数を削除し、より堅牢なロジックに変更
                    original_series = df_copy[selected_col_for_type_conversion]
                    
                    # 最初の試行: `errors='coerce'`で不正な値をNaTに変換
                    converted_series = pd.to_datetime(original_series, errors='coerce')
                    
                    # 変換が完全に失敗した場合、UNIXタイムスタンプとして再試行
                    if converted_series.isnull().all():
                        converted_series = pd.to_datetime(original_series, unit='s', errors='coerce')

                    if not converted_series.isnull().all():
                        # Streamlitでエラーを回避するため、datetimeを文字列に変換してから保存する
                        df_copy[selected_col_for_type_conversion] = converted_series.astype(str)
                        st.session_state.data_df = df_copy
                        st.success(f"列'{selected_col_for_type_conversion}'を日付/時刻型に変換しました。")
                    else:
                        st.error(f"列'{selected_col_for_type_conversion}'を日付/時刻型に変換できませんでした。元の形式のままです。")
                
                elif conversion_type == '数値':
                    df_copy[selected_col_for_type_conversion] = pd.to_numeric(df_copy[selected_col_for_type_conversion], errors='coerce')
                    st.session_state.data_df = df_copy
                    st.success(f"列'{selected_col_for_type_conversion}'を数値型に変換しました。")
                
                st.write('変換後のデータ型:')
                st.write(df_copy.dtypes)
                st.dataframe(df_copy.head())

            except Exception as e:
                st.error(f"型の変換中にエラーが発生しました: {e}")
