# Dockerfile

# ベースイメージの指定: Python 3.9 (Alpine版は軽量なLinuxディストリビューション)
FROM python:3.9-slim-buster

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# ホストのrequirements.txtをコンテナの作業ディレクトリにコピー
# これにより、必要なライブラリをインストールできるようになる
COPY requirements.txt ./

# Pythonのライブラリをインストール
# --no-cache-dir: キャッシュを使わないことでイメージサイズを小さくする
# --upgrade pip: pip自体を最新版にアップグレードする
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Streamlitのポート（8501）を公開する設定
EXPOSE 8501

# ホストの現在のディレクトリにある全てのファイルをコンテナの作業ディレクトリにコピー
# app.py, components/ フォルダなどが含まれる
COPY . .

# アプリケーション起動コマンド
# コンテナが起動したときに実行されるコマンド
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]