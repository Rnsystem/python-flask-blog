# Flask + FileMaker Blog

![License](https://img.shields.io/badge/license-MIT-blue.svg) 
![Python](https://img.shields.io/badge/python-3.x-blue) 
![Flask](https://img.shields.io/badge/flask-lightgrey) 
![FileMaker](https://img.shields.io/badge/FileMaker-Data%20API-red)  
[![Author](https://img.shields.io/badge/author-RyohmaU-lightgrey)](https://rnsystem.jp)

---

## 💻 完成ビューサンプル

| PCビュー |
|-----------|
| ![PC Preview](images/sample01.jpg) |

| スマホビュー |
|-----------|
| ![スマホ Preview](images/sample02.jpg) |

---

Python（Flask）で実装したブログシステムです。記事データは **FileMaker Server** 上で管理し、**FileMaker Data API** 経由で読み書きします。  
FileMaker を使うことで **非エンジニアでも運用・保守しやすい** 設計を目指しています。

---

## 概要 / Overview

- シンプルなブログ表示（トップ / 記事 / カテゴリ）  
- FileMaker Data API を使ったデータ取得・更新  
- WebSocket（flask-socketio）によるリアルタイム通知（問い合わせチャット等）  
- Stripe 決済連携（オプション）  
- reCAPTCHA を用いたフォーム保護

---

## 主な特徴 / Features

- FileMaker 管理で運用性が高い（メンテ担当がGUIで編集可能）  
- 非同期でのデータ取得（バックグラウンドスレッド）により初期表示を軽く  
- 画像配信エンドポイント（FileMaker の画像ストレージを参照）  
- Slack 連携（問い合わせ → Slack チャネル作成／通知）  
- 環境変数で全ての機密情報を管理（`.env`）

---

## 技術スタック / Tech Stack

- Python Python 3.11.9  
- Flask, Flask-SocketIO, Flask-CORS, Flask-WTF  
- Claris FileMaker 2025
- FileMaker Data API (via `api_filemaker` モジュール)  
- Stripe（`api_stripe` モジュール）  
- その他：requests, python-dotenv, wtforms

---

## セットアップ（開発向け）

1. リポジトリをクローン

```bash
git clone https://github.com/Rnsystem/python-flask-blog.git
cd python-flask-blog/src
```

2. 仮想環境作成・有効化（Windows example）

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

4. .env をプロジェクト直下（src）に作成（下に .env.example あり）
5. アプリ起動

```bash
python app.py
```

---

- .env.example（必ず実値は入れずにコピーして使用）
```bash
# FileMaker
FILEMAKER_HOST=https://your-fms.example.com
FILEMAKER_DATABASE=blog
FILEMAKER_USER=your_user
FILEMAKER_PASSWORD=your_password
FILEMAKER_VERIFY_SSL=true

# Slack
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxxxxxxxxx
SLACK_CHANNEL_PREFIX=customer-

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxx
PAYMENT_SUCCESS_URL=https://yourdomain.example/payment/success
PAYMENT_CANCEL_URL=https://yourdomain.example/payment/cancel

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY=your_site_key
RECAPTCHA_PRIVATE_KEY=your_secret_key

# Flask
FLASK_SECRET_KEY=your-secret-key
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Admin users (comma separated)
ADMIN_USERS=U03V50E65JN

# Image folders (FileMaker mount path or local)
IMAGE_FOLDER_MAIN=/path/to/main/image_obj
IMAGE_FOLDER_SUB=/path/to/sub/image_obj
IMAGE_FOLDER_WRITERS=/path/to/writers/image_obj
```

> 重要: .env（実値入り）は必ず .gitignore に追加してください。
> 公開済みトークンがある場合は直ちにローテーション（再発行）を行ってください。

---

## 主要エンドポイント
- GET / → /top にリダイレクト
- GET /top → トップページ（キャッシュあり）
- GET /blog/<code> → 記事ページ
- GET /category/<code> → カテゴリ一覧
- GET /image/fm/.../<filename> → 画像配信（設定されている場合）
- POST /payment/create-checkout-session → Stripe チェックアウト作成
- POST /send_message → reCAPTCHA 検証後 Slack へ送信（WebSocket と併用）

---

## 運用メモ / Deployment notes
- 本番では OS 環境変数や Secrets Manager（AWS/GCP/Azure）を使用することを推奨。
- FileMaker Data API の CORS / SSL 設定を確認してください（API が外部からアクセス可能であること）。
- Slack/Stripe のトークンは最小権限で発行すること。
- IMAGE_FOLDER_* はデプロイ先でマウントされるパスを指定してください（未設定時は画像ルートは 404 を返す実装推奨）

---

## セキュリティ注意
- .env を誤ってコミットした場合は即時にトークンをローテーションし、リポジトリ履歴から削除してください。
- ログに機密値が出力されないよう print() 等に注意してください。
- FLASK_SECRET_KEY は本番ではランダムで長い文字列を使用してください。

---

## 🧑‍💻 作者

**Ryohma U.**  
ポートフォリオ：[https://www.rnsystem.jp](https://www.rnsystem.jp)

---

> 💡 **補足**  
> このコードは教育・学習目的で公開しています。  
> 実運用時は必ず `.env` や FileMaker レイアウト・フィールド名を各環境に合わせて設定してください。
