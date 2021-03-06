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

#Webhookのレスポンスを試作
import collections
from django.http.response import JsonResponse

#OAuth 2.0で保護されたリソースにアクセスするためのライブラリ
from oauth2client.service_account import ServiceAccountCredentials

#scope = ['https://spreadsheets.google.com/feeds']
#scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している
credential = {
                "type": "service_account",
                "project_id": os.environ['SHEET_PROJECT_ID'],
                "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
                "private_key": os.environ['SHEET_PRIVATE_KEY'],
                "client_email": os.environ['SHEET_CLIENT_EMAIL'],
                "client_id": os.environ['SHEET_CLIENT_ID'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
             }


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
    tooth_number = req.get("queryResult").get("parameters").get("tooth_number")
    virtical = req.get("queryResult").get("parameters").get("virtical")
    horizontal = req.get("queryResult").get("parameters").get("horizontal")
    depth = req.get("queryResult").get("parameters").get("depth")
    depth_val_1 = req.get("queryResult").get("parameters").get("depth_val_1")
    depth_val_2 = req.get("queryResult").get("parameters").get("depth_val_2")
    depth_val_3 = req.get("queryResult").get("parameters").get("depth_val_3")

    #デバッグ用にログ出力
    print(tooth_number)
    print(virtical)
    print(horizontal)
    print(depth)
    print(depth_val_1)
    print(depth_val_2)
    print(depth_val_3)

    #ダウンロードしたjsonファイルを同じフォルダに格納して指定する
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
    gc = gspread.authorize(credentials)

    # 共有設定したスプレッドシートの名前を指定する
    worksheet = gc.open("JSON_test").sheet1

    print(worksheet.cell(1,1))
    utc_now = datetime.now(timezone('UTC'))
    jst_now = utc_now.astimezone(timezone('Asia/Tokyo'))

    # 3桁または2桁で入力される数値を桁ごとに分解
    # シートに行を追加して記入
    if depth is None:
        worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),tooth_number,"",virtical,depth_val_1[0]]);
        worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),tooth_number,"",virtical,depth_val_2[0]]);
        worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),tooth_number,"",virtical,depth_val_3[0]]);

    if depth is not None:
        worksheet.append_row([jst_now.strftime("%Y/%m/%d %H:%M:%S"),tooth_number[0],horizontal[0],virtical[0],depth[0]]);


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')