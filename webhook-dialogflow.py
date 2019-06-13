#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

# URL を開くためのライブラリ
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

# ウェブアプリケーションフレームワーク
from flask import Flask
from flask import request
from flask import make_response

#googleSpreadsheet用のライブラリ
import gspread

#OAuth 2.0で保護されたリソースにアクセスするためのライブラリ
from oauth2client.service_account import ServiceAccountCredentials
#scope = ['https://spreadsheets.google.com/feeds']
scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

#現在日時のdatetimeオブジェクトを取得するためのライブラリ
from datetime import datetime
from pytz import timezone

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)
    # return返さないとエラーになる
    return "SUCCESS"

def processRequest(req):
    #if req.get("result").get("action") != "writeSpreadSheet":
    #    return {}

    jaw = req.get("queryResult").get("parameters").get("jaw")
    tooth_number = req.get("queryResult").get("parameters").get("tooth_number")
    virtical = req.get("queryResult").get("parameters").get("virtical")
    horizontal = req.get("queryResult").get("parameters").get("horizontal")
    depth = req.get("queryResult").get("parameters").get("depth")

    #ダウンロードしたjsonファイルを同じフォルダに格納して指定する
    credentials = ServiceAccountCredentials.from_json_keyfile_name('probing-test-project-2049bc1f32a8.json', scope)
    gc = gspread.authorize(credentials)
    # 共有設定したスプレッドシートの名前を指定する
    worksheet = gc.open("JSON_test").sheet1

    print(worksheet.cell(1,1))
    utc_now = datetime.now(timezone('UTC'))
    jst_now = utc_now.astimezone(timezone('Asia/Tokyo'))

    # シートに行を追加して記入
    #worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),pee,poo,pooStatus]);
    worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),jaw,tooth_number,horizontal,virtical,depth]);


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')