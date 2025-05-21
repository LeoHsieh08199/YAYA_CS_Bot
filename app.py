from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = '你的 Channel access token'
LINE_CHANNEL_SECRET = '你的 Channel secret'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Sheets 連線設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("YAYA_CS").sheet1
data = sheet.get_all_records()

# 查詢函式
def search_solution(keyword):
    for row in data:
        if keyword in row['問題描述']:
            return f"📱 機型：{row['機型']}\n❓ 問題：{row['問題描述']}\n✅ 解決方案：{row['解決方案']}"
    return "找不到相關解決方案，請試試其他關鍵字。"

# Flask 應用
app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    keyword = event.message.text.strip()
    reply = search_solution(keyword)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
