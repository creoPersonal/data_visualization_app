# components/data_type_converter.py

import streamlit as st
import pandas as pd

def display_data_type_converter(df: pd.DataFrame):
    """
    データ型の変換UIを表示し、変換されたデータフレームをセッションステートに保存します。
    """
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
