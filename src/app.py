# flask
from flask import Flask, request, render_template, send_from_directory, abort, jsonify, redirect, url_for, flash
# 画像提供用のルート設定
from flask import send_from_directory
# flask_socketio WebSocket接続を行うのに使用
from flask_socketio import SocketIO, emit
# 時間のかかる処理を別スレッドで実行するのに使用
from threading import Thread
# 異なるオリジン間のリクエストを許可するのに使用
from flask_cors import CORS
# リアルタイム通信用
from flask_socketio import SocketIO, emit
# 複数のスレッドを使用してPythonプログラムを並列実行するためのツール
import threading
# SSL
import ssl
# URLエンコード、デコード用
import urllib.parse
# システムパッケージ
import sys
import os
# リクエスト
import requests
# json
import json
# FIleMakerAPIの呼び出し
# from odbc_filemaker import FileMaker
from api_filemaker import FileMakerDataAPI
# 時間待機に使用
import time
# UUIDを使用
import uuid
# 決済方法stripeを追加
# stripe
from api_stripe import StripeAPI
# 問い合わせフォーム用
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
# 環境変数読み込み用
from dotenv import load_dotenv
load_dotenv()  # プロジェクト直下の .env を読み込む

def getenv_or_none(key):
    """環境変数が空文字または未設定なら None を返す"""
    value = os.getenv(key)
    return value if value not in (None, "", "null", "None") else None

# クライアントごとの識別情報を管理（session_id: WebSocketの接続）
clients = {}
# お客様のセッションIDとSlackチャンネルを管理する辞書
session_channels = {}
# **各セッションの最終アクティビティを記録**
session_activity = {}
# 各セッションの待機時間（秒）
SESSION_WAIT_TIME = 300


# ADMIN_USERS（カンマ区切り）
# ADMIN_USERS（カンマ区切り → 空なら None）
admin_users_str = getenv_or_none('ADMIN_USERS')
ADMIN_USERS = [u.strip() for u in admin_users_str.split(',')] if admin_users_str else None

# FileMaker
API_FILEMAKER_BLOG_INFO = {
    'host': getenv_or_none('FILEMAKER_HOST'),
    'database': getenv_or_none('FILEMAKER_DATABASE'),
    'user': getenv_or_none('FILEMAKER_USER'),
    'password': getenv_or_none('FILEMAKER_PASSWORD'),
    'verify_ssl': getenv_or_none('FILEMAKER_VERIFY_SSL'),
}

# Slack
SLACK_BOT_TOKEN = getenv_or_none('SLACK_BOT_TOKEN')
SLACK_CHANNEL_PREFIX = getenv_or_none('SLACK_CHANNEL_PREFIX')
SLACK_HEADERS = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}" if SLACK_BOT_TOKEN else "",
    "Content-Type": "application/json"
}

# 画像フォルダ
IMAGE_FOLDER_FILEMAKER_BLOG_MAINCONTENTS = getenv_or_none('IMAGE_FOLDER_MAIN')
IMAGE_FOLDER_FILEMAKER_BLOG_SUBCONTENTS = getenv_or_none('IMAGE_FOLDER_SUB')
IMAGE_FOLDER_FILEMAKER_BLOG_WRITERCONTENT_WRITERS = getenv_or_none('IMAGE_FOLDER_WRITERS')

# Stripe
STRIPE_SECRET_KEY = getenv_or_none('STRIPE_SECRET_KEY')
PAYMENT_SUCCESS_URL = getenv_or_none('PAYMENT_SUCCESS_URL')
PAYMENT_CANCEL_URL = getenv_or_none('PAYMENT_CANCEL_URL')

# グローバル変数でデータを保持する
data_cache = {}

# webアプリ起動 
app = Flask(__name__)

# リアルタイム通信用ソケット定義
socketio = SocketIO(app, cors_allowed_origins="*")

# reCAPTCHA
app.config['RECAPTCHA_PUBLIC_KEY'] = getenv_or_none('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = getenv_or_none('RECAPTCHA_PRIVATE_KEY')

# Flask secret key
secret_key = getenv_or_none('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = secret_key if secret_key else os.urandom(24)

CORS(app)

# appに対してのsoketIOを生成
socketio = SocketIO(app, cors_allowed_origins="*")

# 画像提供先の設定
# blog_maincontents
@app.route('/image/fm/blog/blog_maincontents/image_obj/<filename>')
def image_file_blog_maincontents(filename):
    return send_from_directory(IMAGE_FOLDER_FILEMAKER_BLOG_MAINCONTENTS, filename)
# blog_subcontents
@app.route('/image/fm/blog/blog_subcontents/image_obj/<filename>')
def image_file_blog_subcontents(filename):
    return send_from_directory(IMAGE_FOLDER_FILEMAKER_BLOG_SUBCONTENTS, filename)
# blog_writercontent_writers
@app.route('/image/fm/blog/blog_writercontent_writers/image_obj/<filename>')
def image_file_blog_writercontent_writers(filename):
    return send_from_directory(IMAGE_FOLDER_FILEMAKER_BLOG_WRITERCONTENT_WRITERS, filename)

# favicon
@app.route('/icon/icon32.ico')
def handle_favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'image'),'favicon.ico', mimetype='favicon.ico')

# root
@app.route('/', methods=["GET"])
def handle_root():
    return redirect(url_for('handle_top'))

# top
@app.route('/top', methods = ["GET"])
def handle_top():
    # グローバル変数にアクセス
    global data_cache
    redirectURL = '/top'
    # if code in data_cache:
    if redirectURL in data_cache:
        # キーが存在する場合の処理
        fm_get_data= data_cache.get(redirectURL, "No data available")  # データがない場合のデフォルトメッセージ
        return render_template('index.html', top_contents=fm_get_data)
    else:
        # キーが存在しない場合の処理
        # 時間のかかる処理を別スレッドで実行
        thread = Thread(target=fetch_data, args=('top', None, redirectURL,))
        thread.start()
        # クライアントに「loading.html」を返す
        return redirect(url_for('handle_loading', redirectURL=redirectURL))

# privacy
@app.route('/privacy', methods = ["GET"])
def handle_privacy():
    return render_template('privacy.html')

# privacy_iframe
@app.route('/privacy_iframe', methods = ["GET"])
def handle_privacy_iframe():
    return render_template('privacy_iframe.html')

# company
@app.route('/company', methods = ["GET"])
def handle_company():
    return render_template('company.html')

# contact
@app.route('/contact', methods = ["GET","POST"])
def handle_contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        content = request.form.get('content')
        agree = request.form.get('agree')
        recaptcha_response = request.form.get('g-recaptcha-response')  # reCAPTCHAのレスポンス
        # バリデーション
        errors = {}
        if not name:
            errors['name_error'] = '名前を入力してください。'
        elif len(name) > 20:
            errors['name_error'] = '名前は全角20字以内で入力してください。'
        if not email:
            errors['email_error'] = 'メールアドレスを入力してください。'
        elif not check_email_format(email):
            errors['email_error'] = 'メールアドレス形式が正しくありません。'
        if not content:
            errors['content_error'] = 'お問い合わせ内容を入力してください。'
        elif len(content) > 2000:
            errors['content_error'] = 'お問い合わせ内容は全角2000文字以内で入力してください。'
        if not agree:
            errors['agree_error'] = '個人情報保護ポリシーに同意してください。'
        # reCAPTCHA検証
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            errors['recaptcha_error'] = 'reCAPTCHAの検証に失敗しました。もう一度お試しください。'
        # エラーがある場合、エラーメッセージを表示
        if errors:
            for field, message in errors.items():
                flash(message, field)
            return render_template('contact.html')

        # ここでフォームの処理を行う（例: メール送信、データベース保存など）
        # 成功メッセージを表示してリダイレクト
        flash('お問い合わせ内容を送信しました。', 'success')
        return redirect(url_for('handle_contact'))
    return render_template('contact.html')

# emailのフォーマット確認
def check_email_format(email):
    """メールアドレスの簡易的な形式チェック"""
    import re
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)
# Google reCAPTCHAの検証を行う関数
def verify_recaptcha(recaptcha_response):
    """Google reCAPTCHAの検証を行う関数"""
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': app.config['RECAPTCHA_PRIVATE_KEY'],
        'response': recaptcha_response
    }
    r = requests.post(url, data=data)
    result = r.json()
    return result.get('success', False)

# checkout/success
@app.route('/payment/success', methods=['GET'])
def payment_success():
    return render_template('payment_success.html')

# checkout/cancel
@app.route('/payment/cancel', methods=['GET'])
def payment_cancel():
    return render_template('payment_cancel.html')

# checkout(テスト用)
@app.route('/payment/checkout', methods=['GET'])
def payment_checkout():
    return render_template('payment_checkout.html')  # フロントエンドで決済ページを作成

# create-checkout-session
@app.route('/payment/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # JavaScriptから送信されたJSONデータを取得
    data = request.get_json()
    # 'stripe_price_id'を取得
    stripe_price_id = data.get('stripe_price_id')
    stripe_quantity = data.get('stripe_quantity')
    items = [
        {
            'price': stripe_price_id,  # 価格ID
            'quantity': stripe_quantity,  # 購入する数量
        }
    ]
    # StripeAPIクラスの呼出
    s_api = StripeAPI(STRIPE_SECRET_KEY)
    res = s_api.post_checkout(PAYMENT_SUCCESS_URL, PAYMENT_CANCEL_URL, *items)
    # 決済判定
    if res['code'] == 200:
        return jsonify({'id': res['id']})
    else:
        return jsonify(error=str(res['message'])), 403

# loading
@app.route('/loading', methods=["GET"])
def handle_loading():
    # ここでクエリパラメータを取得
    redirectURL = request.args.get('redirectURL')
    return render_template('loading.html' ,redirectURL=redirectURL)

# blog
@app.route('/blog/<string:code>', methods = ["GET"])
def handle_blog(code):
    # グローバル変数にアクセス
    global data_cache
    redirectURL = '/blog/'+code
    # if code in data_cache:
    if redirectURL in data_cache:
        # キーが存在する場合の処理
        fm_get_data= data_cache.get(redirectURL, "No data available")  # データがない場合のデフォルトメッセージ
        return render_template('blog.html', blog=fm_get_data)
    else:
        # キーが存在しない場合の処理
        # 時間のかかる処理を別スレッドで実行
        thread = Thread(target=fetch_data, args=('blog',code,redirectURL,))
        thread.start()
        # クライアントに「loading.html」を返す
        return redirect(url_for('handle_loading', redirectURL=redirectURL))


# /category にアクセスされた場合は /category/non にリダイレクト
@app.route('/category/', methods=["GET"])
def handle_category_empty():
    return redirect(url_for('handle_category', code='non'))

# category
@app.route('/category/<string:code>', methods = ["GET"])
def handle_category(code):
    # グローバル変数にアクセス
    global data_cache
    redirectURL = '/category/'+code
    # if code in data_cache:
    if redirectURL in data_cache:
        # キーが存在する場合の処理
        fm_get_data= data_cache.get(redirectURL, "No data available")  # データがない場合のデフォルトメッセージ
        return render_template('category.html', blogs=fm_get_data)
    else:
        # キーが存在しない場合の処理
        # 時間のかかる処理を別スレッドで実行
        thread = Thread(target=fetch_data, args=('category', code, redirectURL,))
        thread.start()
        # クライアントに「loading.html」を返す
        return redirect(url_for('handle_loading', redirectURL=redirectURL))

# `/message` にアクセスしたときのみ WebSocket を有効化
@app.route("/message", methods=["GET"])
def message_page():
    return render_template("message.html", recaptcha_site_key=app.config['RECAPTCHA_PUBLIC_KEY'])

# クライアント接続時に `session_id` を生成して管理
@socketio.on("connect", namespace="/message")
def handle_connect():
    session_id = str(uuid.uuid4())  # ユニークIDを生成
    clients[session_id] = request.sid  # WebSocketのセッションIDを保存
    emit("session_id", session_id)  # クライアントに `session_id` を送信
    print(f"新しいクライアント接続: {session_id}")

#  """クライアントが切断したときの処理"""
@socketio.on("disconnect", namespace="/message")
def handle_disconnect():
    session_id = None
    # クライアントのセッションIDを探す
    for sid, client_sid in clients.items():
        if client_sid == request.sid:
            session_id = sid
            break
    if session_id:
        print(f"クライアント {session_id} が切断しました。セッションを削除します。")

        # **セッション情報を削除**
        if session_id in clients:
            del clients[session_id]
        if session_id in session_channels:
            del session_channels[session_id]
        if session_id in session_activity:
            del session_activity[session_id]

# **reCAPTCHAを検証してメッセージをSlackに送信**
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    msg = data.get("message")
    session_id = data.get("session_id")
    recaptcha_response = data.get("g-recaptcha-response")

    if not session_id or not msg:
        return jsonify({"status": "error", "error": "セッションIDまたはメッセージが空です"}), 400

    # **reCAPTCHA 検証**
    if not recaptcha_response or not verify_recaptcha(recaptcha_response):
        return jsonify({"status": "error", "error": "reCAPTCHA の検証に失敗しました"}), 403

    print(f"Received message from {session_id}: {msg}")

    # Slackのチャンネルを取得 or 作成
    channel_id = get_or_create_slack_channel(session_id)
    
    if channel_id:
        slack_data = {
            "channel": channel_id,
            "text": f"ユーザーのメッセージ: {msg}",
            "username": "ChatBot"
        }
        response = requests.post("https://slack.com/api/chat.postMessage", headers=SLACK_HEADERS, json=slack_data)

        if response.status_code == 200 and response.json().get("ok"):
            print(f"Slackにメッセージ送信成功: {msg}")
            session_activity[session_id] = time.time()
            return jsonify({"status": "ok"})
        else:
            print(f"Slackメッセージ送信エラー: {response.json()}")
            return jsonify({"status": "error", "error": "Slackメッセージ送信に失敗しました"}), 500
    return jsonify({"status": "error", "error": "Slackチャンネルが取得できませんでした"}), 500


# クライアントとリアルタイム通信 (namespace `/message`)
@socketio.on("message", namespace="/message")
def handle_message(data):
    msg = data.get("msg")
    session_id = data.get("session_id")
    if not session_id:
        print("エラー: session_id が None")
        return
    # **セッションが途絶えたメッセージを受け取ったら削除**
    if "セッションが途絶えました" in msg:
        print(f"セッション {session_id} が終了しました。セッションデータを削除します。")
        if session_id in clients:
            del clients[session_id]
        if session_id in session_channels:
            del session_channels[session_id]
        if session_id in session_activity:
            del session_activity[session_id]
        return
    # Slackのチャンネルを取得 or 作成
    channel_id = get_or_create_slack_channel(session_id)
    if channel_id:
        slack_data = {
            "channel": channel_id,
            "text": f"ユーザーのメッセージ: {msg}",
            "username": "ChatBot"
        }
        response = requests.post("https://slack.com/api/chat.postMessage", headers=SLACK_HEADERS, json=slack_data)

        if response.status_code == 200 and response.json().get("ok"):
            print(f"Slackにメッセージ送信成功: {msg}")
            session_activity[session_id] = time.time()
        else:
            print(f"Slackメッセージ送信エラー: {response.json()}")


@app.route("/slack", methods=["POST"])
def slack_webhook():
    data = request.json

    # Slack の URL 検証リクエストに対応
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

    event = data.get("event", {})
    text = event.get("text", "")
    user_id = event.get("user", "")
    channel_id = event.get("channel", "")
    subtype = event.get("subtype", "")

    # **システム通知を除外（subtype がある場合はシステムメッセージ）**
    if subtype or not user_id:
        print(f"システムメッセージを除外: {text}")  # デバッグログ
        return jsonify({"status": "ignored"}), 200

    # **指定されたユーザー (`ADMIN_USERS`) のみメッセージを送信**
    if user_id not in ADMIN_USERS:
        print(f"許可されていないユーザー {user_id} のメッセージを無視: {text}")  # デバッグログ
        return jsonify({"status": "ignored"}), 200

    # session_id を検索
    session_id = None
    for key, value in session_channels.items():
        if value == channel_id:
            session_id = key
            break

    # **クライアントにメッセージを送信**
    if session_id and session_id in clients:
        socketio.emit("message", text, room=clients[session_id], namespace="/message")

    return jsonify({"status": "ok"}), 200


# **Slackのチャンネルを作成または取得**
def get_or_create_slack_channel(session_id):
    if session_id in session_channels:
        return session_channels[session_id]

    channel_name = f"{SLACK_CHANNEL_PREFIX}{session_id}"

    # **既存のチャンネルを検索**
    list_url = "https://slack.com/api/conversations.list"
    response = requests.get(list_url, headers=SLACK_HEADERS)

    if response.status_code == 200:
        channels = response.json().get("channels", [])
        for channel in channels:
            if channel["name"] == channel_name:
                session_channels[session_id] = channel["id"]
                return channel["id"]

    # **新規チャンネルを作成**
    create_url = "https://slack.com/api/conversations.create"
    data = {"name": channel_name}
    response = requests.post(create_url, headers=SLACK_HEADERS, json=data)

    if response.status_code == 200 and response.json().get("ok"):
        channel_id = response.json()["channel"]["id"]
        session_channels[session_id] = channel_id
        invite_users_to_channel(channel_id, ADMIN_USERS)
        return channel_id
    return None

# **指定ユーザーをチャンネルに招待**
def invite_users_to_channel(channel_id, users):
    invite_url = "https://slack.com/api/conversations.invite"
    data = {"channel": channel_id, "users": ",".join(users)}
    response = requests.post(invite_url, headers=SLACK_HEADERS, json=data)
    if response.status_code == 200 and response.json().get("ok"):
        print(f"指定ユーザーをチャンネルに招待: {users}")


# **SESSION_WAIT_TIME分間アクティビティがないセッションを終了する関数**
def check_inactive_sessions():
    current_time = time.time()
    inactive_sessions = []

    for session_id, last_time in session_activity.items():
        if current_time - last_time > SESSION_WAIT_TIME:  # セッションが一定時間アクティブでない場合
            channel_id = session_channels.get(session_id)

            if channel_id:
                print(f"セッション {session_id} が {SESSION_WAIT_TIME} 秒間アクティビティなし。終了処理を実行。")

                # **管理者 (`ADMIN_USERS`) をチャンネルから削除**
                remove_admin_users_from_channel(channel_id)

                # **Slackに「セッション終了」メッセージを投稿**
                message = f"{SESSION_WAIT_TIME}秒間通信がなかったため、セッションが終了しました。"
                slack_data = {"channel": channel_id, "text": message}
                requests.post("https://slack.com/api/chat.postMessage", headers=SLACK_HEADERS, json=slack_data)

                # **ボットをチャンネルから退出**
                requests.post("https://slack.com/api/conversations.leave", headers=SLACK_HEADERS, json={"channel": channel_id})

                # **チャンネルをアーカイブ**
                requests.post("https://slack.com/api/conversations.archive", headers=SLACK_HEADERS, json={"channel": channel_id})

                # **Webクライアントにもセッション終了を通知**
                if session_id in clients:
                    socketio.emit("message", message, room=clients[session_id], namespace="/message")

                inactive_sessions.append(session_id)

    # **終了したセッションを削除**
    for session_id in inactive_sessions:
        del session_activity[session_id]
        del session_channels[session_id]
        if session_id in clients:
            del clients[session_id]

    # **継続的に実行するためのタイマー**
    threading.Timer(SESSION_WAIT_TIME, check_inactive_sessions).start()



# **ADMIN_USERS のみをチャンネルから削除する関数**
def remove_admin_users_from_channel(channel_id):
    # **チャンネルのメンバーを取得**
    members_url = "https://slack.com/api/conversations.members"
    response = requests.get(members_url, headers=SLACK_HEADERS, params={"channel": channel_id})

    if response.status_code == 200:
        resp_json = response.json()
        if resp_json.get("ok"):
            members = resp_json["members"]
            print(f"チャンネル {channel_id} のメンバー一覧: {members}")

            # **ADMIN_USERS のみを強制退出**
            for user_id in ADMIN_USERS:
                if user_id in members:
                    kick_url = "https://slack.com/api/conversations.kick"
                    kick_data = {"channel": channel_id, "user": user_id}
                    kick_response = requests.post(kick_url, headers=SLACK_HEADERS, json=kick_data)

                    if kick_response.status_code == 200 and kick_response.json().get("ok"):
                        print(f"管理者 {user_id} をチャンネル {channel_id} から削除しました。")
                    else:
                        print(f"管理者削除エラー: {kick_response.json()}")

        else:
            print(f"メンバー取得エラー: {resp_json}")
    else:
        print(f"メンバー取得HTTPエラー: {response.json()}")


# 時間がかかる処理をバックグラウンドで実行する関数
def fetch_data(type, code, redirectURL):
    time.sleep(2)
    # グローバル変数にアクセス
    global data_cache 
    # クライアントに対して「読み込み中」であることを通知
    socketio.emit('loading', {'data': 'データ取得中...', 'redirectURL': redirectURL, 'code': code})
    print('loading...')
    if 'top' in type:
        # fmデータ取得
        fm_get_data = get_fm_top()
    elif 'blog' in type:
        # fmデータ取得
        fm_get_data = get_fm_blog(code)
        # stripeデータ取得
        if fm_get_data['sale_flag'] == 1 and len(fm_get_data['sale_price_id']) > 0:
            # StripeAPIクラスの呼出
            s_api = StripeAPI(STRIPE_SECRET_KEY)
            fm_get_data['stripeContentList'] = s_api.find_price(fm_get_data['sale_price_id'])
    elif 'category' in type:
        # fmデータ取得
        fm_get_data = get_fm_category(code)
    # データをグローバル変数に保存
    # data_cache[code] = fm_get_data
    data_cache[redirectURL] = fm_get_data
    # クライアントに対して処理が完了したことを通知
    socketio.emit('loaded', {'data': 'データ取得しました。', 'redirectURL': redirectURL, 'code': code})
    # print(fm_get_data)
    print('loaded.')

# get_fm_top取得
def get_fm_top() -> list:
    fm_record_top = get_api_filemaker_top( 'sv_blogs', 'sort', 'ascend', 10)
    if len(fm_record_top) > 0:
        # records
        res_dict_list = []
        for record in fm_record_top:
            # print(record)
            res_dict = {}
            # fileds
            for k, v in record.items():
                res_dict[k] = v
            fm_record_blog_id = record['主キー']
            # main contents
            fm_record_blog_maincontents = get_api_filemaker_blog( 'sv_blog_maincontents', 'blog_id', fm_record_blog_id)
            if len(fm_record_blog_maincontents) > 0:
                res_dict['mainContentList'] = fm_record_blog_maincontents
            # sub contents
            fm_record_blog_subcontents = get_api_filemaker_blog( 'sv_blog_subcontents', 'blog_id', fm_record_blog_id)
            if len(fm_record_blog_subcontents) > 0:
                res_dict['subContentList'] = fm_record_blog_subcontents
            # writer contents
            fm_record_blog_writercontents = get_api_filemaker_blog( 'sv_blog_writercontents', 'blog_id', fm_record_blog_id)
            if len(fm_record_blog_writercontents) > 0:
                res_list = []
                for fm_record_blog_writercontent in fm_record_blog_writercontents:
                    fm_record_blog_writercontent_id = fm_record_blog_writercontent['blog_writercontent_writer_id']
                    fm_record_blog_writers = get_api_filemaker_blog( 'sv_blog_writercontent_writers', '主キー', fm_record_blog_writercontent_id)
                    if len(fm_record_blog_writers) > 0:
                        res_list.append(fm_record_blog_writers[0])
                res_dict['writerContentList'] = res_list
            # category contents
            fm_record_blog_categorycontents = get_api_filemaker_blog( 'sv_blog_categorycontents', 'blog_id', fm_record_blog_id)
            if len(fm_record_blog_categorycontents) > 0:
                res_list = []
                for fm_record_blog_categorycontent in fm_record_blog_categorycontents:
                    fm_record_blog_categorycontent_id = fm_record_blog_categorycontent['blog_categorycontent_category_id']
                    fm_record_blog_categories = get_api_filemaker_blog( 'sv_blog_categorycontent_categories', '主キー', fm_record_blog_categorycontent_id)
                    if len(fm_record_blog_categories) > 0:
                        res_list.append(fm_record_blog_categories[0])
                res_dict['categoryContentList'] = res_list
            res_dict_list.append(res_dict)
        # print("res_dict_list")
        # print(res_dict_list)
        return res_dict_list
    else:
        print('fm_record_blog is no record.')
        return {}


# get_fm_category取得
def get_fm_category(code) -> dict:
    # category
    fm_record_category = get_api_filemaker_blog( 'sv_blog_categorycontent_categories', 'code', code)
    if len(fm_record_category) > 0:
        # records
        res_dict_list = []
        fm_record_category_id = fm_record_category[0]['主キー']
        # category contents
        fm_record_blog_categorycontents = get_api_filemaker_blog( 'sv_blog_categorycontents', 'blog_categorycontent_category_id', fm_record_category_id)
        if len(fm_record_blog_categorycontents) > 0:
            for fm_record_blog_categorycontent in fm_record_blog_categorycontents:
                # blogs
                fm_record_blog_id = fm_record_blog_categorycontent['blog_id']
                fm_record_blog = get_api_filemaker_blog( 'sv_blogs', '主キー', fm_record_blog_id)
                if len(fm_record_blog) > 0:
                    # main contents
                    fm_record_blog_maincontents = get_api_filemaker_blog( 'sv_blog_maincontents', 'blog_id', fm_record_blog_id)
                    if len(fm_record_blog_maincontents) > 0:
                        val = {
                            'categoryContentList':fm_record_category[0],
                            'blogContentList':fm_record_blog[0],
                            'mainContentList':fm_record_blog_maincontents[0]
                        }
                        res_dict_list.append(val)
        return res_dict_list
    else:
        print('fm_record_blog is no record.')
        return {}


# get_fm_blog取得
def get_fm_blog(code) -> dict:
    fm_record_blog = get_api_filemaker_blog( 'sv_blogs', 'code', code)
    if len(fm_record_blog) > 0:
        res_dict = {}
        for k, v in fm_record_blog[0].items():
            res_dict[k] = v
        fm_record_blog_id = fm_record_blog[0]['主キー']
        # main contents
        fm_record_blog_maincontents = get_api_filemaker_blog( 'sv_blog_maincontents', 'blog_id', fm_record_blog_id)
        if len(fm_record_blog_maincontents) > 0:
            res_dict['mainContentList'] = fm_record_blog_maincontents
        # sub contents
        fm_record_blog_subcontents = get_api_filemaker_blog( 'sv_blog_subcontents', 'blog_id', fm_record_blog_id)
        if len(fm_record_blog_subcontents) > 0:
            res_dict['subContentList'] = fm_record_blog_subcontents
        # writer contents
        fm_record_blog_writercontents = get_api_filemaker_blog( 'sv_blog_writercontents', 'blog_id', fm_record_blog_id)
        if len(fm_record_blog_writercontents) > 0:
            res_list = []
            for fm_record_blog_writercontent in fm_record_blog_writercontents:
                fm_record_blog_writercontent_id = fm_record_blog_writercontent['blog_writercontent_writer_id']
                fm_record_blog_writers = get_api_filemaker_blog( 'sv_blog_writercontent_writers', '主キー', fm_record_blog_writercontent_id)
                if len(fm_record_blog_writers) > 0:
                    res_list.append(fm_record_blog_writers[0])
            res_dict['writerContentList'] = res_list
        # category contents
        fm_record_blog_categorycontents = get_api_filemaker_blog( 'sv_blog_categorycontents', 'blog_id', fm_record_blog_id)
        if len(fm_record_blog_categorycontents) > 0:
            res_list = []
            for fm_record_blog_categorycontent in fm_record_blog_categorycontents:
                fm_record_blog_categorycontent_id = fm_record_blog_categorycontent['blog_categorycontent_category_id']
                fm_record_blog_categories = get_api_filemaker_blog( 'sv_blog_categorycontent_categories', '主キー', fm_record_blog_categorycontent_id)
                if len(fm_record_blog_categories) > 0:
                    res_list.append(fm_record_blog_categories[0])
            res_dict['categoryContentList'] = res_list
            # print(res_list)
        return res_dict
    else:
        print('fm_record_blog is no record.')
        return {}

# api_filemaker top取得
def get_api_filemaker_top(tablename, fieldname, sort, limit) -> list:
    try:
        # 接続を確立します
        api_fm_blog = FileMakerDataAPI(**API_FILEMAKER_BLOG_INFO)
        # クエリを実行します
        query = {"display_flag": "1"}
        sort_order = [{
            "fieldName": fieldname,
            "sortOrder": sort
        }]
        records = api_fm_blog.find_records(layout=tablename, query=query, sort=sort_order, limit=limit)
        return records
    except requests.exceptions.RequestException as e:
        print("HTTP通信エラー:", e)
        return []

    except ValueError as e:
        print("値エラー（たとえばJSON decode失敗など）:", e)
        return []

    except Exception as e:
        print("その他のエラー:", e)
        return []

# api_filemaker blog取得
def get_api_filemaker_blog(tablename, fieldname, fieldvalue) -> list:
    print("tablename：{} , fieldname：{}, fieldvalue{}".format(tablename, fieldname, fieldvalue))
    try:
        # 接続を確立します
        api_fm_blog = FileMakerDataAPI(**API_FILEMAKER_BLOG_INFO)
        # クエリを実行します
        query = {
                "display_flag": "1", 
                fieldname : str(fieldvalue)
            }
        sort_order = [{
            "fieldName": "sort",
            "sortOrder": "ascend"  # ascend / descend
        }]
        records = api_fm_blog.find_records(layout=tablename, query=query, sort=sort_order)
        return records
    except requests.exceptions.RequestException as e:
        print("HTTP通信エラー:", e)
        return []

    except ValueError as e:
        print("値エラー（たとえばJSON decode失敗など）:", e)
        return []

    except Exception as e:
        print("その他のエラー:", e)
        return []


# メイン
if __name__ == '__main__':
    # **サーバー起動時に1回チェックを開始**
    threading.Timer(SESSION_WAIT_TIME, check_inactive_sessions).start()
    socketio.run(app, host="0.0.0.0", port=5001)



