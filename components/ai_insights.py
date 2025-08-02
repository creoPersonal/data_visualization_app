# components/ai_insights.py

import streamlit as st
import pandas as pd
import requests
import json
import time
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def get_ai_insight(prompt_text):
    """
    Gemini APIを呼び出して、テキスト生成を行います。
    """
    chatHistory = []
    chatHistory.append({ "role": "user", "parts": [{ "text": prompt_text }] })
    payload = { "contents": chatHistory }
    # 環境変数からAPIキーを読み込む
    apiKey = os.getenv("API_KEY", "") 
    # もし環境変数が設定されていなければエラーメッセージを表示
    if not apiKey:
        st.error("APIキーが設定されていません。プロジェクトのルートディレクトリに.envファイルを作成し、API_KEY='your_api_key'と記述してください。")
        return None
        
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={apiKey}"
    
    retries = 3
    for i in range(retries):
        try:
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            result = response.json()
            if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error("AIからのレスポンスが予期せぬ形式です。")
                return None
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                time.sleep(2 ** i) # 指数バックオフ
                continue
            else:
                st.error(f"API呼び出し中にエラーが発生しました: {e}")
                return None


def display_ai_insights(df: pd.DataFrame):
    """
    AIによるインサイト生成のUIとロジックを表示します。
    """
    st.subheader("AIによるデータインサイト生成")
    st.write("データについて知りたいことを質問してください。AIがデータ全体を分析し、インサイトを生成します。")

    # ユーザーの質問
    user_prompt = st.text_area("質問を入力してください:", value="このデータセットから重要な傾向とインサイトを日本語で教えてください。", height=150)
    
    # 実行ボタン
    if st.button("AIに分析を依頼"):
        st.session_state.ai_analysis_triggered = True

    if st.session_state.ai_analysis_triggered:
        if not df.empty:
            with st.spinner("分析を実行中...しばらくお待ちください。"):
                # AIへのプロンプトを準備
                data_preview = df.head(50).to_string()
                prompt = f"""
                以下のデータセットのサンプルを分析し、ユーザーの質問に答えてください。
                データはCSV形式で提供されており、以下の部分的な内容を参照できます。
                
                データ:
                {data_preview}
                
                ユーザーの質問:
                {user_prompt}
                
                回答は、具体的なデータに基づいた洞察、傾向、および結論を含め、詳細でわかりやすい日本語で記述してください。
                """
                
                insight_text = get_ai_insight(prompt)
                st.session_state.ai_insight_text = insight_text
                st.session_state.ai_analysis_triggered = False # リセット
                st.rerun()
        else:
            st.warning("先にデータをアップロードまたは入力してください。")
            st.session_state.ai_analysis_triggered = False # リセット
            st.rerun()

    if st.session_state.ai_insight_text:
        st.success("分析が完了しました！")
        st.markdown(st.session_state.ai_insight_text)
