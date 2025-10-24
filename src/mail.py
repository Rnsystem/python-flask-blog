from smtplib import SMTP

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email.utils import formatdate
from email.utils import formataddr


def createMIMEText(mail_from, mail_from_name, mail_to, mail_to_name, mail_message, mail_subject):
    # MIMETextを作成
    msg = MIMEText(mail_message, "html")
    # msg = MIMEText(message)
    # msg = MIMEText(message, "plain", 'utf-8')
    msg["Subject"] = mail_subject
    msg["From"] = formataddr((mail_from_name, mail_from))
    msg["To"] = formataddr((mail_to_name, mail_to))
    msg['Date'] = formatdate()
    return msg


def send_email(smtp_account, smtp_password, smtp_host, smtp_port, msg=""):
    # SMTPサーバのユーザ名とパスワード
    account = smtp_account
    password = smtp_password
    host = smtp_host
    port = smtp_port
    server = SMTP(host, port)
    server.starttls()
    server.login(account, password)
    # メールを送信する
    server.send_message(msg)
    # 閉じる
    server.quit()



if __name__ == '__main__':
    print("\n----------")
    print("main")
    print('-----')
