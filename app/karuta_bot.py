#-*- coding:utf-8 -*-
from twitter import * # GitHub: https://github.com/sixohsix/twitter
import json
import datetime
import time
import random
import copy
import os
import logger
import sys

#-------------------------------------------------------------
# global変数
#-------------------------------------------------------------
app = None
app_up = None
app_auth = None
conf_file_name = "conf.json"
karuta_info_file_name = "karuta_info.json"
logger = logger.Logger(__file__ + ".log")

def main():
    """ main """

    global app
    global app_up
    global app_auth
    global conf_file_name
    global karuta_info_file_name

    #-------------------------------------------------------------
    # 設定ファイル読み込み
    #-------------------------------------------------------------
    try:
        with open(conf_file_name) as f:
            conf_data = json.loads(f.read())
    except Exception as e:
        logger.write("設定ファイルの読み込みに失敗しました。")
        logger.write(str(e))
        sys.exit(1)

    #-------------------------------------------------------------
    # Twitterアプリ認証
    #-------------------------------------------------------------
    try:
        app_auth = OAuth(
            conf_data["access_token"],
            conf_data["access_token_secret"],
            conf_data["consumer_key"],
            conf_data["consumer_secret"])
        app = Twitter(auth=app_auth)
        app_up = Twitter(domain="upload.twitter.com", auth=app_auth)
    except Exception as e:
        logger.write("Twitterアプリ認証に失敗しました。")
        logger.write(str(e))
        sys.exit(1)

    #-------------------------------------------------------------
    # 百人一首ファイル読み込み
    #-------------------------------------------------------------
    try:
        karuta_info = []
        with open(karuta_info_file_name) as f:
            for line in json.load(f):
                karuta_info.append(line)
    except Exception as e:
        logger.write("百人一首ファイル[{filename}]の読み込みに失敗しました。".format(filename=karuta_info_file_name))
        logger.write(str(e))
        sys.exit(1)

    #-------------------------------------------------------------
    # 初回起動メッセージをつぶやく
    #-------------------------------------------------------------
    #try:
    #    tweet_time = datetime.datetime.now()
    #    tweet_msg = """
    #                karuta_bot.pyが起動したよ!!\n
    #                これから5分毎に百人一首をつぶやくよ!!
    #                """
    #    app.statuses.update(status=tweet_msg)
    #except Exception as e:
    #    logger.write("初回起動メッセージのつぶやきに失敗しました。")
    #    logger.write(str(e))
    #    sys.exit(1)

    #-------------------------------------------------------------
    # つぶやく（とりあえず10分ごとにつぶやく）
    #-------------------------------------------------------------
    tweet_time = datetime.datetime(1900, 1, 1, 0, 0, 0)
    tweet_karuta_list = copy.deepcopy(karuta_info)
    while True:
        now_time = datetime.datetime.now()
        if int((now_time - tweet_time).seconds / 600) >= 1:
            idx = random.randint(0, len(tweet_karuta_list) - 1)
            if karuta_tweet(tweet_karuta_list[idx]):
                tweet_karuta_list.pop(idx)
            if not tweet_karuta_list:
                tweet_karuta_list = copy.deepcopy(karuta_info)
            tweet_time = now_time
        time.sleep(10)

def karuta_tweet(karuta_info):
    """ つぶやく """

    global app
    global app_up

    #-------------------------------------------------------------
    # かるた画像ファイル読み込み
    #-------------------------------------------------------------
    try:
        file_path = os.path.join("./karuta_img/", karuta_info["img"])
        with open(file_path, "rb") as image_f:
            image_data = image_f.read()
    except Exception as e:
        logger.write("画像ファイル[{filename}]の読み込みに失敗しました".format(filename=filepath))
        logger.write(str(e))
        return False

    #-------------------------------------------------------------
    # 原文ツイート作成
    #-------------------------------------------------------------
    tweet_msg = (
        karuta_info["first_part"] + "\n" +
        karuta_info["last_part"] + "\n" +
        karuta_info["name"])

    #-------------------------------------------------------------
    # 原文をつぶやく
    #-------------------------------------------------------------
    try:
        id_img = app_up.media.upload(media=image_data)["media_id_string"]
        app.statuses.update(status=tweet_msg, media_ids=id_img)
    except Exception as e:
        logger.write("画像のTweetに失敗しました。")
        logger.write(str(e))
        return False

    #-------------------------------------------------------------
    # 連続でツイートすることができないため、
    # 一定時間スリープする
    #-------------------------------------------------------------
    time.sleep(300)

    #-------------------------------------------------------------
    # 日本語訳をツイート
    #-------------------------------------------------------------
    tweet_msg = karuta_info["translate"]
    try:
        app.statuses.update(status=tweet_msg)
    except Exception as e:
        logger.write("現代語訳のTweetに失敗しました。")
        logger.write(str(e))
        return False

    return True


if __name__ == "__main__":
    main()
