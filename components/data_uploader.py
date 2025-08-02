# components/data_uploader.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def display_data_uploader_and_editor():
    """
    データのアップロードおよび手動での編集UIを表示します。
    """
    upload_tab, editor_tab = st.tabs(["CSVファイルのアップロード", "テーブルでデータを直接入力"])

    with upload_tab:
        uploaded_files = st.file_uploader("CSVファイルを選択", type=["csv"], accept_multiple_files=True)
        if uploaded_files:
            try:
                # 複数のCSVを結合するロジック（簡略化）
                dfs = [pd.read_csv(file) for file in uploaded_files]
                df = pd.concat(dfs, ignore_index=True)
                st.session_state.data_df = df
                st.success(f'{len(uploaded_files)} 個のファイルをアップロードし、結合が完了しました！')
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")
                st.session_state.data_df = pd.DataFrame()
        else:
            st.info('CSVファイルをアップロードしてください。')

    with editor_tab:
        if st.session_state.data_df.empty:
            # デフォルトのサンプルデータを設定
            sample_data_for_editor = {
                'Date': [datetime.now() - timedelta(minutes=i) for i in range(10)][::-1],
                'Product_A_Sales': [100, 105, 110, 95, 120, 115, 130, 125, 140, 135],
                'Product_B_Sales': [50, 52, 55, 48, 60, 62, 65, 61, 70, 68],
                'Customer_Rating': [4.5, 4.6, 4.7, 4.4, 4.8, 4.7, 4.9, 4.6, 4.9, 4.8],
                'Region': ['East', 'West', 'East', 'Central', 'West', 'East', 'Central', 'West', 'East', 'Central'],
                'Category': ['A', 'B', 'A', 'A', 'B', 'B', 'A', 'A', 'B', 'A'],
                'Sales_Target': [110, 55, 115, 100, 65, 120, 135, 130, 75, 145],
                'Customer_Satisfaction': [85, 92, 78, 95, 88, 90, 85, 91, 93, 89]
            }
            st.session_state.data_df = pd.DataFrame(sample_data_for_editor)
        
        # st.data_editorでデータフレームを編集可能にする
        edited_df = st.data_editor(
            st.session_state.data_df,
            num_rows="dynamic",
            use_container_width=True,
            key='editor_table'
        )
        st.session_state.data_df = edited_df

