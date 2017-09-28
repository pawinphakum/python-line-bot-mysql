from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import sqlite3
import random
import os
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('DB_SCHEMA')
mysql.init_app(app)

line_bot_api = LineBotApi('CEVP2r/YR77YziQNKaJWiynlA5iABxA2/vy5/O2IFLZCkO6hwW1kaoPQP2HCbENKmn/N5Xv3LqwgLn3wlyWEsHzdsi83xJjB/vH7/Y7VM9BLVs6AykBq2/OhOScCkHyBEdaC39SJnVdU+daEzzQgrQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2a1d3c17a4ef843a5d06ec04073a2776')

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as Text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: '+body)

    # handler webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # conn = sqlite3.connect('chat.db')
    conn = mysql.connect()
    c = conn.cursor()

    q = event.message.text.strip(' ')
    print('q=:'+q+':')

    if q.startswith('.'):
        firstSpace = q.find(' ')
        if firstSpace > 0:
            k = q[1:firstSpace]
            if k:
                v = q[firstSpace+1:]
                print('k=:'+k+':')
                print('v=:'+v+':')
                queryString = (k)
                c.execute('SELECT answer FROM chat WHERE question = %s', queryString)
                fname = c.fetchone()
                if fname:
                    queryString = (v, k)
                    c.execute('UPDATE chat SET answer = %s WHERE question = %s', queryString)
                    conn.commit()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='update...OK'))
                else:
                    queryString = (k, v)
                    c.execute('INSERT INTO chat (question, answer) VALUES (%s, %s)', queryString)
                    conn.commit()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='insert...OK'))


    queryString = (q)
    c.execute('SELECT answer FROM chat WHERE question = %s', queryString)
    a = c.fetchone()
    if a:
        print(a[0])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=a[0]))
    else:
        if queryString.find('อับดุล') > -1:
            foo = ['เรียกผมเหรอครับ', 'วาจังดายย', 'อะไรวะ', 'เรียกอยู่ได้', 'ถาหาขาไพ?่', 'Zzzz', 'ครับครับ', 'ย๊างหมอ']
            randAns = random.choice(foo)
            # print(randAns)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=randAns))

    c.close()
    conn.close()

if __name__ == '__main__':
    app.run()
