# components/data_filtering.py

import streamlit as st
import pandas as pd
from datetime import timedelta

def display_data_filtering(df: pd.DataFrame) -> pd.DataFrame:
    """
    StreamlitのUIでデータのフィルタリング機能を表示し、
    フィルタリングされたデータフレームを返します。
    """
    with st.expander("データのフィルタリング", expanded=True):
        st.info("以下の設定でデータをフィルタリングできます。フィルタリングはグラフに反映されます。")
        filtered_df = df.copy()
        filter_cols = filtered_df.columns.tolist()
        
        # 列の選択
        filter_col = st.selectbox("フィルタリングしたい列を選択", [''] + filter_cols, key="filter_column_select")
        
        if filter_col:
            # 選択した列のデータ型に基づいたUIの動的生成
            series = filtered_df[filter_col]
            dtype = series.dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_val, max_val = float(series.min()), float(series.max())
                selected_range = st.slider(
                    f'{filter_col}の範囲を選択',
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=(max_val - min_val) / 100
                )
                filtered_df = filtered_df[ (filtered_df[filter_col] >= selected_range[0]) & (filtered_df[filter_col] <= selected_range[1]) ]
            
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                # 日付データをdatetimeオブジェクトに変換
                series = pd.to_datetime(filtered_df[filter_col], errors='coerce')
                series = series.dropna()

                if not series.empty:
                    min_datetime_full = series.min().to_pydatetime()
                    max_datetime_full = series.max().to_pydatetime()

                    # 日付範囲の長さに応じてスライダーのステップを調整
                    time_delta = max_datetime_full - min_datetime_full
                    if time_delta.total_seconds() > 365 * 24 * 60 * 60:
                        step = timedelta(days=30) # 1年以上の場合は月単位
                    elif time_delta.total_seconds() > 30 * 24 * 60 * 60:
                        step = timedelta(days=7) # 1ヶ月以上の場合は週単位
                    elif time_delta.total_seconds() > 7 * 24 * 60 * 60:
                        step = timedelta(days=1) # 1週間以上の場合は日単位
                    elif time_delta.total_seconds() > 24 * 60 * 60:
                        step = timedelta(hours=1) # 1日以上の場合は時間単位
                    else:
                        step = timedelta(minutes=1) # 1日未満の場合は分単位
                    
                    # スライダーの初期値をセッションステートで管理
                    if f'date_range_{filter_col}' not in st.session_state:
                        st.session_state[f'date_range_{filter_col}'] = (min_datetime_full, max_datetime_full)

                    # 日付/時刻スライダーを作成
                    selected_datetime_range = st.slider(
                        f'{filter_col}の期間を選択',
                        min_value=min_datetime_full,
                        max_value=max_datetime_full,
                        value=st.session_state[f'date_range_{filter_col}'],
                        step=step,
                        format="YYYY-MM-DD HH:mm"
                    )
                    st.session_state[f'date_range_{filter_col}'] = selected_datetime_range
                    
                    start_datetime, end_datetime = selected_datetime_range[0], selected_datetime_range[1]
                    
                    # 選択範囲の文字列を整形して表示
                    st.write(f"選択された期間: **{start_datetime.strftime('%Y-%m-%d %H:%M')}** から **{end_datetime.strftime('%Y-%m-%d %H:%M')}**")
                    
                    filtered_df = filtered_df[ (series >= start_datetime) & (series <= end_datetime) ]
                else:
                    st.warning("有効な日付範囲を選択してください。")
            
            else: # カテゴリカルデータ
                unique_values = filtered_df[filter_col].unique().tolist()
                
                # 検索ボックスの追加
                search_term = st.text_input('キーワードでフィルタ', value='', key=f"search_{filter_col}")
                
                # 検索キーワードで選択肢を絞り込む
                if search_term:
                    filtered_options = [val for val in unique_values if search_term.lower() in str(val).lower()]
                else:
                    filtered_options = unique_values

                # すべて選択/すべて解除ボタンの追加
                col_select_all, col_deselect_all = st.columns(2)
                with col_select_all:
                    if st.button("すべて選択", key=f"select_all_{filter_col}"):
                        st.session_state[f"selected_values_{filter_col}"] = filtered_options
                        st.rerun()
                with col_deselect_all:
                    if st.button("すべて解除", key=f"deselect_all_{filter_col}"):
                        st.session_state[f"selected_values_{filter_col}"] = []
                        st.rerun()
                
                # session_stateに選択値を保存
                if f"selected_values_{filter_col}" not in st.session_state:
                    st.session_state[f"selected_values_{filter_col}"] = unique_values
                
                # multiselectのデフォルト値は、session_stateから取得する
                selected_values = st.multiselect(
                    f'{filter_col}の値を絞り込む',
                    options=filtered_options, # 検索された項目のみ表示
                    default=st.session_state[f"selected_values_{filter_col}"],
                    key=f"multiselect_{filter_col}"
                )
                
                # ユーザーが手動で選択を変更したときにsession_stateを更新
                if selected_values != st.session_state[f"selected_values_{filter_col}"]:
                    st.session_state[f"selected_values_{filter_col}"] = selected_values
                    st.rerun()

                filtered_df = filtered_df[filtered_df[filter_col].isin(selected_values)]
        
        st.write(f"フィルタリング後のデータ: {len(filtered_df)} 行")
        st.dataframe(filtered_df)

    return filtered_df
